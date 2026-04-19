from __future__ import annotations

from src.infrastructure.models.showcase import Showcase
from src.infrastructure.repositories._base_repository import SqlAlchemyRepository


class ShowcaseRepository(SqlAlchemyRepository[Showcase]):
    model = Showcase
