from __future__ import annotations

from datetime import datetime, timedelta, timezone

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, HTTPException, Request, Response, status

from cfg import DEV, REFRESH_TOKEN_EXPIRE_SECONDS
from di_container import Container as c
from src.app.core.dependencies import uow
from src.app.core.rate_limit import rate_limiter
from src.app.schemas.auth import PinSendRequest, PinVerifyRequest
from src.app.services.auth_session import AuthSessionService
from src.app.services.mail import MailService
from src.app.services.security import SecurityService
from src.infrastructure.models.pin_code import PinCode
from src.infrastructure.models.user import User
from src.modules.shared.unit_of_work import UnitOfWork

router = APIRouter(prefix="/auth", tags=["auth"])


PIN_TTL_MINUTES = 15
MAX_ATTEMPTS = 5
EMAIL_SENDS_PER_WINDOW = 3
EMAIL_WINDOW_MINUTES = 15


def _redirect_path(admin_only: bool) -> str:
    return "/admin" if admin_only else "/dashboard"


async def _get_user_by_email(uow: UnitOfWork, email: str) -> User | None:
    return await uow.users.get_by_email(email)


async def _get_or_create_user(uow: UnitOfWork, email: str, sec: SecurityService) -> User:
    existing_user = await _get_user_by_email(uow, email)
    if existing_user:
        return existing_user

    return await uow.users.get_or_create(
        email=email,
        name=email,
        password_hash=sec.hash_password(sec.generate_random_password()),
    )


async def _send_pin(
    payload: PinSendRequest,
    request: Request,
    uow: UnitOfWork,
    response: Response,
    mailer: MailService,
    sec: SecurityService,
    auth_session: AuthSessionService,
    admin_only: bool,
) -> dict:
    email = payload.email.lower()
    user = await _get_user_by_email(uow, email)
    if admin_only and (not user or not user.is_admin):
        return {"success": True}

    if user and user.is_banned and not admin_only:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Ваш аккаунт заблокирован.")

    allowed, retry_after = await rate_limiter.hit(
        f"{'admin-' if admin_only else ''}send-pin:{email}",
        EMAIL_SENDS_PER_WINDOW,
        EMAIL_WINDOW_MINUTES * 60,
    )
    if not allowed:
        response.headers["Retry-After"] = str(retry_after)
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Слишком много попыток. Повторите через {retry_after} с.",
    )

    if admin_only and DEV:
        user = await _get_or_create_user(uow, email, sec)
        await auth_session.create_auth_session(uow, response, request, user)
        return {"redirect": _redirect_path(admin_only=True)}

    await uow.pin_codes.delete_by_email(email)
    pin = sec.generate_pin()
    await uow.pin_codes.add(
        PinCode(
            email=email,
            code_hash=sec.hash_pin(pin),
            ip_address=request.client.host if request.client else None,
            attempts=0,
            expires_at=datetime.now(timezone.utc) + timedelta(minutes=PIN_TTL_MINUTES),
        )
    )
    await uow.commit()

    if DEV:
        return {"success": True, "debug_pin": pin}

    await mailer.send_pin(email, pin)
    return {"success": True}


async def _verify_pin(
    payload: PinVerifyRequest,
    request: Request,
    response: Response,
    uow: UnitOfWork,
    sec: SecurityService,
    auth_session: AuthSessionService,
    admin_only: bool,
) -> dict:
    email = payload.email.lower()
    pin = payload.pin

    user = await _get_user_by_email(uow, email)
    if admin_only and (not user or not user.is_admin):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Доступ запрещён.")

    if user and user.is_banned and not admin_only:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Ваш аккаунт заблокирован.")

    if not DEV or admin_only:
        record = await uow.pin_codes.get_latest_active(email, datetime.now(timezone.utc), MAX_ATTEMPTS)

        if not record:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Код не найден или истёк. Запросите новый.",
            )

        record.attempts += 1
        await uow.flush()

        if not sec.verify_pin(pin, record.code_hash):
            attempts_left = MAX_ATTEMPTS - record.attempts
            if attempts_left <= 0:
                await uow.pin_codes.delete(record)
                await uow.commit()
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail="Неверный код. Лимит попыток исчерпан, запросите новый код.",
                )

            await uow.commit()
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Неверный код. Осталось попыток: {attempts_left}.",
            )

        await uow.pin_codes.delete(record)

    user = await _get_or_create_user(uow, email, sec)

    await auth_session.create_auth_session(uow, response, request, user)
    return {"redirect": _redirect_path(admin_only)}


@router.get("/csrf")
@inject
async def csrf(
    response: Response,
    sec: SecurityService = Depends(Provide[c.security_service]),
) -> dict:
    token = sec.create_csrf_token()
    sec.set_csrf_cookie(response, token)
    return {"csrf_token": token}


@router.post("/client/send-pin")
@inject
async def client_send_pin(
    payload: PinSendRequest,
    request: Request,
    response: Response,
    uow: UnitOfWork = Depends(uow),
    mailer: MailService = Depends(Provide[c.mail_service]),
    sec: SecurityService = Depends(Provide[c.security_service]),
    auth_session: AuthSessionService = Depends(Provide[c.auth_session_service]),
) -> dict:
    return await _send_pin(payload, request, uow, response, mailer, sec, auth_session, admin_only=False)


@router.post("/client/verify-pin")
@inject
async def client_verify_pin(
    payload: PinVerifyRequest,
    request: Request,
    response: Response,
    uow: UnitOfWork = Depends(uow),
    sec: SecurityService = Depends(Provide[c.security_service]),
    auth_session: AuthSessionService = Depends(Provide[c.auth_session_service]),
) -> dict:
    return await _verify_pin(payload, request, response, uow, sec, auth_session, admin_only=False)


@router.post("/admin/login/send-pin")
@inject
async def admin_send_pin(
    payload: PinSendRequest,
    request: Request,
    response: Response,
    uow: UnitOfWork = Depends(uow),
    mailer: MailService = Depends(Provide[c.mail_service]),
    sec: SecurityService = Depends(Provide[c.security_service]),
    auth_session: AuthSessionService = Depends(Provide[c.auth_session_service]),
) -> dict:
    return await _send_pin(payload, request, uow, response, mailer, sec, auth_session, admin_only=True)


@router.post("/admin/login/verify-pin")
@inject
async def admin_verify_pin(
    payload: PinVerifyRequest,
    request: Request,
    response: Response,
    uow: UnitOfWork = Depends(uow),
    sec: SecurityService = Depends(Provide[c.security_service]),
    auth_session: AuthSessionService = Depends(Provide[c.auth_session_service]),
) -> dict:
    return await _verify_pin(payload, request, response, uow, sec, auth_session, admin_only=True)


@router.post("/refresh")
@inject
async def refresh(
    request: Request,
    response: Response,
    uow: UnitOfWork = Depends(uow),
    sec: SecurityService = Depends(Provide[c.security_service]),
    auth_session: AuthSessionService = Depends(Provide[c.auth_session_service]),
) -> dict:
    access_token = request.cookies.get(sec.ACCESS_COOKIE)
    refresh_token = request.cookies.get(sec.REFRESH_COOKIE)
    if not access_token or not refresh_token:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail={"error": "not auth"})

    access_claims = sec.decode_token(access_token, options={"verify_exp": False})
    refresh_claims = sec.decode_token(refresh_token)

    if (
        access_claims.user_id != refresh_claims.user_id
        or access_claims.session_id != refresh_claims.session_id
    ):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail={"error": "not auth"})

    session = await auth_session.get_session_by_refresh_cookie(uow, request, verify_exp=True)
    if not session:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail={"error": "not auth"})

    await auth_session.rotate_session_credentials(uow, response, session, session.user, REFRESH_TOKEN_EXPIRE_SECONDS)
    await uow.commit()
    return {}


@router.post("/client/logout")
@inject
async def client_logout(
    request: Request,
    response: Response,
    uow: UnitOfWork = Depends(uow),
    sec: SecurityService = Depends(Provide[c.security_service]),
    auth_session: AuthSessionService = Depends(Provide[c.auth_session_service]),
) -> dict:
    await auth_session.revoke_session_by_refresh_cookie(uow, request)
    sec.clear_auth_cookies(response)
    return {"redirect": "/client"}


@router.post("/admin/logout")
@inject
async def admin_logout(
    request: Request,
    response: Response,
    uow: UnitOfWork = Depends(uow),
    sec: SecurityService = Depends(Provide[c.security_service]),
    auth_session: AuthSessionService = Depends(Provide[c.auth_session_service]),
) -> dict:
    await auth_session.revoke_session_by_refresh_cookie(uow, request)
    sec.clear_auth_cookies(response)
    return {"redirect": "/admin"}
