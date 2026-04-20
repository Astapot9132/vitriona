from __future__ import annotations

from datetime import datetime, timezone

from dependency_injector.wiring import Provide, inject
from sqlalchemy import desc, func, or_, select, text
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.orm import selectinload
from fastapi import APIRouter, Depends, HTTPException, Query, Request, Response, status

from di_container import Container as c, api_uow
from src.app.core.dependencies import (
    get_current_session,
    require_admin,
)
from src.app.schemas.auth import AuthUser
from src.app.services.affise import AffiseService
from src.app.services.auth_session import AuthSessionService
from src.app.services.security import SecurityService
from src.infrastructure.models.offer import Offer
from src.infrastructure.models.offer_source import OfferSource
from src.infrastructure.models.session import AppSession
from src.infrastructure.models.showcase import Showcase
from src.infrastructure.models.user import User
from src.modules.shared.unit_of_work import UnitOfWork

router = APIRouter(prefix="/admin", tags=["admin"])


def _serialize_offer(offer: Offer) -> dict:
    return {
        "id": offer.id,
        "source_id": offer.source_id,
        "external_id": offer.external_id,
        "title": offer.title,
        "status": offer.status,
        "privacy": offer.privacy,
        "url": offer.url,
        "preview_url": offer.preview_url,
        "logo": offer.logo,
        "description_lang": offer.description_lang,
        "categories": offer.categories,
        "countries": offer.countries,
        "payments": offer.payments,
        "targeting": offer.targeting,
        "tags": offer.tags,
        "cr": offer.cr,
        "epc": offer.epc,
        "hold_period": offer.hold_period,
        "raw_data": offer.raw_data,
        "synced_at": offer.synced_at,
        "created_at": offer.created_at,
        "updated_at": offer.updated_at,
        "source": {
            "id": offer.source.id,
            "name": offer.source.name,
            "type": offer.source.type,
        } if offer.source else None,
    }


@router.get("")
async def admin_root(user: AuthUser = Depends(require_admin)) -> dict:
    return {"user": {"name": user.name, "email": user.email}}


@router.get("/admins")
async def admin_list(
    user: AuthUser = Depends(require_admin),
    uow: UnitOfWork = Depends(api_uow),
) -> dict:
    admins = (await uow.session.execute(select(User).where(User.is_admin.is_(True)).order_by(User.id.asc()))).scalars().all()
    return {
        "admins": [
            {
                "id": item.id,
                "name": item.name,
                "email": item.email,
            }
            for item in admins
        ]
    }


@router.get("/offers")
async def admin_offers(
    user: AuthUser = Depends(require_admin),
    uow: UnitOfWork = Depends(api_uow),
    search: str | None = Query(default=None),
    category: str | None = Query(default=None),
    status_value: str | None = Query(default=None, alias="status"),
    country: str | None = Query(default=None),
    sort: str = Query(default="id"),
    dir: str = Query(default="desc"),
    page: int = Query(default=1, ge=1),
) -> dict:
    db = uow.session
    page_size = 50
    sortable = {"id": Offer.id, "external_id": Offer.external_id, "title": Offer.title, "status": Offer.status, "cr": Offer.cr, "epc": Offer.epc, "synced_at": Offer.synced_at}
    stmt = select(Offer).join(OfferSource, Offer.source_id == OfferSource.id).options(selectinload(Offer.source))
    if search:
        stmt = stmt.where(or_(Offer.title.ilike(f"%{search}%"), Offer.external_id.ilike(f"%{search}%")))
    if category:
        stmt = stmt.where(text("EXISTS (SELECT 1 FROM jsonb_array_elements(COALESCE(offers.categories, '[]'::jsonb)) elem WHERE COALESCE(elem->>'title', trim(both '\"' from elem::text)) = :category)")).params(category=category)
    if status_value:
        stmt = stmt.where(Offer.status == status_value)
    if country:
        stmt = stmt.where(text("EXISTS (SELECT 1 FROM jsonb_array_elements_text(COALESCE(offers.countries, '[]'::jsonb)) elem WHERE elem = :country)")).params(country=country)

    total = await db.scalar(select(func.count()).select_from(stmt.subquery()))
    sort_column = sortable.get(sort, Offer.id)
    stmt = stmt.order_by(sort_column.asc() if dir == "asc" else sort_column.desc())
    stmt = stmt.offset((page - 1) * page_size).limit(page_size)
    offers = (await db.execute(stmt)).scalars().all()

    categories_query = text(
        """
        SELECT DISTINCT COALESCE(elem->>'title', trim(both '"' from elem::text)) AS value
        FROM offers
        CROSS JOIN LATERAL jsonb_array_elements(COALESCE(offers.categories, '[]'::jsonb)) AS elem
        WHERE COALESCE(elem->>'title', trim(both '"' from elem::text)) <> ''
        ORDER BY value
        """
    )
    countries_query = text(
        """
        SELECT DISTINCT elem AS value
        FROM offers
        CROSS JOIN LATERAL jsonb_array_elements_text(COALESCE(offers.countries, '[]'::jsonb)) AS elem
        WHERE elem <> ''
        ORDER BY value
        """
    )

    categories = [row.value for row in (await db.execute(categories_query))]
    countries = [row.value for row in (await db.execute(countries_query))]

    return {
        "offers": {
            "data": [_serialize_offer(offer) for offer in offers],
            "meta": {
                "total": total or 0,
                "page": page,
                "per_page": page_size,
                "last_page": ((total or 0) + page_size - 1) // page_size,
            },
        },
        "filters": {
            "search": search or "",
            "category": category or "",
            "status": status_value or "",
            "country": country or "",
            "sort": sort,
            "dir": dir,
        },
        "categories": categories,
        "countries": countries,
    }


@router.get("/offers/{offer_id}")
async def admin_offer_show(
    offer_id: int,
    user: AuthUser = Depends(require_admin),
    uow: UnitOfWork = Depends(api_uow),
) -> dict:
    db = uow.session
    offer = (
        await db.execute(select(Offer).where(Offer.id == offer_id).options(selectinload(Offer.source)))
    ).scalar_one_or_none()
    if not offer:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")
    return _serialize_offer(offer)


@router.post("/offers/sync")
@inject
async def admin_offers_sync(
    user: AuthUser = Depends(require_admin),
    uow: UnitOfWork = Depends(api_uow),
    affise: AffiseService = Depends(Provide[c.affise_service]),
) -> dict:
    db = uow.session
    sources = (await db.execute(select(OfferSource).where(OfferSource.enabled.is_(True)))).scalars().all()
    if not sources:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Нет активных источников для синхронизации.")

    total = 0
    names: list[str] = []
    now = datetime.now(timezone.utc)

    try:
        for source in sources:
            if source.type != "affise":
                continue
            page = 1
            names.append(source.name)
            while True:
                response = await affise.get_offers(page=page, limit=500)
                if (response.get("status") != 1) or not response.get("offers"):
                    break

                batch = []
                for raw_offer in response["offers"]:
                    batch.append(
                        {
                            "source_id": source.id,
                            "external_id": str(raw_offer.get("offer_id") or raw_offer.get("id")),
                            "title": raw_offer.get("title") or "",
                            "status": raw_offer.get("status") or "active",
                            "privacy": raw_offer.get("privacy") or "public",
                            "url": raw_offer.get("url"),
                            "preview_url": raw_offer.get("preview_url"),
                            "logo": raw_offer.get("logo") or None,
                            "description_lang": raw_offer.get("description_lang"),
                            "categories": raw_offer.get("full_categories") or raw_offer.get("categories"),
                            "countries": raw_offer.get("countries"),
                            "payments": raw_offer.get("payments"),
                            "targeting": raw_offer.get("targeting"),
                            "tags": raw_offer.get("tags"),
                            "cr": float(raw_offer.get("cr") or 0),
                            "epc": float(raw_offer.get("epc") or 0),
                            "hold_period": int(raw_offer.get("hold_period") or 0),
                            "raw_data": raw_offer,
                            "external_created_at": raw_offer.get("created_at"),
                            "external_updated_at": raw_offer.get("updated_at"),
                            "synced_at": now,
                            "updated_at": now,
                        }
                    )

                if batch:
                    stmt = pg_insert(Offer).values(batch)
                    stmt = stmt.on_conflict_do_update(
                        index_elements=["source_id", "external_id"],
                        set_={
                            "title": stmt.excluded.title,
                            "status": stmt.excluded.status,
                            "privacy": stmt.excluded.privacy,
                            "url": stmt.excluded.url,
                            "preview_url": stmt.excluded.preview_url,
                            "logo": stmt.excluded.logo,
                            "description_lang": stmt.excluded.description_lang,
                            "categories": stmt.excluded.categories,
                            "countries": stmt.excluded.countries,
                            "payments": stmt.excluded.payments,
                            "targeting": stmt.excluded.targeting,
                            "tags": stmt.excluded.tags,
                            "cr": stmt.excluded.cr,
                            "epc": stmt.excluded.epc,
                            "hold_period": stmt.excluded.hold_period,
                            "raw_data": stmt.excluded.raw_data,
                            "external_created_at": stmt.excluded.external_created_at,
                            "external_updated_at": stmt.excluded.external_updated_at,
                            "synced_at": stmt.excluded.synced_at,
                            "updated_at": stmt.excluded.updated_at,
                        },
                    )
                    await db.execute(stmt)
                    total += len(batch)

                next_page = (response.get("pagination") or {}).get("next_page")
                if not next_page:
                    break
                page = int(next_page)
        await uow.commit()
    except Exception as exc:
        await uow.rollback()
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=f"Ошибка синхронизации: {exc}") from exc

    return {"message": f"Синхронизировано {total} офферов ({', '.join(names)})", "total": total}


@router.get("/users")
async def admin_users(
    user: AuthUser = Depends(require_admin),
    uow: UnitOfWork = Depends(api_uow),
) -> dict:
    db = uow.session
    stmt = (
        select(
            User.id,
            User.name,
            User.email,
            User.is_banned,
            User.is_admin,
            func.count(Showcase.id).label("showcases_count"),
        )
        .outerjoin(Showcase, Showcase.user_id == User.id)
        .group_by(User.id)
        .order_by(User.id.desc())
    )
    rows = (await db.execute(stmt)).all()
    return {
        "users": [
            {
                "id": row.id,
                "name": row.name,
                "email": row.email,
                "is_banned": row.is_banned,
                "is_admin": row.is_admin,
                "showcases_count": row.showcases_count,
            }
            for row in rows
        ]
    }


@router.post("/users/{user_id}/ban")
async def admin_ban_user(
    user_id: int,
    admin: AuthUser = Depends(require_admin),
    uow: UnitOfWork = Depends(api_uow),
) -> dict:
    target = await uow.users.get_by_id(user_id)
    if not target:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")
    await uow.users.set_banned(user_id, is_banned=True)
    await uow.commit()
    return {"success": True}


@router.post("/users/{user_id}/unban")
async def admin_unban_user(
    user_id: int,
    admin: AuthUser = Depends(require_admin),
    uow: UnitOfWork = Depends(api_uow),
) -> dict:
    target = await uow.users.get_by_id(user_id)
    if not target:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")
    await uow.users.set_banned(user_id, is_banned=False)
    await uow.commit()
    return {"success": True}


@router.post("/users/{user_id}/make-admin")
async def admin_make_admin(
    user_id: int,
    admin: AuthUser = Depends(require_admin),
    uow: UnitOfWork = Depends(api_uow),
) -> dict:
    target = await uow.users.get_by_id(user_id)
    if not target:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")
    await uow.users.set_admin(user_id, is_admin=True)
    await uow.commit()
    return {"success": True}


@router.post("/users/{user_id}/revoke-admin")
async def admin_revoke_admin(
    user_id: int,
    admin: AuthUser = Depends(require_admin),
    uow: UnitOfWork = Depends(api_uow),
) -> dict:
    target = await uow.users.get_by_id(user_id)
    if not target:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")
    await uow.users.set_admin(user_id, is_admin=False)
    await uow.commit()
    return {"success": True}


@router.post("/users/{user_id}/impersonate")
@inject
async def admin_impersonate(
    user_id: int,
    request: Request,
    response: Response,
    admin: AuthUser = Depends(require_admin),
    session: AppSession | None = Depends(get_current_session),
    uow: UnitOfWork = Depends(api_uow),
    sec: SecurityService = Depends(Provide[c.security_service]),
    auth_session: AuthSessionService = Depends(Provide[c.auth_session_service]),
) -> dict:
    target = await uow.users.get_by_id(user_id)
    if not target:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")

    if session:
        await uow.sessions.close_session(session.id, reason="impersonation_started")

    await auth_session.create_auth_session(uow, response, request, target, impersonator_admin_id=admin.id)
    return {"redirect": "/dashboard"}


@router.post("/impersonate/leave")
@inject
async def admin_impersonate_leave(
    request: Request,
    response: Response,
    session: AppSession | None = Depends(get_current_session),
    uow: UnitOfWork = Depends(api_uow),
    sec: SecurityService = Depends(Provide[c.security_service]),
    auth_session: AuthSessionService = Depends(Provide[c.auth_session_service]),
) -> dict:
    if not session or not session.impersonator_admin_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Not impersonating")

    admin = await uow.users.get_by_id(session.impersonator_admin_id)
    if not admin:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Admin not found")

    await uow.sessions.close_session(session.id, reason="impersonation_finished")

    await auth_session.create_auth_session(uow, response, request, admin)
    return {"redirect": "/admin/users"}
