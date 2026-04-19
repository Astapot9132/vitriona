from __future__ import annotations

import logging
from typing import Any

import httpx

from src.app.core.config import Settings, get_settings


logger = logging.getLogger(__name__)


class AffiseService:
    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or get_settings()
        self.base_url = self.settings.affise_api_url.rstrip("/")

    async def get_custom_fields(self) -> dict[str, Any]:
        return await self._request("GET", "/3.0/admin/custom_fields", headers={"API-Key": self.settings.affise_api_key})

    async def get_offers(self, page: int = 1, limit: int = 500) -> dict[str, Any]:
        return await self._request(
            "GET",
            "/3.0/offers",
            params={"page": page, "limit": limit},
            headers={"API-Key": self.settings.affise_api_key},
        )

    async def create_affiliate(self, data: dict[str, Any]) -> dict[str, Any]:
        return await self._request(
            "POST",
            "/3.0/admin/partner",
            headers={"api-key": self.settings.affise_api_key},
            data=data,
        )

    async def get_partner_offers(
        self,
        partner_api_key: str,
        page: int = 1,
        limit: int = 500,
    ) -> dict[str, Any]:
        return await self._request(
            "GET",
            "/3.0/partner/offers",
            headers={"API-Key": partner_api_key},
            params={"page": page, "limit": limit},
        )

    async def _request(
        self,
        method: str,
        path: str,
        headers: dict[str, str] | None = None,
        params: dict[str, Any] | None = None,
        data: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        async with httpx.AsyncClient(base_url=self.base_url, timeout=30.0) as client:
            response = await client.request(method, path, headers=headers, params=params, data=data)

        if response.is_error:
            logger.error("Affise request failed: %s %s", response.status_code, response.text)
            raise RuntimeError(f"Affise API error {response.status_code}: {response.text}")

        return response.json()
