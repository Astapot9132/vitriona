from __future__ import annotations

from src.infrastructure.models.offer_source import OfferSource
from src.infrastructure.repositories._base_repository import SqlAlchemyRepository


class OfferSourceRepository(SqlAlchemyRepository[OfferSource]):
    model = OfferSource
