from __future__ import annotations

from abc import ABC
from typing import Generic, TypeVar

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


ModelT = TypeVar("ModelT")


class SqlAlchemyRepository(ABC, Generic[ModelT]):
    model: type[ModelT]

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, id_: int | str) -> ModelT | None:
        result = await self.session.execute(select(self.model).where(self.model.id == id_))  # type: ignore[attr-defined]
        return result.scalars().one_or_none()

    async def add(self, instance: ModelT) -> ModelT:
        self.session.add(instance)
        return instance

    async def delete(self, instance: ModelT) -> None:
        await self.session.delete(instance)
