from __future__ import annotations

from datetime import datetime

from sqlalchemy import BigInteger, DateTime, Float, ForeignKey, Identity, Index, Integer, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.app.core.db import Base, TimestampMixin


class Offer(Base, TimestampMixin):
    __tablename__ = "offers"
    __table_args__ = (
        UniqueConstraint("source_id", "external_id", name="uq_offers_source_external"),
        Index("ix_offers_status", "status"),
    )

    id: Mapped[int] = mapped_column(BigInteger, Identity(), primary_key=True)
    source_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("offer_sources.id", ondelete="CASCADE"), index=True)
    external_id: Mapped[str] = mapped_column(String(255), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[str] = mapped_column(String(64), default="active", nullable=False)
    privacy: Mapped[str] = mapped_column(String(64), default="public", nullable=False)
    url: Mapped[str | None] = mapped_column(Text, nullable=True)
    preview_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    logo: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    description_lang: Mapped[dict | list | None] = mapped_column(JSONB, nullable=True)
    categories: Mapped[dict | list | None] = mapped_column(JSONB, nullable=True)
    countries: Mapped[list | None] = mapped_column(JSONB, nullable=True)
    payments: Mapped[list | dict | None] = mapped_column(JSONB, nullable=True)
    targeting: Mapped[list | dict | None] = mapped_column(JSONB, nullable=True)
    tags: Mapped[list | None] = mapped_column(JSONB, nullable=True)
    cr: Mapped[float] = mapped_column(Float, default=0, nullable=False)
    epc: Mapped[float] = mapped_column(Float, default=0, nullable=False)
    hold_period: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    raw_data: Mapped[dict | list | None] = mapped_column(JSONB, nullable=True)
    external_created_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    external_updated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    synced_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    source = relationship("OfferSource", back_populates="offers")
