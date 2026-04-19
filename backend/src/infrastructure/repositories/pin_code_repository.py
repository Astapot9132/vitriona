from __future__ import annotations

from datetime import datetime

from sqlalchemy import delete, select

from src.infrastructure.models.pin_code import PinCode
from src.infrastructure.repositories._base_repository import SqlAlchemyRepository


class PinCodeRepository(SqlAlchemyRepository[PinCode]):
    model = PinCode

    async def delete_by_email(self, email: str) -> None:
        await self.session.execute(delete(PinCode).where(PinCode.email == email))

    async def get_latest_active(self, email: str, now: datetime, max_attempts: int) -> PinCode | None:
        result = await self.session.execute(
            select(PinCode)
            .where(PinCode.email == email)
            .where(PinCode.expires_at > now)
            .where(PinCode.attempts < max_attempts)
            .order_by(PinCode.created_at.desc())
        )
        return result.scalars().first()
