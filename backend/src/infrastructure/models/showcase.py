from __future__ import annotations

from sqlalchemy import BigInteger, ForeignKey, Identity, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.app.core.db import Base, TimestampMixin


class Showcase(Base, TimestampMixin):
    __tablename__ = "showcases"

    id: Mapped[int] = mapped_column(BigInteger, Identity(), primary_key=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    platform_main: Mapped[str] = mapped_column(String(255), nullable=False)
    platform_sub: Mapped[str | None] = mapped_column(String(255), nullable=True)
    url: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[str] = mapped_column(String(64), default="draft", nullable=False)
    config: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    user = relationship("User", back_populates="showcases")
