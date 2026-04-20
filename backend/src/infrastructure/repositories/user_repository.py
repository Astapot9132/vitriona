from __future__ import annotations

from sqlalchemy import select, update
from sqlalchemy.dialects.postgresql import insert as pg_insert

from src.infrastructure.models.user import User
from src.infrastructure.repositories._base_repository import SqlAlchemyRepository


class UserRepository(SqlAlchemyRepository[User]):
    model = User

    async def get_by_email(self, email: str) -> User | None:
        result = await self.session.execute(select(User).where(User.email == email))
        return result.scalars().one_or_none()

    async def get_or_create(self, *, email: str, name: str, password_hash: str) -> User:
        await self.session.execute(
            pg_insert(User)
            .values(email=email, name=name, password_hash=password_hash)
            .on_conflict_do_nothing(index_elements=[User.email])
        )
        user = await self.get_by_email(email)
        if not user:
            raise RuntimeError("Failed to load user after upsert")
        return user

    async def set_banned(self, user_id: int, *, is_banned: bool) -> None:
        await self.session.execute(
            update(User)
            .where(User.id == user_id)
            .values(is_banned=is_banned)
        )

    async def set_admin(self, user_id: int, *, is_admin: bool) -> None:
        await self.session.execute(
            update(User)
            .where(User.id == user_id)
            .values(is_admin=is_admin)
        )

    async def update_affise_profile(
        self,
        user_id: int,
        *,
        affise_password: str,
        affise_country: str,
        affise_id: int | None,
        affise_api_key: str | None,
    ) -> None:
        await self.session.execute(
            update(User)
            .where(User.id == user_id)
            .values(
                affise_password=affise_password,
                affise_country=affise_country,
                affise_id=affise_id,
                affise_api_key=affise_api_key,
            )
        )

    async def update_affise_country(self, user_id: int, *, affise_country: str) -> None:
        await self.session.execute(
            update(User)
            .where(User.id == user_id)
            .values(affise_country=affise_country)
        )
