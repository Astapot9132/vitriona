from __future__ import annotations

from datetime import datetime

from sqlalchemy import BigInteger, Boolean, DateTime, Float, ForeignKey, Identity, Integer, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.app.core.db import Base, TimestampMixin


class PartnerOffer(Base, TimestampMixin):
    __tablename__ = "partner_offers"
    __table_args__ = (UniqueConstraint("user_id", "external_id", name="uq_partner_offers_user_external"),)

    id: Mapped[int] = mapped_column(BigInteger, Identity(), primary_key=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), index=True)
    external_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    logo: Mapped[str] = mapped_column(String(1024), default="", nullable=False)
    preview_url: Mapped[str] = mapped_column(String(1024), default="", nullable=False)
    link: Mapped[str] = mapped_column(Text, default="", nullable=False)
    description_lang: Mapped[dict | list | None] = mapped_column(JSONB, nullable=True)
    categories: Mapped[list | None] = mapped_column(JSONB, nullable=True)
    countries: Mapped[list | None] = mapped_column(JSONB, nullable=True)
    payments: Mapped[list | dict | None] = mapped_column(JSONB, nullable=True)
    targeting: Mapped[list | dict | None] = mapped_column(JSONB, nullable=True)
    sources: Mapped[list | dict | None] = mapped_column(JSONB, nullable=True)
    landings: Mapped[list | dict | None] = mapped_column(JSONB, nullable=True)
    cr: Mapped[float] = mapped_column(Float, default=0, nullable=False)
    epc: Mapped[float] = mapped_column(Float, default=0, nullable=False)
    hold_period: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    required_approval: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    raw_data: Mapped[dict | list | None] = mapped_column(JSONB, nullable=True)
    synced_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    user = relationship("User", back_populates="partner_offers")
