from __future__ import annotations

from sqlalchemy import update

from src.infrastructure.models.showcase import Showcase
from src.infrastructure.repositories._base_repository import SqlAlchemyRepository


class ShowcaseRepository(SqlAlchemyRepository[Showcase]):
    model = Showcase

    async def update_fields(self, showcase_id: int, **values) -> None:
        await self.session.execute(
            update(Showcase)
            .where(Showcase.id == showcase_id)
            .values(**values)
        )
