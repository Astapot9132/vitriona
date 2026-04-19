import json
from typing import Any

# import os
# import dotenv
#
# dotenv.load_dotenv()
#
#
#
# APP_NAME = os.getenv("APP_NAME")
# DEV = os.getenv("APP_NAME")
# APP_URL = os.getenv("APP_URL")
# STORAGE_DIR = os.getenv("STORAGE_DIR")
#
#
#
#
# JWT_SECRET = os.getenv("JWT_SECRET")
# CSRF_SECRET = os.getenv("CSRF_SECRET")
# REFRESH_TOKEN_PEPPER = os.getenv("REFRESH_TOKEN_PEPPER")
#
#
#
#
#
# POSTGRES_USER = os.getenv("POSTGRES_USER")
# POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
# POSTGRES_HOST = os.getenv("POSTGRES_HOST")
# POSTGRES_PORT = os.getenv("POSTGRES_PORT")
# POSTGRES_DB = os.getenv("POSTGRES_DB")
#
#
# DATABASE_URL = f"postgresql+asyncpg://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
# SYNC_DATABASE_URL = f"postgresql+psycopg://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
#
#
# REDIS_URL = os.getenv("APP_NAME")
#
#
# ACCESS_COOKIE = os.getenv("APP_NAME")
# REFRESH_COOKIE = os.getenv("APP_NAME")
# CSRF_COOKIE = os.getenv("APP_NAME")
# CSRF_HEADER = os.getenv("APP_NAME")
# ACCESS_TOKEN_EXPIRE_SECONDS = os.getenv("APP_NAME")
# REFRESH_TOKEN_EXPIRE_SECONDS = os.getenv("APP_NAME")
# REFRESH_COOKIE_PATH = os.getenv("APP_NAME")
# ADMINS_LIST = os.getenv("APP_NAME")
#
#
#
#
# MAIL_FROM_ADDRESS = os.getenv("APP_NAME")
# MAIL_FROM_NAME = os.getenv("APP_NAME")
# MAIL_TRANSPORT = os.getenv("APP_NAME")
#
#
#
#
# AFFISE_ENABLED = os.getenv("APP_NAME")
# AFFISE_API_URL = os.getenv("APP_NAME")
# AFFISE_API_KEY = os.getenv("APP_NAME")
#
#
# TELEGRAM_BOT_TOKEN = os.getenv("APP_NAME")
# TELEGRAM_CHAT_ID = os.getenv("APP_NAME")
# TELEGRAM_LOG_LEVEL = os.getenv("APP_NAME")
#


from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Cfg(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    APP_NAME: str = Field()
    DEV: bool = Field()
    BACKEND_URL: str = Field()
    FRONTEND_URL: str = Field()
    STORAGE_DIR: str = Field()

    JWT_SECRET: str = Field()
    CSRF_SECRET: str = Field()
    REFRESH_TOKEN_PEPPER: str = Field()

    POSTGRES_USER: str = Field()
    POSTGRES_PASSWORD: str = Field()
    POSTGRES_HOST: str = Field()
    POSTGRES_PORT: int = Field()
    POSTGRES_DB: str = Field()

    REDIS_URL: str = Field()

    ACCESS_COOKIE: str = Field("access_token")
    REFRESH_COOKIE: str = Field("refresh_token")
    CSRF_COOKIE: str = Field("csrf_token")
    CSRF_HEADER: str = Field("X-CSRF-Token")
    ACCESS_TOKEN_EXPIRE_SECONDS: int = Field(300)
    REFRESH_TOKEN_EXPIRE_SECONDS: int = Field(864000)
    REFRESH_COOKIE_PATH: str = Field("/api/auth")
    ADMINS_LIST_RAW: str = Field("[]", alias="ADMINS_LIST")
    ADMIN_EMAIL: str = Field()
    MAIL_FROM_ADDRESS: str = Field()
    MAIL_FROM_NAME: str = Field()
    MAIL_TRANSPORT: str = Field()

    AFFISE_ENABLED: bool = Field()
    AFFISE_API_URL: str = Field()
    AFFISE_API_KEY: str = Field()


    TELEGRAM_BOT_TOKEN: str = Field()
    TELEGRAM_CHAT_ID: str = Field()
    TELEGRAM_LOG_LEVEL: str = Field()

    @property
    def ADB_URL(self) -> str:
        return f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

    def SDB_URL(self) -> str:
        return f"postgresql+psycopg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

    @property
    def ADMINS_LIST(self) -> list[dict[str, Any]]:

        data = json.loads(self.ADMINS_LIST_RAW)
        return data if isinstance(data, list) else []


