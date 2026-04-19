from __future__ import annotations

from datetime import datetime

from sqlalchemy import BigInteger, DateTime, Identity, SmallInteger, String
from sqlalchemy.orm import Mapped, mapped_column

from src.app.core.db import Base, TimestampMixin


class PinCode(Base, TimestampMixin):
    __tablename__ = "pin_codes"

    id: Mapped[int] = mapped_column(BigInteger, Identity(), primary_key=True)
    email: Mapped[str] = mapped_column(String(255), index=True, nullable=False)
    code_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    ip_address: Mapped[str | None] = mapped_column(String(45), nullable=True)
    attempts: Mapped[int] = mapped_column(SmallInteger, default=0, nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
