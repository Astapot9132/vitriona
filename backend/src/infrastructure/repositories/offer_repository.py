from __future__ import annotations

from src.infrastructure.models.offer import Offer
from src.infrastructure.repositories._base_repository import SqlAlchemyRepository


class OfferRepository(SqlAlchemyRepository[Offer]):
    model = Offer
