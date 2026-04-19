from __future__ import annotations

from fastapi import Depends, HTTPException, Request, Response, status

from di_container import api_uow, container
from src.app.core.auth_sessions import get_live_session
from src.app.core.config import Settings, get_settings
from src.app.schemas.auth import AuthUser, JWTClaims
from src.infrastructure.models.session import AppSession
from src.modules.shared.unit_of_work import UnitOfWork


async def get_settings_dep() -> Settings:
    return get_settings()


async def get_current_claims(request: Request) -> JWTClaims | None:
    sec = container.security_service()
    access_token = request.cookies.get(sec.ACCESS_COOKIE)
    if not access_token:
        return None

    claims = sec.decode_token(access_token)
    if claims.token_type != "access":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Authentication failed")
    return claims


async def get_current_session(
    request: Request,
    response: Response,
    uow: UnitOfWork = Depends(api_uow),
    claims: JWTClaims | None = Depends(get_current_claims),
) -> AppSession | None:
    if not claims:
        return None
    return await get_live_session(uow, response, container.security_service(), claims.session_id, claims.user_id)


async def get_current_user(claims: JWTClaims | None = Depends(get_current_claims)) -> AuthUser | None:
    return claims.to_auth_user() if claims else None


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


def is_admin_email(email: str, settings: Settings) -> bool:
    allowed = {str(item.get("email", "")).lower() for item in settings.admins_list}
    return email.lower() in allowed


async def require_admin(
    user: AuthUser = Depends(require_user),
    settings: Settings = Depends(get_settings_dep),
) -> AuthUser:
    if not user.is_admin or not is_admin_email(user.email, settings):
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
    sec = container.security_service()
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


async def maybe_user_context(
    request: Request,
    user: AuthUser | None = Depends(get_current_user),
    settings: Settings = Depends(get_settings_dep),
) -> dict:
    sec = container.security_service()
    return {
        "user": user,
        "is_admin": bool(user and user.is_admin and is_admin_email(user.email, settings)),
        "impersonating": bool(user and user.impersonating),
        "csrf_token": request.cookies.get(sec.CSRF_COOKIE),
    }
