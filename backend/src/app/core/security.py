import hashlib
import hmac
import secrets
from datetime import datetime, timedelta, timezone
from http import HTTPStatus
from typing import Any

import itsdangerous
from fastapi import HTTPException, Request
from jose import ExpiredSignatureError, JWTError, jwt
from passlib.context import CryptContext
from pydantic import ValidationError
from starlette.responses import Response

from src.app.core.config import Settings
from src.app.schemas.auth import AuthUser, JWTClaims


pwd_context = CryptContext(schemes=["bcrypt"], bcrypt__default_rounds=12, bcrypt__ident="2b")


def hash_password(value: str) -> str:
    return pwd_context.hash(value)


def verify_password(value: str, hashed: str) -> bool:
    return pwd_context.verify(value, hashed)


def generate_pin() -> str:
    return f"{secrets.randbelow(1_000_000):06d}"


def hash_pin(value: str) -> str:
    return hash_password(value)


def verify_pin(value: str, hashed: str) -> bool:
    return verify_password(value, hashed)


def generate_random_password() -> str:
    lower = "".join(secrets.choice("abcdefghijklmnopqrstuvwxyz") for _ in range(4))
    upper = "".join(secrets.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZ") for _ in range(3))
    digits = "".join(secrets.choice("0123456789") for _ in range(3))
    special = secrets.choice("_!@*")
    chars = list(lower + upper + digits + special)
    secrets.SystemRandom().shuffle(chars)
    return "".join(chars)


def expires_at(seconds: int) -> datetime:
    return datetime.now(timezone.utc) + timedelta(seconds=seconds)


def generate_session_id() -> str:
    return secrets.token_urlsafe(32)


def generate_csrf_secret() -> str:
    return secrets.token_urlsafe(24)


class SecurityService:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.CSRF_SERIALIZER = itsdangerous.URLSafeTimedSerializer(settings.csrf_secret)
        self.ACCESS_COOKIE = settings.access_cookie
        self.REFRESH_COOKIE = settings.refresh_cookie
        self.CSRF_COOKIE = settings.csrf_cookie
        self.CSRF_HEADER = settings.csrf_header

    def _create_token(self, payload: dict[str, Any], token_type: str, expires_delta: int) -> str:
        payload = {
            **payload,
            "type": token_type,
            "exp": datetime.now(timezone.utc) + timedelta(seconds=expires_delta),
        }
        return jwt.encode(payload, self.settings.jwt_secret, algorithm="HS256")

    def create_access_token(self, auth_user: AuthUser, session_id: str) -> str:
        return self._create_token(
            {
                "user_id": auth_user.id,
                "sid": session_id,
                "name": auth_user.name,
                "email": auth_user.email,
                "affise_password": auth_user.affise_password,
                "affise_country": auth_user.affise_country,
                "affise_id": auth_user.affise_id,
                "affise_api_key": auth_user.affise_api_key,
                "is_banned": auth_user.is_banned,
                "is_admin": auth_user.is_admin,
                "impersonating": auth_user.impersonating,
            },
            "access",
            self.settings.access_token_expire_seconds,
        )

    def create_refresh_token(self, user_id: int, session_id: str) -> str:
        return self._create_token(
            {"user_id": user_id, "sid": session_id},
            "refresh",
            self.settings.refresh_token_expire_seconds,
        )

    def hash_refresh_token_for_db(self, token: str) -> str:
        return hmac.new(
            self.settings.refresh_token_pepper.encode("utf-8"),
            token.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()

    def decode_token(self, token: str, options: dict[str, Any] | None = None) -> JWTClaims:
        try:
            payload = jwt.decode(token, self.settings.jwt_secret, algorithms=["HS256"], options=options)
            return JWTClaims(**payload)
        except ExpiredSignatureError as exc:
            raise HTTPException(
                status_code=HTTPStatus.UNAUTHORIZED,
                detail={"error": "token expired"},
            ) from exc
        except (JWTError, ValidationError) as exc:
            raise HTTPException(
                status_code=HTTPStatus.FORBIDDEN,
                detail={"error": "token invalid"},
            ) from exc

    def require_auth(self, request: Request) -> JWTClaims:
        access_token = request.cookies.get(self.ACCESS_COOKIE)
        if not access_token:
            raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED, detail="Authentication required")

        claims = self.decode_token(access_token)
        if claims.token_type != "access":
            raise HTTPException(status_code=HTTPStatus.FORBIDDEN, detail={"error": "token invalid"})
        return claims

    def require_csrf(self, request: Request) -> None:
        cookie_token = request.cookies.get(self.CSRF_COOKIE)
        header_token = request.headers.get(self.CSRF_HEADER)
        if not cookie_token or not header_token:
            raise HTTPException(status_code=HTTPStatus.FORBIDDEN, detail="CSRF token required")
        if not secrets.compare_digest(cookie_token, header_token):
            raise HTTPException(status_code=HTTPStatus.FORBIDDEN, detail="CSRF token mismatch")
        try:
            self.CSRF_SERIALIZER.loads(cookie_token, max_age=self.settings.refresh_token_expire_seconds)
        except itsdangerous.BadSignature as exc:
            raise HTTPException(status_code=HTTPStatus.FORBIDDEN, detail="CSRF token invalid") from exc

    def create_csrf_token(self) -> str:
        return self.CSRF_SERIALIZER.dumps({"nonce": secrets.token_urlsafe(16)})

    def set_csrf_cookie(self, response: Response, token: str) -> None:
        response.set_cookie(
            key=self.CSRF_COOKIE,
            value=token,
            httponly=False,
            secure=self.settings.cookie_secure,
            samesite="strict",
            path="/",
            max_age=self.settings.refresh_token_expire_seconds,
        )

    def set_access_token(self, response: Response, auth_user: AuthUser, session_id: str) -> str:
        token = self.create_access_token(auth_user, session_id)
        response.set_cookie(
            key=self.ACCESS_COOKIE,
            value=token,
            httponly=True,
            secure=self.settings.cookie_secure,
            samesite="lax",
            path="/",
            max_age=self.settings.refresh_token_expire_seconds,
        )
        return token

    def set_refresh_cookie(self, response: Response, token: str) -> None:
        response.set_cookie(
            key=self.REFRESH_COOKIE,
            value=token,
            httponly=True,
            secure=self.settings.cookie_secure,
            samesite="lax",
            path=self.settings.refresh_cookie_path,
            max_age=self.settings.refresh_token_expire_seconds,
        )

    def clear_auth_cookies(self, response: Response) -> None:
        response.delete_cookie(self.ACCESS_COOKIE, path="/", samesite="lax", secure=self.settings.cookie_secure)
        response.delete_cookie(
            self.REFRESH_COOKIE,
            path=self.settings.refresh_cookie_path,
            samesite="lax",
            secure=self.settings.cookie_secure,
        )
        response.delete_cookie(self.CSRF_COOKIE, path="/", samesite="strict", secure=self.settings.cookie_secure)
