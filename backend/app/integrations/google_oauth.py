from __future__ import annotations

import urllib.parse

import httpx

from app.core.config import settings


class GoogleOAuth:
    AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
    TOKEN_URL = "https://oauth2.googleapis.com/token"
    USERINFO_URL = "https://openidconnect.googleapis.com/v1/userinfo"

    def __init__(self) -> None:
        if not settings.google_client_id or not settings.google_client_secret:
            raise RuntimeError("Google OAuth is not configured (missing GOOGLE_CLIENT_ID / GOOGLE_CLIENT_SECRET)")

    def build_authorization_url(self, state: str) -> str:
        scope = " ".join(
            [
                "openid",
                "email",
                "profile",
                # We create calendar events for registrations.
                "https://www.googleapis.com/auth/calendar.events",
            ]
        )
        params = {
            "client_id": settings.google_client_id,
            "redirect_uri": settings.google_redirect_uri,
            "response_type": "code",
            "scope": scope,
            "state": state,
            # offline => refresh_token; prompt=consent ensures refresh_token on first connect.
            "access_type": "offline",
            "prompt": "consent",
            # Request granted scopes incrementally (helps if we add more later).
            "include_granted_scopes": "true",
        }
        return f"{self.AUTH_URL}?{urllib.parse.urlencode(params)}"

    def exchange_code(self, code: str) -> dict:
        data = {
            "client_id": settings.google_client_id,
            "client_secret": settings.google_client_secret,
            "code": code,
            "redirect_uri": settings.google_redirect_uri,
            "grant_type": "authorization_code",
        }
        with httpx.Client(timeout=20) as client:
            res = client.post(self.TOKEN_URL, data=data)
            res.raise_for_status()
            return res.json()

    def fetch_userinfo(self, access_token: str) -> dict:
        with httpx.Client(timeout=20) as client:
            res = client.get(self.USERINFO_URL, headers={"Authorization": f"Bearer {access_token}"})
            res.raise_for_status()
            return res.json()

