from __future__ import annotations

from cryptography.fernet import Fernet

from cfg import AFFISE_DATA_SECRET


class CryptoService:
    def __init__(self) -> None:
        self._cipher = Fernet(AFFISE_DATA_SECRET.encode("utf-8"))

    def encrypt_text(self, value: str | None) -> str | None:
        if value is None:
            return None
        return self._cipher.encrypt(value.encode("utf-8")).decode("utf-8")

    def decrypt_text(self, value: str | None) -> str | None:
        if value is None:
            return None
        return self._cipher.decrypt(value.encode("utf-8")).decode("utf-8")
