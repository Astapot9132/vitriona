from __future__ import annotations

from datetime import datetime, timezone

from fastapi import HTTPException, Request, Response

from cfg import REFRESH_TOKEN_EXPIRE_SECONDS
from src.app.schemas.auth import AuthUser
from src.app.services.security import SecurityService
from src.infrastructure.models.session import AppSession
from src.infrastructure.models.user import User
from src.modules.shared.unit_of_work import UnitOfWork


class AuthSessionService:
    def __init__(self, sec: SecurityService):
        self.sec = sec

    def build_auth_user(self, user: User, session: AppSession) -> AuthUser:
        return AuthUser(
            id=user.id,
            name=user.name,
            email=user.email,
            affise_password=user.affise_password,
            affise_country=user.affise_country,
            affise_id=user.affise_id,
            affise_api_key=user.affise_api_key,
            is_banned=user.is_banned,
            is_admin=user.is_admin,
            impersonating=bool(session.impersonator_admin_id),
        )

    async def _issue_session_cookies(
        self,
        uow: UnitOfWork,
        response: Response,
        session: AppSession,
        auth_user: AuthUser,
        *,
        expires_at: datetime | None = None,
    ) -> None:
        self.sec.set_access_token(response, auth_user, session.id)
        refresh_token = self.sec.create_refresh_token(session.user_id, session.id)
        self.sec.set_refresh_cookie(response, refresh_token)
        self.sec.set_csrf_cookie(response, self.sec.create_csrf_token())
        refresh_token_hash = self.sec.hash_refresh_token_for_db(refresh_token)
        if expires_at is None:
            await uow.sessions.set_refresh_token_hash(session.id, refresh_token_hash=refresh_token_hash)
            return
        await uow.sessions.rotate_session(
            session.id,
            refresh_token_hash=refresh_token_hash,
            expires_at=expires_at,
        )

    async def get_session_by_refresh_cookie(
        self,
        uow: UnitOfWork,
        request: Request,
        *,
        verify_exp: bool,
    ) -> AppSession | None:
        refresh_token = request.cookies.get(self.sec.REFRESH_COOKIE)
        if not refresh_token:
            return None

        options = {"verify_exp": verify_exp}
        try:
            claims = self.sec.decode_token(refresh_token, options=options)
        except HTTPException:
            if not verify_exp:
                return None
            try:
                claims = self.sec.decode_token(refresh_token, options={"verify_exp": False})
            except HTTPException:
                return None
            session = await uow.sessions.get_by_refresh_claims(
                claims.session_id,
                claims.user_id,
                self.sec.hash_refresh_token_for_db(refresh_token),
            )
            if session and not session.is_closed and session.expires_at <= datetime.now(timezone.utc):
                await uow.sessions.close_session(session.id, reason="expired")
                await uow.commit()
            return None

        session = await uow.sessions.get_by_refresh_claims(
            claims.session_id,
            claims.user_id,
            self.sec.hash_refresh_token_for_db(refresh_token),
        )
        if not session:
            return None
        if session.is_closed:
            return None
        if session.expires_at <= datetime.now(timezone.utc):
            await uow.sessions.close_session(session.id, reason="expired")
            await uow.commit()
            return None

        return session

    async def create_auth_session(
        self,
        uow: UnitOfWork,
        response: Response,
        request: Request,
        user: User,
        impersonator_admin_id: int | None = None,
    ) -> AppSession:
        now = datetime.now(timezone.utc)
        session = AppSession(
            id=self.sec.generate_session_id(),
            user_id=user.id,
            ip_address=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent"),
            is_closed=False,
            closed_at=None,
            close_reason=None,
            last_seen_at=now,
            expires_at=self.sec.expires_at(REFRESH_TOKEN_EXPIRE_SECONDS),
            impersonator_admin_id=impersonator_admin_id,
        )
        await uow.sessions.add(session)
        await uow.flush()

        auth_user = self.build_auth_user(user, session)
        await self._issue_session_cookies(uow, response, session, auth_user)

        await uow.commit()
        await uow.refresh(session)
        return session

    async def rotate_session_credentials(
        self,
        uow: UnitOfWork,
        response: Response,
        session: AppSession,
        user: User,
        ttl_seconds: int,
    ) -> None:
        expires_at = self.sec.expires_at(ttl_seconds)
        auth_user = self.build_auth_user(user, session)
        await self._issue_session_cookies(
            uow,
            response,
            session,
            auth_user,
            expires_at=expires_at,
        )

    async def revoke_session_by_refresh_cookie(
        self,
        uow: UnitOfWork,
        request: Request,
    ) -> AppSession | None:
        session = await self.get_session_by_refresh_cookie(uow, request, verify_exp=False)
        if not session:
            return None

        await uow.sessions.close_session(session.id, reason="logout")
        await uow.commit()
        return session

    async def get_live_session(
        self,
        uow: UnitOfWork,
        response: Response,
        session_id: str,
        user_id: int,
    ) -> AppSession | None:
        session = await uow.sessions.get_by_id_with_user(session_id)
        if not session:
            return None

        if session.user_id != user_id:
            self.sec.clear_auth_cookies(response)
            return None
        if session.is_closed:
            self.sec.clear_auth_cookies(response)
            return None

        if session.expires_at <= datetime.now(timezone.utc):
            await uow.sessions.close_session(session.id, reason="expired")
            await uow.commit()
            self.sec.clear_auth_cookies(response)
            return None

        return session
