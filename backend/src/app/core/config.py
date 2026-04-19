from functools import lru_cache
from typing import Any

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = Field("New Vitriona", alias="APP_NAME")
    app_env: str = Field("local", alias="APP_ENV")
    app_debug: bool = Field(True, alias="APP_DEBUG")
    dev: bool = Field(False, alias="DEV")
    app_url: str = Field("http://localhost:8000", alias="APP_URL")
    frontend_url: str = Field("http://localhost:5173", alias="FRONTEND_URL")
    storage_dir: str = Field("/app/storage", alias="STORAGE_DIR")
    jwt_secret: str = Field(alias="JWT_SECRET")
    csrf_secret: str = Field(alias="CSRF_SECRET")
    refresh_token_pepper: str = Field(alias="REFRESH_TOKEN_PEPPER")
    database_url: str = Field(alias="DATABASE_URL")
    sync_database_url: str = Field(alias="SYNC_DATABASE_URL")
    redis_url: str = Field("redis://redis:6379/0", alias="REDIS_URL")
    access_cookie: str = Field("access_token", alias="ACCESS_COOKIE")
    refresh_cookie: str = Field("refresh_token", alias="REFRESH_COOKIE")
    csrf_cookie: str = Field("csrf_token", alias="CSRF_COOKIE")
    csrf_header: str = Field("X-CSRF-Token", alias="CSRF_HEADER")
    access_token_expire_seconds: int = Field(900, alias="ACCESS_TOKEN_EXPIRE_SECONDS")
    refresh_token_expire_seconds: int = Field(2592000, alias="REFRESH_TOKEN_EXPIRE_SECONDS")
    refresh_cookie_path: str = Field("/api/auth", alias="REFRESH_COOKIE_PATH")
    admins_list_raw: str = Field("[]", alias="ADMINS_LIST")
    mail_from_address: str = Field("noreply@example.com", alias="MAIL_FROM_ADDRESS")
    mail_from_name: str = Field("New Vitriona", alias="MAIL_FROM_NAME")
    mail_transport: str = Field("log", alias="MAIL_TRANSPORT")
    affise_enabled: bool = Field(True, alias="AFFISE_ENABLED")
    affise_api_url: str = Field("https://api-s-y-n-c.affise.com", alias="AFFISE_API_URL")
    affise_api_key: str = Field("", alias="AFFISE_API_KEY")
    telegram_bot_token: str = Field("", alias="TELEGRAM_BOT_TOKEN")
    telegram_chat_id: str = Field("", alias="TELEGRAM_CHAT_ID")
    telegram_log_level: str = Field("ERROR", alias="TELEGRAM_LOG_LEVEL")

    @property
    def is_local_like(self) -> bool:
        return self.app_env in {"local", "staging"}

    @property
    def cookie_secure(self) -> bool:
        return not self.dev

    @property
    def admins_list(self) -> list[dict[str, Any]]:
        import json

        try:
            data = json.loads(self.admins_list_raw)
            return data if isinstance(data, list) else []
        except Exception:
            return []


@lru_cache
def get_settings() -> Settings:
    return Settings()
