from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import select, update
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

    async def get_by_refresh_claims(
        self,
        session_id: str,
        user_id: int,
        refresh_token_hash: str,
    ) -> AppSession | None:
        result = await self.session.execute(
            select(AppSession)
            .where(AppSession.id == session_id)
            .where(AppSession.user_id == user_id)
            .where(AppSession.refresh_token_hash == refresh_token_hash)
            .options(selectinload(AppSession.user))
        )
        return result.scalars().one_or_none()

    async def close_session(self, session_id: str, *, reason: str) -> None:
        await self.session.execute(
            update(AppSession)
            .where(AppSession.id == session_id)
            .values(
                is_closed=True,
                closed_at=datetime.now(timezone.utc),
                close_reason=reason,
                refresh_token_hash=None,
            )
        )

    async def set_refresh_token_hash(self, session_id: str, *, refresh_token_hash: str) -> None:
        await self.session.execute(
            update(AppSession)
            .where(AppSession.id == session_id)
            .values(refresh_token_hash=refresh_token_hash)
        )

    async def rotate_session(
        self,
        session_id: str,
        *,
        refresh_token_hash: str,
        expires_at: datetime,
    ) -> None:
        await self.session.execute(
            update(AppSession)
            .where(AppSession.id == session_id)
            .values(
                refresh_token_hash=refresh_token_hash,
                last_seen_at=datetime.now(timezone.utc),
                expires_at=expires_at,
                is_closed=False,
                closed_at=None,
                close_reason=None,
            )
        )
