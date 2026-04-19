from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import String, cast, delete, desc, func, or_, select, text
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, HTTPException, Query, Request, Response, status

from di_container import Container as c, api_uow
from src.app.core.dependencies import require_claims, require_onboarded, require_onboarded_and_csrf, require_user, require_user_and_csrf
from src.app.schemas.auth import AuthUser, JWTClaims
from src.app.schemas.client import (
    DomainCreateRequest,
    OnboardingCompleteRequest,
    ShowcaseCreateRequest,
    ShowcaseUpdateRequest,
    UpdateCountryRequest,
)
from src.app.services.affise import AffiseService
from src.app.services.geoip import GeoIpService
from src.app.services.landing import LandingService
from src.app.services.security import SecurityService
from src.infrastructure.models.domain import Domain
from src.infrastructure.models.partner_offer import PartnerOffer
from src.infrastructure.models.showcase import Showcase
from src.infrastructure.models.user import User
from src.modules.shared.unit_of_work import UnitOfWork

router = APIRouter(prefix="", tags=["client"])

SYSTEM_DOMAINS = [
    "smart-1.smartconstruct.app",
    "offers.smartconstruct.app",
    "click.smartconstruct.app",
]


def _auth_user_from_db(db_user: User, current_user: AuthUser) -> AuthUser:
    return AuthUser(
        id=db_user.id,
        name=db_user.name,
        email=db_user.email,
        affise_password=db_user.affise_password,
        affise_country=db_user.affise_country,
        affise_id=db_user.affise_id,
        affise_api_key=db_user.affise_api_key,
        is_banned=db_user.is_banned,
        is_admin=db_user.is_admin,
        impersonating=current_user.impersonating,
    )


def _serialize_user(user: AuthUser | User) -> dict:
    return {
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "affise_password": user.affise_password,
        "affise_country": user.affise_country,
        "affise_id": user.affise_id,
        "affise_api_key": user.affise_api_key,
        "is_banned": user.is_banned,
    }


def _serialize_showcase(showcase: Showcase) -> dict:
    return {
        "id": showcase.id,
        "name": showcase.name,
        "platform_main": showcase.platform_main,
        "platform_sub": showcase.platform_sub,
        "url": showcase.url,
        "status": showcase.status,
        "config": showcase.config,
        "created_at": showcase.created_at,
        "updated_at": showcase.updated_at,
    }


def _serialize_domain(domain: Domain) -> dict:
    return {
        "id": domain.id,
        "system_domain": domain.system_domain,
        "webmaster_domain": domain.webmaster_domain,
        "status": domain.status,
        "admin_comment": domain.admin_comment,
    }


def _serialize_partner_offer(offer: PartnerOffer) -> dict:
    return {
        "id": offer.id,
        "external_id": offer.external_id,
        "title": offer.title,
        "logo": offer.logo,
        "preview_url": offer.preview_url,
        "link": offer.link,
        "description_lang": offer.description_lang,
        "categories": offer.categories,
        "countries": offer.countries,
        "payments": offer.payments,
        "targeting": offer.targeting,
        "sources": offer.sources,
        "landings": offer.landings,
        "cr": offer.cr,
        "epc": offer.epc,
        "hold_period": offer.hold_period,
        "required_approval": offer.required_approval,
        "synced_at": offer.synced_at,
    }


async def _get_custom_fields(verticals: list[str], affise: AffiseService) -> list[dict]:
    translations = {
        1: "Telegram / WhatsApp / MS Teams",
        5: "Источник трафика",
        7: "Откуда узнали о нас?",
        8: "Вертикали",
        9: "Ежемесячный рекламный бюджет",
        10: "Название компании",
    }
    traffic_sources = [
        "Google Ads",
        "Facebook Ads",
        "TikTok Ads",
        "Telegram Ads",
        "Yandex Direct",
        "Social",
        "SEO",
        "In-app",
        "Email",
        "Other",
    ]
    overrides = {
        5: {"field_type": "multiselect", "field_values": {value: value for value in traffic_sources}},
        8: {"field_type": "multiselect", "field_values": {value: value for value in verticals}},
    }
    field_order = [8, 5, 9, 10, 1, 7]

    try:
        response = await affise.get_custom_fields()
        raw_fields = response.get("fields") or []
        indexed = {}
        for field in raw_fields:
            if field.get("id") == 2:
                continue
            field_id = int(field["id"])
            merged = {**field, "name": translations.get(field_id, field.get("name")), **overrides.get(field_id, {})}
            indexed[field_id] = merged

        sorted_fields = []
        for field_id in field_order:
            if field_id in indexed:
                sorted_fields.append(indexed[field_id])
        for field_id, field in indexed.items():
            if field_id not in field_order:
                sorted_fields.append(field)
        return sorted_fields
    except Exception:
        return []


async def _get_verticals(db: AsyncSession) -> list[str]:
    query = text(
        """
        SELECT DISTINCT COALESCE(elem->>'title', trim(both '"' from elem::text)) AS title
        FROM offers
        CROSS JOIN LATERAL jsonb_array_elements(COALESCE(offers.categories, '[]'::jsonb)) AS elem
        WHERE COALESCE(elem->>'title', trim(both '"' from elem::text)) <> ''
        ORDER BY title
        """
    )
    result = await db.execute(query)
    return [row.title for row in result]


async def _get_partner_categories(db: AsyncSession, user_id: int) -> list[str]:
    query = text(
        """
        SELECT DISTINCT trim(both '"' from elem::text) AS value
        FROM partner_offers
        CROSS JOIN LATERAL jsonb_array_elements(COALESCE(partner_offers.categories, '[]'::jsonb)) AS elem
        WHERE partner_offers.user_id = :user_id
          AND trim(both '"' from elem::text) <> ''
        ORDER BY value
        """
    )
    result = await db.execute(query, {"user_id": user_id})
    return [row.value for row in result]


async def _get_partner_countries(db: AsyncSession, user_id: int) -> list[str]:
    query = text(
        """
        SELECT DISTINCT elem AS value
        FROM partner_offers
        CROSS JOIN LATERAL jsonb_array_elements_text(COALESCE(partner_offers.countries, '[]'::jsonb)) AS elem
        WHERE partner_offers.user_id = :user_id
          AND elem <> ''
        ORDER BY value
        """
    )
    result = await db.execute(query, {"user_id": user_id})
    return [row.value for row in result]


@router.get("/dashboard")
async def dashboard(user: AuthUser = Depends(require_onboarded)) -> dict:
    return {"user": _serialize_user(user)}


@router.get("/onboarding")
async def onboarding_show(
    request: Request,
    user: AuthUser = Depends(require_user),
    uow: UnitOfWork = Depends(api_uow),
) -> dict:
    if user.affise_password:
        return {"redirect": "/dashboard"}

    db = uow.session
    geoip = GeoIpService()
    affise = AffiseService()
    detected_country = await geoip.get_country_code(request.client.host if request.client else None)
    verticals = await _get_verticals(db)
    custom_fields = await _get_custom_fields(verticals, affise)
    return {"detected_country": detected_country, "custom_fields": custom_fields}


@router.post("/onboarding")
@inject
async def onboarding_complete(
    payload: OnboardingCompleteRequest,
    response: Response,
    user: AuthUser = Depends(require_user_and_csrf),
    claims: JWTClaims = Depends(require_claims),
    uow: UnitOfWork = Depends(api_uow),
    sec: SecurityService = Depends(Provide[c.security_service]),
) -> dict:
    password = sec.generate_random_password()
    affise_params: dict[str, str] = {
        "email": user.email,
        "login": user.email,
        "password": password,
        "status": "active",
        "country": payload.country,
    }
    for field_id, value in payload.custom_fields.items():
        affise_params[f"custom_fields[{field_id}]"] = ", ".join(value) if isinstance(value, list) else str(value)
    affise_params["custom_fields[2]"] = payload.country

    affise = AffiseService()
    try:
        if affise.affise_enabled:
            affise_response = await affise.create_affiliate(affise_params)
            partner = affise_response.get("partner") or {}
        else:
            partner = {}
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=f"Не удалось создать аккаунт в Affise: {exc}") from exc

    db_user = await uow.users.get_by_id(user.id)
    if not db_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    db_user.affise_password = password
    db_user.affise_country = payload.country
    db_user.affise_id = partner.get("id")
    db_user.affise_api_key = partner.get("api_key")
    await uow.commit()
    sec.set_access_token(
        response,
        _auth_user_from_db(db_user, user),
        claims.session_id,
    )
    return {"redirect": "/dashboard"}


@router.patch("/profile/country")
@inject
async def update_country(
    payload: UpdateCountryRequest,
    response: Response,
    user: AuthUser = Depends(require_onboarded_and_csrf),
    claims: JWTClaims = Depends(require_claims),
    uow: UnitOfWork = Depends(api_uow),
    sec: SecurityService = Depends(Provide[c.security_service]),
) -> dict:
    db_user = await uow.users.get_by_id(user.id)
    if not db_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    db_user.affise_country = payload.country
    await uow.commit()
    sec.set_access_token(
        response,
        _auth_user_from_db(db_user, user),
        claims.session_id,
    )
    return {"success": True}


@router.get("/offers")
async def client_offers(
    user: AuthUser = Depends(require_onboarded),
    uow: UnitOfWork = Depends(api_uow),
    search: str | None = Query(default=None),
    category: str | None = Query(default=None),
    country: str | None = Query(default=None),
    page: int = Query(default=1, ge=1),
) -> dict:
    db = uow.session
    page_size = 50
    stmt = select(PartnerOffer).where(PartnerOffer.user_id == user.id)
    if search:
        stmt = stmt.where(
            or_(
                PartnerOffer.title.ilike(f"%{search}%"),
                cast(PartnerOffer.external_id, String).ilike(f"%{search}%"),
            )
        )
    if category:
        stmt = stmt.where(text("EXISTS (SELECT 1 FROM jsonb_array_elements(COALESCE(partner_offers.categories, '[]'::jsonb)) elem WHERE trim(both '\"' from elem::text) = :category)")).params(category=category)
    if country:
        stmt = stmt.where(text("EXISTS (SELECT 1 FROM jsonb_array_elements_text(COALESCE(partner_offers.countries, '[]'::jsonb)) elem WHERE elem = :country)")).params(country=country)

    total = await db.scalar(select(func.count()).select_from(stmt.subquery()))
    stmt = stmt.order_by(desc(PartnerOffer.external_id)).offset((page - 1) * page_size).limit(page_size)
    offers = (await db.execute(stmt)).scalars().all()
    synced_at = await db.scalar(select(func.max(PartnerOffer.synced_at)).where(PartnerOffer.user_id == user.id))

    return {
        "offers": {
            "data": [_serialize_partner_offer(offer) for offer in offers],
            "meta": {
                "total": total or 0,
                "page": page,
                "per_page": page_size,
                "last_page": ((total or 0) + page_size - 1) // page_size,
            },
        },
        "filters": {"search": search or "", "category": category or "", "country": country or ""},
        "categories": await _get_partner_categories(db, user.id),
        "countries": await _get_partner_countries(db, user.id),
        "synced_at": synced_at,
        "has_api_key": bool(user.affise_api_key),
    }


@router.post("/offers/sync")
async def client_offers_sync(
    user: AuthUser = Depends(require_onboarded_and_csrf),
    uow: UnitOfWork = Depends(api_uow),
) -> dict:
    if not user.affise_api_key:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="API-ключ Affise не найден.")

    db = uow.session
    affise = AffiseService()
    total = 0
    page = 1
    now = datetime.now(timezone.utc)
    synced_ids: list[int] = []

    try:
        while True:
            response = await affise.get_partner_offers(user.affise_api_key, page=page, limit=500)
            offers = response.get("offers") or []
            if not offers:
                break

            batch = []
            for offer in offers:
                external_id = int(offer.get("id") or offer.get("offer_id"))
                synced_ids.append(external_id)
                batch.append(
                    {
                        "user_id": user.id,
                        "external_id": external_id,
                        "title": offer.get("title") or "",
                        "logo": offer.get("logo") or "",
                        "preview_url": offer.get("preview_url") or "",
                        "link": offer.get("link") or "",
                        "description_lang": offer.get("description_lang") or [],
                        "categories": offer.get("categories") or [],
                        "countries": offer.get("countries") or [],
                        "payments": offer.get("payments") or [],
                        "targeting": offer.get("targeting") or [],
                        "sources": offer.get("sources") or [],
                        "landings": offer.get("landings") or [],
                        "cr": float(offer.get("cr") or 0),
                        "epc": float(offer.get("epc") or 0),
                        "hold_period": int(offer.get("hold_period") or 0),
                        "required_approval": bool(offer.get("required_approval") or False),
                        "raw_data": offer,
                        "synced_at": now,
                        "updated_at": now,
                    }
                )
            if batch:
                stmt = pg_insert(PartnerOffer).values(batch)
                stmt = stmt.on_conflict_do_update(
                    index_elements=["user_id", "external_id"],
                    set_={
                        "title": stmt.excluded.title,
                        "logo": stmt.excluded.logo,
                        "preview_url": stmt.excluded.preview_url,
                        "link": stmt.excluded.link,
                        "description_lang": stmt.excluded.description_lang,
                        "categories": stmt.excluded.categories,
                        "countries": stmt.excluded.countries,
                        "payments": stmt.excluded.payments,
                        "targeting": stmt.excluded.targeting,
                        "sources": stmt.excluded.sources,
                        "landings": stmt.excluded.landings,
                        "cr": stmt.excluded.cr,
                        "epc": stmt.excluded.epc,
                        "hold_period": stmt.excluded.hold_period,
                        "required_approval": stmt.excluded.required_approval,
                        "raw_data": stmt.excluded.raw_data,
                        "synced_at": stmt.excluded.synced_at,
                        "updated_at": stmt.excluded.updated_at,
                    },
                )
                await db.execute(stmt)
            total += len(offers)
            next_page = (response.get("pagination") or {}).get("next_page")
            if not next_page:
                break
            page = int(next_page)

        if synced_ids:
            await db.execute(
                delete(PartnerOffer)
                .where(PartnerOffer.user_id == user.id)
                .where(PartnerOffer.external_id.not_in(synced_ids))
            )
        await uow.commit()
    except Exception as exc:
        await uow.rollback()
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=f"Ошибка синхронизации: {exc}") from exc

    return {"message": f"Синхронизировано {total} офферов", "total": total}


@router.get("/showcases")
async def showcases_index(
    user: AuthUser = Depends(require_onboarded),
    uow: UnitOfWork = Depends(api_uow),
) -> dict:
    db = uow.session
    showcases = (
        await db.execute(select(Showcase).where(Showcase.user_id == user.id).order_by(Showcase.created_at.desc()))
    ).scalars().all()
    domains = (
        await db.execute(select(Domain).where(Domain.user_id == user.id).order_by(Domain.created_at.desc()))
    ).scalars().all()
    return {
        "showcases": [_serialize_showcase(item) for item in showcases],
        "domains": [_serialize_domain(item) for item in domains],
        "systemDomains": SYSTEM_DOMAINS,
    }


@router.post("/showcases")
async def showcase_store(
    payload: ShowcaseCreateRequest,
    user: AuthUser = Depends(require_onboarded_and_csrf),
    uow: UnitOfWork = Depends(api_uow),
) -> dict:
    showcase = Showcase(
        user_id=user.id,
        name=payload.name,
        platform_main=payload.platform_main,
        platform_sub=payload.platform_sub,
        url=payload.url,
        status="draft",
    )
    await uow.showcases.add(showcase)
    await uow.commit()
    await uow.refresh(showcase)
    return {"showcase": _serialize_showcase(showcase), "redirect": f"/showcases/{showcase.id}/edit"}


@router.get("/showcases/{showcase_id}")
async def showcase_edit(
    showcase_id: int,
    user: AuthUser = Depends(require_onboarded),
    uow: UnitOfWork = Depends(api_uow),
) -> dict:
    db = uow.session
    showcase = (
        await db.execute(
            select(Showcase)
            .where(Showcase.id == showcase_id, Showcase.user_id == user.id)
            .options(selectinload(Showcase.user).selectinload(User.partner_offers))
        )
    ).scalar_one_or_none()
    if not showcase:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")

    domains = (
        await db.execute(
            select(Domain)
            .where(Domain.user_id == user.id, Domain.status == "active")
            .order_by(Domain.created_at.desc())
        )
    ).scalars().all()

    landing = LandingService()
    return {
        "showcase": _serialize_showcase(showcase),
        "offers": [_serialize_partner_offer(item) for item in showcase.user.partner_offers],
        "domains": [_serialize_domain(item) for item in domains],
        "systemDomains": SYSTEM_DOMAINS,
        "previewUrl": landing.get_preview_url(showcase.id),
    }


@router.put("/showcases/{showcase_id}")
async def showcase_update(
    showcase_id: int,
    payload: ShowcaseUpdateRequest,
    user: AuthUser = Depends(require_onboarded_and_csrf),
    uow: UnitOfWork = Depends(api_uow),
) -> dict:
    db = uow.session
    showcase = (
        await db.execute(
            select(Showcase)
            .where(Showcase.id == showcase_id, Showcase.user_id == user.id)
            .options(selectinload(Showcase.user).selectinload(User.partner_offers))
        )
    ).scalar_one_or_none()
    if not showcase:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")

    update_data = payload.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(showcase, key, value)
    await uow.commit()
    await uow.refresh(showcase)

    preview_url = None
    if "config" in update_data:
        preview_url = await LandingService().generate(db, showcase)

    return {"success": True, "showcase": _serialize_showcase(showcase), "previewUrl": preview_url}


@router.post("/showcases/{showcase_id}/duplicate")
async def showcase_duplicate(
    showcase_id: int,
    user: AuthUser = Depends(require_onboarded_and_csrf),
    uow: UnitOfWork = Depends(api_uow),
) -> dict:
    db = uow.session

    showcase = (
        await db.execute(select(Showcase).where(Showcase.id == showcase_id, Showcase.user_id == user.id))
    ).scalar_one_or_none()
    if not showcase:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")

    copy = Showcase(
        user_id=user.id,
        name=showcase.name,
        platform_main=showcase.platform_main,
        platform_sub=showcase.platform_sub,
        url=showcase.url,
        status="draft",
        config=showcase.config,
    )
    await uow.showcases.add(copy)
    await uow.commit()
    await uow.refresh(copy)
    return {"success": True, "message": "Витрина скопирована", "showcase": _serialize_showcase(copy)}


@router.delete("/showcases/{showcase_id}")
async def showcase_destroy(
    showcase_id: int,
    user: AuthUser = Depends(require_onboarded_and_csrf),
    uow: UnitOfWork = Depends(api_uow),
) -> dict:
    db = uow.session

    showcase = (
        await db.execute(select(Showcase).where(Showcase.id == showcase_id, Showcase.user_id == user.id))
    ).scalar_one_or_none()
    if not showcase:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")
    await uow.showcases.delete(showcase)
    await uow.commit()
    return {"success": True, "message": "Витрина удалена"}


@router.post("/domains")
async def domain_store(
    payload: DomainCreateRequest,
    user: AuthUser = Depends(require_onboarded_and_csrf),
    uow: UnitOfWork = Depends(api_uow),
) -> dict:
    domain = Domain(
        user_id=user.id,
        system_domain=payload.system_domain,
        webmaster_domain=payload.webmaster_domain,
        status="pending",
    )
    await uow.domains.add(domain)
    await uow.commit()
    await uow.refresh(domain)
    return {"success": True, "message": "Домен сохранён", "domain": _serialize_domain(domain)}


@router.delete("/domains/{domain_id}")
async def domain_destroy(
    domain_id: int,
    user: AuthUser = Depends(require_onboarded_and_csrf),
    uow: UnitOfWork = Depends(api_uow),
) -> dict:
    db = uow.session

    domain = (
        await db.execute(select(Domain).where(Domain.id == domain_id, Domain.user_id == user.id))
    ).scalar_one_or_none()
    if not domain:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")
    await uow.domains.delete(domain)
    await uow.commit()
    return {"success": True, "message": "Домен удалён"}
