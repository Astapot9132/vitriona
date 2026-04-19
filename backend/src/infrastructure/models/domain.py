from __future__ import annotations

from sqlalchemy import BigInteger, ForeignKey, Identity, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.app.core.db import Base, TimestampMixin


class Domain(Base, TimestampMixin):
    __tablename__ = "domains"

    id: Mapped[int] = mapped_column(BigInteger, Identity(), primary_key=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), index=True)
    system_domain: Mapped[str] = mapped_column(String(255), nullable=False)
    webmaster_domain: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[str] = mapped_column(String(64), default="pending", nullable=False)
    admin_comment: Mapped[str | None] = mapped_column(String(255), nullable=True)

    user = relationship("User", back_populates="domains")
