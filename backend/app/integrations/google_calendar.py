from __future__ import annotations

import httpx

from app.core.config import settings


class GoogleCalendar:
    TOKEN_URL = "https://oauth2.googleapis.com/token"
    API_BASE = "https://www.googleapis.com/calendar/v3"

    def __init__(self) -> None:
        if not settings.google_client_id or not settings.google_client_secret:
            raise RuntimeError("Google Calendar is not configured (missing GOOGLE_CLIENT_ID / GOOGLE_CLIENT_SECRET)")

    def _refresh_access_token(self, refresh_token: str) -> str:
        data = {
            "client_id": settings.google_client_id,
            "client_secret": settings.google_client_secret,
            "refresh_token": refresh_token,
            "grant_type": "refresh_token",
        }
        with httpx.Client(timeout=20) as client:
            res = client.post(self.TOKEN_URL, data=data)
            res.raise_for_status()
            payload = res.json()
            access_token = payload.get("access_token")
            if not access_token:
                raise RuntimeError("Google token refresh response missing access_token")
            return str(access_token)

    def create_event(
        self,
        refresh_token: str,
        *,
        calendar_id: str,
        title: str,
        start_dt,
        end_dt,
        timezone: str,
    ) -> dict:
        access_token = self._refresh_access_token(refresh_token)
        url = f"{self.API_BASE}/calendars/{calendar_id}/events"
        body = {
            "summary": title,
            "start": {"dateTime": start_dt.isoformat(), "timeZone": timezone},
            "end": {"dateTime": end_dt.isoformat(), "timeZone": timezone},
        }
        with httpx.Client(timeout=20) as client:
            res = client.post(url, headers={"Authorization": f"Bearer {access_token}"}, json=body)
            res.raise_for_status()
            return res.json()

    def delete_event(self, refresh_token: str, *, calendar_id: str, provider_event_id: str) -> None:
        access_token = self._refresh_access_token(refresh_token)
        url = f"{self.API_BASE}/calendars/{calendar_id}/events/{provider_event_id}"
        with httpx.Client(timeout=20) as client:
            res = client.delete(url, headers={"Authorization": f"Bearer {access_token}"})
            # 404 can happen if the user deleted the event manually; treat as already deleted.
            if res.status_code in (200, 204, 404):
                return
            res.raise_for_status()

