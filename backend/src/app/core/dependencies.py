from __future__ import annotations

from dependency_injector.wiring import Provide, inject
from fastapi import Depends, HTTPException, Request, Response, status

from di_container import api_uow, Container as c
from src.app.schemas.auth import AuthUser, JWTClaims
from src.app.services.auth_session import AuthSessionService
from src.app.services.security import SecurityService
from src.infrastructure.models.session import AppSession
from src.modules.shared.unit_of_work import UnitOfWork


@inject
async def get_current_claims(
    request: Request,
    sec: SecurityService = Depends(Provide[c.security_service]),
) -> JWTClaims | None:
    access_token = request.cookies.get(sec.ACCESS_COOKIE)
    if not access_token:
        return None

    claims = sec.decode_token(access_token)
    return claims


@inject
async def get_current_session(
    request: Request,
    response: Response,
    uow: UnitOfWork = Depends(api_uow),
    claims: JWTClaims | None = Depends(get_current_claims),
    auth_session: AuthSessionService = Depends(Provide[c.auth_session_service]),
) -> AppSession | None:
    if not claims:
        return None
    return await auth_session.get_live_session(uow, response, claims.session_id, claims.user_id)


async def get_current_user(claims: JWTClaims | None = Depends(get_current_claims)) -> AuthUser | None:
    return claims.to_auth_user() if claims else None


@inject
def require_auth(
    request: Request,
    sec: SecurityService = Depends(Provide[c.security_service]),
):
    return sec.require_auth(request)


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


async def require_admin(
    user: AuthUser = Depends(require_not_banned)
) -> AuthUser:
    if not user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    return user


async def require_onboarded(user: AuthUser = Depends(require_not_banned)) -> AuthUser:
    if not user.affise_password:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Onboarding required",
        )
    return user


@inject
async def require_csrf(
    request: Request,
    sec: SecurityService = Depends(Provide[c.security_service]),
) -> None:
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
    sec: SecurityService = Depends(Provide[c.security_service]),

) -> dict:
    return {
        "user": user,
        "is_admin": bool(user and user.is_admin),
        "impersonating": bool(user and user.impersonating),
        "csrf_token": request.cookies.get(sec.CSRF_COOKIE),
    }
