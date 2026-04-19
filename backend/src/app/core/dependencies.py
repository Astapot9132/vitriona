from __future__ import annotations

from dependency_injector.wiring import Provide, inject
from fastapi import Depends, HTTPException, Request, Response, status

from cfg import ADMINS_LIST
from di_container import api_uow, container as c
from src.app.core.auth_sessions import get_live_session
from src.app.core.security import SecurityService
from src.app.schemas.auth import AuthUser, JWTClaims
from src.infrastructure.models.session import AppSession
from src.modules.shared.unit_of_work import UnitOfWork


async def get_current_claims(request: Request) -> JWTClaims | None:
    sec = c.security_service()
    access_token = request.cookies.get(sec.ACCESS_COOKIE)
    if not access_token:
        return None

    claims = sec.decode_token(access_token)
    return claims


async def get_current_session(
    request: Request,
    response: Response,
    uow: UnitOfWork = Depends(api_uow),
    claims: JWTClaims | None = Depends(get_current_claims),
) -> AppSession | None:
    if not claims:
        return None
    return await get_live_session(uow, response, claims.session_id, claims.user_id)


async def get_current_user(claims: JWTClaims | None = Depends(get_current_claims)) -> AuthUser | None:
    return claims.to_auth_user() if claims else None


def require_auth(request: Request):
    return c.security_service().require_auth(request)


async def require_user(user: AuthUser | None = Depends(get_current_user)) -> AuthUser:
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required")
    return user


async def require_claims(claims: JWTClaims | None = Depends(get_current_claims)) -> JWTClaims:
    if not claims:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required")
    return claims


async def require_not_banned(user: AuthUser = Depends(require_user)) -> AuthUser:
    if user.is_banned:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Ваш аккаунт заблокирован.")
    return user


def is_admin_email(email: str) -> bool:
    allowed = {str(item.get("email", "")).lower() for item in ADMINS_LIST}
    return email.lower() in allowed


async def require_admin(
    user: AuthUser = Depends(require_user)
) -> AuthUser:
    if not user.is_admin or not is_admin_email(user.email):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    return user


async def require_onboarded(user: AuthUser = Depends(require_not_banned)) -> AuthUser:
    if not user.affise_password:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Onboarding required",
        )
    return user


async def require_csrf(request: Request) -> None:
    sec = c.security_service()
    sec.require_csrf(request)


async def require_user_and_csrf(
    _: None = Depends(require_csrf),
    user: AuthUser = Depends(require_not_banned),
) -> AuthUser:
    return user


async def require_admin_and_csrf(
    _: None = Depends(require_csrf),
    user: AuthUser = Depends(require_admin),
) -> AuthUser:
    return user


async def require_onboarded_and_csrf(
    _: None = Depends(require_csrf),
    user: AuthUser = Depends(require_onboarded),
) -> AuthUser:
    return user


async def get_impersonating_flag(session: AppSession | None = Depends(get_current_session)) -> bool:
    return bool(session and session.impersonator_admin_id)


@inject
async def maybe_user_context(
    request: Request,
    user: AuthUser | None = Depends(get_current_user),
    sec: SecurityService = Depends(Provide[SecurityService]),

) -> dict:
    return {
        "user": user,
        "is_admin": bool(user and user.is_admin and is_admin_email(user.email)),
        "impersonating": bool(user and user.impersonating),
        "csrf_token": request.cookies.get(sec.CSRF_COOKIE),
    }
