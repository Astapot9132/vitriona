from __future__ import annotations

import logging

import httpx


logger = logging.getLogger(__name__)


class GeoIpService:
    async def get_country_code(self, ip: str | None) -> str | None:
        if not ip:
            return None

        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(
                    f"http://ip-api.com/json/{ip}",
                    params={"fields": "status,countryCode"},
                )
            response.raise_for_status()
            data = response.json()
            if data.get("status") == "success":
                return data.get("countryCode") or None
        except Exception as exc:
            logger.warning("GeoIp lookup failed: %s", exc)

        return None
