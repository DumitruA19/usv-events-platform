from __future__ import annotations

from datetime import datetime, timedelta, timezone

from jose import jwt

from app.core.config import settings


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def create_access_token(subject: str, role: str) -> str:
    expire = _utcnow() + timedelta(minutes=settings.jwt_access_token_expires_minutes)
    to_encode = {"sub": subject, "role": role, "type": "access", "exp": expire}
    return jwt.encode(to_encode, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def create_refresh_token(subject: str, role: str) -> str:
    expire = _utcnow() + timedelta(days=settings.jwt_refresh_token_expires_days)
    to_encode = {"sub": subject, "role": role, "type": "refresh", "exp": expire}
    return jwt.encode(to_encode, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def decode_token(token: str) -> dict:
    return jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])

