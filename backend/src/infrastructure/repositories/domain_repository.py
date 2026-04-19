from __future__ import annotations

from src.infrastructure.models.domain import Domain
from src.infrastructure.repositories._base_repository import SqlAlchemyRepository


class DomainRepository(SqlAlchemyRepository[Domain]):
    model = Domain
