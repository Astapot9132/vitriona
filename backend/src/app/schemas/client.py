from typing import Any

from pydantic import BaseModel, Field, field_validator


class OnboardingCompleteRequest(BaseModel):
    country: str = Field(min_length=2, max_length=2)
    custom_fields: dict[str, Any]

    @field_validator("country")
    @classmethod
    def normalize_country(cls, value: str) -> str:
        if not value.isalpha() or len(value) != 2:
            raise ValueError("Country must be a 2-letter code")
        return value.upper()


class UpdateCountryRequest(BaseModel):
    country: str = Field(min_length=2, max_length=2)

    @field_validator("country")
    @classmethod
    def normalize_country(cls, value: str) -> str:
        if not value.isalpha() or len(value) != 2:
            raise ValueError("Country must be a 2-letter code")
        return value.upper()


class ShowcaseCreateRequest(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    platform_main: str = Field(min_length=1, max_length=255)
    platform_sub: str | None = Field(default=None, max_length=255)
    url: str = Field(min_length=1, max_length=255)


class ShowcaseUpdateRequest(BaseModel):
    name: str | None = Field(default=None, max_length=255)
    platform_main: str | None = Field(default=None, max_length=255)
    platform_sub: str | None = Field(default=None, max_length=255)
    url: str | None = Field(default=None, max_length=255)
    status: str | None = None
    config: dict[str, Any] | None = None

    @field_validator("status")
    @classmethod
    def validate_status(cls, value: str | None) -> str | None:
        if value is None:
            return value
        if value not in {"draft", "published"}:
            raise ValueError("Invalid status")
        return value


class DomainCreateRequest(BaseModel):
    system_domain: str = Field(min_length=1, max_length=255)
    webmaster_domain: str = Field(min_length=1, max_length=255)
