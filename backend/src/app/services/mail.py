from __future__ import annotations

import logging

from src.app.core.config import Settings, get_settings


logger = logging.getLogger(__name__)


class MailService:
    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or get_settings()

    async def send_pin(self, email: str, pin: str) -> None:
        logger.info(
            "PIN code generated",
            extra={
                "email": email,
                "pin": pin,
                "transport": self.settings.mail_transport,
            },
        )
