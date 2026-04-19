from __future__ import annotations

from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from src.infrastructure.models.session import AppSession
from src.infrastructure.repositories._base_repository import SqlAlchemyRepository


class SessionRepository(SqlAlchemyRepository[AppSession]):
    model = AppSession

    async def get_by_id_with_user(self, session_id: str) -> AppSession | None:
        result = await self.session.execute(
            select(AppSession)
            .where(AppSession.id == session_id)
            .options(selectinload(AppSession.user))
        )
        return result.scalars().one_or_none()

    async def get_valid_by_refresh_claims(
        self,
        session_id: str,
        user_id: int,
        refresh_token_hash: str,
        now: datetime,
    ) -> AppSession | None:
        result = await self.session.execute(
            select(AppSession)
            .where(AppSession.id == session_id)
            .where(AppSession.user_id == user_id)
            .where(AppSession.refresh_token_hash == refresh_token_hash)
            .where(AppSession.expires_at > now)
            .options(selectinload(AppSession.user))
        )
        return result.scalars().one_or_none()
