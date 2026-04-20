from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


class PinSendRequest(BaseModel):
    email: EmailStr

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: str) -> str:
        return value.lower()


class PinVerifyRequest(PinSendRequest):
    pin: str = Field(min_length=6, max_length=6)

    @field_validator("pin")
    @classmethod
    def digits_only(cls, value: str) -> str:
        if not value.isdigit():
            raise ValueError("PIN must contain 6 digits")
        return value


class AuthUser(BaseModel):
    id: int
    name: str
    email: str
    affise_country: str | None = None
    affise_id: int | None = None
    is_onboarded: bool = False
    is_banned: bool = False
    is_admin: bool = False
    impersonating: bool = False


class JWTClaims(BaseModel):
    model_config = ConfigDict(extra="ignore")

    user_id: int
    session_id: str = Field(alias="sid")
    exp: datetime
    name: str | None = None
    email: str | None = None
    affise_password: str | None = None
    affise_country: str | None = None
    affise_id: int | None = None
    is_onboarded: bool = False
    is_banned: bool = False
    is_admin: bool = False
    impersonating: bool = False

    def to_auth_user(self) -> AuthUser:
        return AuthUser(
            id=self.user_id,
            name=self.name or "",
            email=self.email or "",
            affise_country=self.affise_country,
            affise_id=self.affise_id,
            is_onboarded=bool(self.is_onboarded or self.affise_password),
            is_banned=self.is_banned,
            is_admin=self.is_admin,
            impersonating=self.impersonating,
        )
