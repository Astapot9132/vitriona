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

from cfg import CSRF_SECRET, JWT_SECRET, ACCESS_TOKEN_EXPIRE_SECONDS, REFRESH_TOKEN_EXPIRE_SECONDS, \
    REFRESH_TOKEN_PEPPER, DEV, REFRESH_COOKIE_PATH
from src.app.schemas.auth import AuthUser, JWTClaims


class SecurityService:
    ACCESS_COOKIE = "access_token"
    REFRESH_COOKIE = "refresh_token"
    CSRF_COOKIE = "csrf_token"
    CSRF_HEADER = "csrf_header"


    PWD_CONTEXT = CryptContext(schemes=['bcrypt'],
                               bcrypt__default_rounds=12,
                               bcrypt__ident='2b'
                               )

    def __init__(self):
        self.CSRF_SERIALIZER = itsdangerous.URLSafeTimedSerializer(CSRF_SECRET)

    def _create_token(self, payload: dict[str, Any], expires_delta: int) -> str:
        payload = {
            **payload,
            "exp": datetime.now(timezone.utc) + timedelta(seconds=expires_delta),
        }
        return jwt.encode(payload, JWT_SECRET, algorithm="HS256")

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
            ACCESS_TOKEN_EXPIRE_SECONDS,
        )

    def create_refresh_token(self, user_id: int, session_id: str) -> str:
        return self._create_token(
            {"user_id": user_id, "sid": session_id},
            REFRESH_TOKEN_EXPIRE_SECONDS,
        )

    @classmethod
    def hash_refresh_token_for_db(cls, token: str) -> str:
        return hmac.new(
            REFRESH_TOKEN_PEPPER.encode("utf-8"),
            token.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()

    @classmethod
    def decode_token(cls, token: str, options: dict[str, Any] | None = None) -> JWTClaims:
        try:
            payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"], options=options)
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
            secure=not DEV,
            samesite="strict",
            path="/",
            max_age=REFRESH_TOKEN_EXPIRE_SECONDS,
        )

    def set_access_token(self, response: Response, auth_user: AuthUser, session_id: str) -> str:
        token = self.create_access_token(auth_user, session_id)
        response.set_cookie(
            key=self.ACCESS_COOKIE,
            value=token,
            httponly=True,
            secure=not DEV,
            samesite="lax",
            path="/",
            max_age=REFRESH_TOKEN_EXPIRE_SECONDS,
        )
        return token

    def set_refresh_cookie(self, response: Response, token: str) -> None:
        response.set_cookie(
            key=self.REFRESH_COOKIE,
            value=token,
            httponly=True,
            secure=not DEV,
            samesite="lax",
            path=REFRESH_COOKIE_PATH,
            max_age=REFRESH_TOKEN_EXPIRE_SECONDS,
        )

    def clear_auth_cookies(self, response: Response) -> None:
        response.delete_cookie(self.ACCESS_COOKIE, path="/", samesite="lax", secure=not DEV)
        response.delete_cookie(
            self.REFRESH_COOKIE,
            path=REFRESH_COOKIE_PATH,
            samesite="lax",
            secure=not DEV,
        )
        response.delete_cookie(self.CSRF_COOKIE, path="/", samesite="strict", secure=not DEV)


    @classmethod
    def hash_password(cls, value: str) -> str:
        return cls.PWD_CONTEXT.hash(value)

    @classmethod
    def verify_password(cls, value: str, hashed: str) -> bool:
        return cls.PWD_CONTEXT.verify(value, hashed)

    @classmethod
    def generate_pin(cls) -> str:
        return f"{secrets.randbelow(1_000_000):06d}"

    @classmethod
    def hash_pin(cls, value: str) -> str:
        return cls.hash_password(value)

    @classmethod
    def verify_pin(cls, value: str, hashed: str) -> bool:
        return cls.verify_password(value, hashed)

    @classmethod
    def generate_random_password(cls) -> str:
        lower = "".join(secrets.choice("abcdefghijklmnopqrstuvwxyz") for _ in range(4))
        upper = "".join(secrets.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZ") for _ in range(3))
        digits = "".join(secrets.choice("0123456789") for _ in range(3))
        special = secrets.choice("_!@*")
        chars = list(lower + upper + digits + special)
        secrets.SystemRandom().shuffle(chars)
        return "".join(chars)

    @classmethod
    def expires_at(cls, seconds: int) -> datetime:
        return datetime.now(timezone.utc) + timedelta(seconds=seconds)

    @classmethod
    def generate_session_id(cls) -> str:
        return secrets.token_urlsafe(32)

    @classmethod
    def generate_csrf_secret(cls) -> str:
        return secrets.token_urlsafe(24)
