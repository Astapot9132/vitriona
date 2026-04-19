from __future__ import annotations

from sqlalchemy import BigInteger, Boolean, Identity, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.app.core.db import Base, TimestampMixin


class OfferSource(Base, TimestampMixin):
    __tablename__ = "offer_sources"

    id: Mapped[int] = mapped_column(BigInteger, Identity(), primary_key=True)
    name: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    type: Mapped[str] = mapped_column(String(64), nullable=False)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    offers = relationship("Offer", back_populates="source", cascade="all, delete-orphan")
