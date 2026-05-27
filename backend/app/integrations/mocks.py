from __future__ import annotations

import json
import re
from datetime import datetime, timedelta, timezone
from pathlib import Path

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

from app.core.config import allowed_student_email_domains, settings
from app.integrations.interfaces import (
    EmailSenderAdapter,
    GoogleCalendarAdapter,
    GoogleOAuthAdapter,
    NotificationSenderAdapter,
    OAuthUserInfo,
    PDFReportGeneratorAdapter,
    QRCodeGeneratorAdapter,
    RecommendationEngineAdapter,
    ScraperProviderAdapter,
    SentimentAnalyzerAdapter,
)


class MockGoogleOAuth(GoogleOAuthAdapter):
    def mock_login(self, email: str) -> OAuthUserInfo:
        email = (email or "").strip().lower()
        domains = allowed_student_email_domains()
        if domains and not any(email.endswith("@" + d) for d in domains):
            raise ValueError("Only institutional emails are allowed")
        name = email.split("@", 1)[0].replace(".", " ").title()
        return OAuthUserInfo(email=email, full_name=name)

    def build_authorization_url(self, state: str) -> str:
        # For local dev, we keep the mock login flow separate from real OAuth.
        _ = state
        raise NotImplementedError("MockGoogleOAuth does not support real OAuth flow")

    def exchange_code(self, code: str) -> dict:
        _ = code
        raise NotImplementedError("MockGoogleOAuth does not support real OAuth flow")

    def fetch_userinfo(self, access_token: str) -> dict:
        _ = access_token
        raise NotImplementedError("MockGoogleOAuth does not support real OAuth flow")


class MockGoogleCalendar(GoogleCalendarAdapter):
    def mock_add_event(self, user_id: int, event_id: int, title: str, start_dt: datetime, end_dt: datetime) -> dict:
        return {
            "provider": "mock-google-calendar",
            "user_id": user_id,
            "event_id": event_id,
            "title": title,
            "start_dt": start_dt.isoformat(),
            "end_dt": end_dt.isoformat(),
            "status": "added",
        }

    def create_event(
        self,
        refresh_token: str,
        *,
        calendar_id: str,
        title: str,
        start_dt: datetime,
        end_dt: datetime,
        timezone: str,
    ) -> dict:
        # Return a consistent shape with what the real Calendar API returns (at least "id").
        _ = refresh_token
        _ = calendar_id
        _ = timezone
        return {"id": f"mock-{int(start_dt.timestamp())}", "summary": title, "start": {"dateTime": start_dt.isoformat()}, "end": {"dateTime": end_dt.isoformat()}}

    def delete_event(self, refresh_token: str, *, calendar_id: str, provider_event_id: str) -> None:
        _ = refresh_token
        _ = calendar_id
        _ = provider_event_id
        return None


class MockEmailSender(EmailSenderAdapter):
    def send(self, to_email: str, subject: str, body: str) -> dict:
        return {"provider": "mock-email", "to": to_email, "subject": subject, "body_preview": body[:120]}


class MockNotificationSender(NotificationSenderAdapter):
    def send(self, user_id: int, type: str, payload: dict) -> dict:
        return {"provider": "mock-notification", "user_id": user_id, "type": type, "payload": payload}


class MockQRCodeGenerator(QRCodeGeneratorAdapter):
    def build_payload(self, kind: str, entity_id: int, salt: str | None = None) -> str:
        s = salt or "local"
        return f"usv-events:{kind}:{entity_id}:{s}"


class MockPDFReportGenerator(PDFReportGeneratorAdapter):
    def generate(self, title: str, lines: list[str], output_path: str) -> str:
        out = Path(output_path)
        out.parent.mkdir(parents=True, exist_ok=True)

        c = canvas.Canvas(str(out), pagesize=A4)
        width, height = A4
        y = height - 60
        c.setFont("Helvetica-Bold", 14)
        c.drawString(40, y, title)
        y -= 28
        c.setFont("Helvetica", 10)
        for line in lines:
            if y < 60:
                c.showPage()
                y = height - 60
                c.setFont("Helvetica", 10)
            c.drawString(40, y, line[:120])
            y -= 14
        c.save()
        return str(out)


class MockSentimentAnalyzer(SentimentAnalyzerAdapter):
    POS = {"great", "good", "excellent", "amazing", "helpful", "love", "enjoyed", "nice"}
    NEG = {"bad", "terrible", "boring", "awful", "hate", "waste", "poor", "late"}

    def analyze(self, text: str | None) -> str:
        if not text:
            return "NEUTRAL"
        t = re.findall(r"[a-z]+", text.lower())
        score = sum(1 for w in t if w in self.POS) - sum(1 for w in t if w in self.NEG)
        if score >= 2:
            return "POSITIVE"
        if score <= -2:
            return "NEGATIVE"
        return "NEUTRAL"


class MockRecommendationEngine(RecommendationEngineAdapter):
    def __init__(self):
        self._store_path = Path(settings.storage_dir) / "mock-reco-store.json"
        self._store_path.parent.mkdir(parents=True, exist_ok=True)

    def _load(self) -> dict:
        if not self._store_path.exists():
            return {}
        try:
            return json.loads(self._store_path.read_text(encoding="utf-8"))
        except Exception:
            return {}

    def _save(self, data: dict) -> None:
        self._store_path.write_text(json.dumps(data, ensure_ascii=True, indent=2), encoding="utf-8")

    def record_interest(self, student_id: int, category_id: int) -> None:
        data = self._load()
        key = str(student_id)
        counts = data.get(key, {})
        counts[str(category_id)] = int(counts.get(str(category_id), 0)) + 1
        data[key] = counts
        self._save(data)

    def recommend_event_ids(self, student_id: int, max_items: int = 5) -> list[int]:
        # Service layer maps these to concrete events; here we return empty by default.
        _ = student_id
        _ = max_items
        return []


class MockScraperProvider(ScraperProviderAdapter):
    def run_mock(self) -> list[dict]:
        # Scraper-ready interface: returns event-like dicts without hitting the network.
        now = datetime.now(timezone.utc)
        return [
            {
                "source": "mock-local-html",
                "title": "Public Lecture: AI in Education",
                "description": "Sample scraped event from local HTML parser (mock).",
                "start_dt": (now + timedelta(days=10)).isoformat(),
                "end_dt": (now + timedelta(days=10, hours=2)).isoformat(),
                "location": "USV - Auditorium A",
                "category": "Lecture",
            },
            {
                "source": "mock-local-html",
                "title": "Career Fair (Mock Discovery)",
                "description": "Another mock discovered draft.",
                "start_dt": (now + timedelta(days=15)).isoformat(),
                "end_dt": (now + timedelta(days=15, hours=5)).isoformat(),
                "location": "USV Campus",
                "category": "Career",
            },
        ]
