from datetime import datetime
from typing import Any

from pydantic import BaseModel


class AdminOfferListItem(BaseModel):
    id: int
    source_id: int
    external_id: str
    title: str
    status: str
    privacy: str
    url: str | None
    preview_url: str | None
    logo: str | None
    description_lang: dict[str, Any] | list[Any] | None
    categories: dict[str, Any] | list[Any] | None
    countries: list[str] | None
    payments: list[Any] | dict[str, Any] | None
    targeting: list[Any] | dict[str, Any] | None
    tags: list[Any] | None
    cr: float
    epc: float
    hold_period: int
    synced_at: datetime | None
    created_at: datetime
    updated_at: datetime


class AdminUserItem(BaseModel):
    id: int
    name: str
    email: str
    is_banned: bool
    showcases_count: int
