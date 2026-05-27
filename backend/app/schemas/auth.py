from __future__ import annotations

from pydantic import BaseModel, EmailStr, Field


class LoginRequest(BaseModel):
    # Classic admin/organizer login is email-only.
    email: EmailStr
    password: str


class MockGoogleLoginRequest(BaseModel):
    email: EmailStr


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    role: str
    user: dict


class RefreshRequest(BaseModel):
    refresh_token: str = Field(min_length=10)

