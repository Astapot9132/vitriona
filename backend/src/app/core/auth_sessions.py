from __future__ import annotations

from datetime import datetime

import pytz
from dependency_injector.wiring import Provide
from fastapi import HTTPException, Request, Response, Depends

from cfg import REFRESH_TOKEN_EXPIRE_SECONDS
from src.app.core.dependencies import is_admin_email
from src.app.core.security import SecurityService
from src.app.schemas.auth import AuthUser
from src.infrastructure.models.session import AppSession
from src.infrastructure.models.user import User
from src.modules.shared.unit_of_work import UnitOfWork
from di_container import api_uow, container as c



def build_auth_user(user: User, session: AppSession) -> AuthUser:
    return AuthUser(
        id=user.id,
        name=user.name,
        email=user.email,
        affise_password=user.affise_password,
        affise_country=user.affise_country,
        affise_id=user.affise_id,
        affise_api_key=user.affise_api_key,
        is_banned=user.is_banned,
        is_admin=is_admin_email(user.email),
        impersonating=bool(session.impersonator_admin_id),
    )


def _issue_session_cookies(response: Response, session: AppSession, auth_user: AuthUser, sec: SecurityService) -> None:
    sec.set_access_token(response, auth_user, session.id)
    refresh_token = sec.create_refresh_token(session.user_id, session.id)
    session.refresh_token_hash = sec.hash_refresh_token_for_db(refresh_token)
    sec.set_refresh_cookie(response, refresh_token)
    sec.set_csrf_cookie(response, sec.create_csrf_token())


async def get_session_by_refresh_cookie(
    uow: UnitOfWork,
    request: Request,
    sec: SecurityService,
    *,
    verify_exp: bool,
) -> AppSession | None:
    refresh_token = request.cookies.get(sec.REFRESH_COOKIE)
    if not refresh_token:
        return None

    options = {"verify_exp": verify_exp}
    try:
        claims = sec.decode_token(refresh_token, options=options)
    except HTTPException:
        return None

    if claims.token_type != "refresh":
        return None

    session = await uow.sessions.get_valid_by_refresh_claims(
        claims.session_id,
        claims.user_id,
        sec.hash_refresh_token_for_db(refresh_token),
        utcnow(),
    )
    if not session:
        return None

    return session


async def create_auth_session(
    uow: UnitOfWork,
    response: Response,
    request: Request,
    user: User,
    sec: SecurityService,
    impersonator_admin_id: int | None = None,

) -> AppSession:
    session = AppSession(
        id=sec.generate_session_id(),
        user_id=user.id,
        csrf_token=sec.generate_csrf_secret(),
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
        expires_at=sec.expires_at(REFRESH_TOKEN_EXPIRE_SECONDS),
        impersonator_admin_id=impersonator_admin_id,
    )
    await uow.sessions.add(session)
    await uow.flush()

    auth_user = build_auth_user(user, session, settings)
    _issue_session_cookies(response, session, auth_user, sec)

    await uow.commit()
    await uow.refresh(session)
    return session


def rotate_session_credentials(
    response: Response,
    session: AppSession,
    user: User,
    sec: SecurityService,
    settings: Settings,
    ttl_seconds: int,
) -> None:
    session.expires_at = expires_at(ttl_seconds)
    auth_user = build_auth_user(user, session, settings)
    _issue_session_cookies(response, session, auth_user, sec)


async def revoke_session_by_refresh_cookie(
    uow: UnitOfWork,
    request: Request,
    sec: SecurityService,
) -> AppSession | None:
    session = await get_session_by_refresh_cookie(uow, request, sec, verify_exp=False)
    if not session:
        return None

    await uow.sessions.delete(session)
    await uow.commit()
    return session


async def get_live_session(
    uow: UnitOfWork,
    response: Response,
    session_id: str,
    user_id: int,
    sec: SecurityService = Depends(Provide[c.security_service]),
) -> AppSession | None:
    session = await uow.sessions.get_by_id_with_user(session_id)
    if not session:
        return None

    if session.user_id != user_id:
        sec.clear_auth_cookies(response)
        return None

    if session.expires_at <= datetime.now(pytz.UTC):
        await uow.sessions.delete(session)
        await uow.commit()
        sec.clear_auth_cookies(response)
        return None

    return session
