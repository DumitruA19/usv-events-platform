from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Protocol


@dataclass(frozen=True)
class OAuthUserInfo:
    email: str
    full_name: str | None = None


class GoogleOAuthAdapter(Protocol):
    def mock_login(self, email: str) -> OAuthUserInfo: ...

    # Real OAuth2 (authorization code) flow helpers.
    def build_authorization_url(self, state: str) -> str: ...

    def exchange_code(self, code: str) -> dict: ...

    def fetch_userinfo(self, access_token: str) -> dict: ...


class GoogleCalendarAdapter(Protocol):
    def mock_add_event(self, user_id: int, event_id: int, title: str, start_dt: datetime, end_dt: datetime) -> dict: ...

    def create_event(self, refresh_token: str, *, calendar_id: str, title: str, start_dt: datetime, end_dt: datetime, timezone: str) -> dict: ...

    def delete_event(self, refresh_token: str, *, calendar_id: str, provider_event_id: str) -> None: ...


class EmailSenderAdapter(Protocol):
    def send(self, to_email: str, subject: str, body: str) -> dict: ...


class NotificationSenderAdapter(Protocol):
    def send(self, user_id: int, type: str, payload: dict) -> dict: ...


class QRCodeGeneratorAdapter(Protocol):
    def build_payload(self, kind: str, entity_id: int, salt: str | None = None) -> str: ...


class PDFReportGeneratorAdapter(Protocol):
    def generate(self, title: str, lines: list[str], output_path: str) -> str: ...


class SentimentAnalyzerAdapter(Protocol):
    def analyze(self, text: str | None) -> str: ...


class RecommendationEngineAdapter(Protocol):
    def recommend_event_ids(self, student_id: int, max_items: int = 5) -> list[int]: ...


class ScraperProviderAdapter(Protocol):
    def run_mock(self) -> list[dict]: ...
