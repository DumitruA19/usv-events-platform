from __future__ import annotations

from pydantic import BaseModel, EmailStr, Field

from app.models.enums import RoleName


class LoginRequest(BaseModel):
    username: str
    password: str


class MockGoogleLoginRequest(BaseModel):
    email: EmailStr


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    role: RoleName
    user: dict


class RefreshRequest(BaseModel):
    refresh_token: str = Field(min_length=10)

