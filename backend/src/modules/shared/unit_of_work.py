from __future__ import annotations

from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from src.infrastructure.repositories.domain_repository import DomainRepository
from src.infrastructure.repositories.offer_repository import OfferRepository
from src.infrastructure.repositories.offer_source_repository import OfferSourceRepository
from src.infrastructure.repositories.partner_offer_repository import PartnerOfferRepository
from src.infrastructure.repositories.pin_code_repository import PinCodeRepository
from src.infrastructure.repositories.session_repository import SessionRepository
from src.infrastructure.repositories.showcase_repository import ShowcaseRepository
from src.infrastructure.repositories.user_repository import UserRepository


class UnitOfWork:
    def __init__(self, session_factory: async_sessionmaker[AsyncSession]):
        self._session_factory = session_factory
        self.session: AsyncSession | None = None
        self._user_repository: UserRepository | None = None
        self._pin_code_repository: PinCodeRepository | None = None
        self._session_repository: SessionRepository | None = None
        self._domain_repository: DomainRepository | None = None
        self._showcase_repository: ShowcaseRepository | None = None
        self._partner_offer_repository: PartnerOfferRepository | None = None
        self._offer_repository: OfferRepository | None = None
        self._offer_source_repository: OfferSourceRepository | None = None

    async def __aenter__(self) -> "UnitOfWork":
        self.session = self._session_factory()
        self._user_repository = UserRepository(self.session)
        self._pin_code_repository = PinCodeRepository(self.session)
        self._session_repository = SessionRepository(self.session)
        self._domain_repository = DomainRepository(self.session)
        self._showcase_repository = ShowcaseRepository(self.session)
        self._partner_offer_repository = PartnerOfferRepository(self.session)
        self._offer_repository = OfferRepository(self.session)
        self._offer_source_repository = OfferSourceRepository(self.session)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        if not self.session:
            return
        try:
            if exc_type:
                await self.session.rollback()
        finally:
            await self.session.close()

    async def commit(self) -> None:
        self._require_session()
        await self.session.commit()

    async def rollback(self) -> None:
        self._require_session()
        await self.session.rollback()

    async def flush(self) -> None:
        self._require_session()
        await self.session.flush()

    async def refresh(self, instance: Any) -> None:
        self._require_session()
        await self.session.refresh(instance)

    @property
    def db(self) -> AsyncSession:
        self._require_session()
        return self.session

    @property
    def users(self) -> UserRepository:
        if not self._user_repository:
            raise RuntimeError("UserRepository is not initialized")
        return self._user_repository

    @property
    def pin_codes(self) -> PinCodeRepository:
        if not self._pin_code_repository:
            raise RuntimeError("PinCodeRepository is not initialized")
        return self._pin_code_repository

    @property
    def sessions(self) -> SessionRepository:
        if not self._session_repository:
            raise RuntimeError("SessionRepository is not initialized")
        return self._session_repository

    @property
    def domains(self) -> DomainRepository:
        if not self._domain_repository:
            raise RuntimeError("DomainRepository is not initialized")
        return self._domain_repository

    @property
    def showcases(self) -> ShowcaseRepository:
        if not self._showcase_repository:
            raise RuntimeError("ShowcaseRepository is not initialized")
        return self._showcase_repository

    @property
    def partner_offers(self) -> PartnerOfferRepository:
        if not self._partner_offer_repository:
            raise RuntimeError("PartnerOfferRepository is not initialized")
        return self._partner_offer_repository

    @property
    def offers(self) -> OfferRepository:
        if not self._offer_repository:
            raise RuntimeError("OfferRepository is not initialized")
        return self._offer_repository

    @property
    def offer_sources(self) -> OfferSourceRepository:
        if not self._offer_source_repository:
            raise RuntimeError("OfferSourceRepository is not initialized")
        return self._offer_source_repository

    def _require_session(self) -> None:
        if not self.session:
            raise RuntimeError("UnitOfWork is not initialized")
