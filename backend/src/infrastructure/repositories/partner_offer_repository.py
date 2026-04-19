from __future__ import annotations

from src.infrastructure.models.partner_offer import PartnerOffer
from src.infrastructure.repositories._base_repository import SqlAlchemyRepository


class PartnerOfferRepository(SqlAlchemyRepository[PartnerOffer]):
    model = PartnerOffer
