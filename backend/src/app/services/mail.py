from __future__ import annotations

import logging

from cfg import MAIL_TRANSPORT


logger = logging.getLogger(__name__)


class MailService:
    async def send_pin(self, email: str, pin: str) -> None:
        logger.info(
            "PIN code generated",
            extra={
                "email": email,
                "pin": pin,
                "transport": MAIL_TRANSPORT,
            },
        )
