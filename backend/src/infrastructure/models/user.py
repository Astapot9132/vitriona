from __future__ import annotations

from sqlalchemy import BigInteger, Boolean, Identity, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.app.core.db import Base, TimestampMixin


class User(Base, TimestampMixin):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(BigInteger, Identity(), primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    is_banned: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    affise_password: Mapped[str | None] = mapped_column(Text, nullable=True)
    affise_country: Mapped[str | None] = mapped_column(String(2), nullable=True)
    affise_id: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    affise_api_key: Mapped[str | None] = mapped_column(Text, nullable=True)

    showcases = relationship("Showcase", back_populates="user", cascade="all, delete-orphan")
    domains = relationship("Domain", back_populates="user", cascade="all, delete-orphan")
    partner_offers = relationship("PartnerOffer", back_populates="user", cascade="all, delete-orphan")
    sessions = relationship("AppSession", back_populates="user", cascade="all, delete-orphan")
