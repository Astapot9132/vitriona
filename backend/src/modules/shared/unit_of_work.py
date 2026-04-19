from __future__ import annotations

from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from src.infrastructure.repositories.domain_repository import DomainRepository
from src.infrastructure.repositories.offer_repository import OfferRepository
from src.infrastructure.repositories.offer_source_repository import OfferSourceRepository
from src.infrastructure.repositories.partner_offer_repository import PartnerOfferRepository
from src.infrastructure.repositories.pin_code_repository import PinCodeRepository
from src.infrastructure.repositories.session_repository import SessionRepository
from src.infrastructure.repositories.showcase_repository import ShowcaseRepository
from src.infrastructure.repositories.user_repository import UserRepository


class UnitOfWork:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.users = UserRepository(session)
        self.pin_codes = PinCodeRepository(session)
        self.sessions = SessionRepository(session)
        self.domains = DomainRepository(session)
        self.showcases = ShowcaseRepository(session)
        self.partner_offers = PartnerOfferRepository(session)
        self.offers = OfferRepository(session)
        self.offer_sources = OfferSourceRepository(session)

    async def __aenter__(self) -> "UnitOfWork":
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        if exc_type:
            await self.session.rollback()
        return await self.session.__aexit__(exc_type, exc_val, exc_tb)

    async def commit(self) -> None:
        await self.session.commit()

    async def rollback(self) -> None:
        await self.session.rollback()

    async def flush(self) -> None:
        await self.session.flush()

    async def refresh(self, instance: Any) -> None:
        await self.session.refresh(instance)
