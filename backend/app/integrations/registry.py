from __future__ import annotations

from functools import lru_cache

from app.core.config import settings
from app.integrations.mocks import (
    MockEmailSender,
    MockGoogleCalendar,
    MockGoogleOAuth,
    MockNotificationSender,
    MockPDFReportGenerator,
    MockQRCodeGenerator,
    MockRecommendationEngine,
    MockScraperProvider,
    MockSentimentAnalyzer,
)


@lru_cache(maxsize=1)
def get_integrations():
    if settings.integrations_mode == "real":
        # Avoid importing real adapters unless explicitly enabled.
        from app.integrations.google_calendar import GoogleCalendar
        from app.integrations.google_oauth import GoogleOAuth

        return {
            "google_oauth": GoogleOAuth(),
            "google_calendar": GoogleCalendar(),
            "email": MockEmailSender(),  # keep mock for now
            "notification": MockNotificationSender(),
            "qr": MockQRCodeGenerator(),
            "pdf": MockPDFReportGenerator(),
            "sentiment": MockSentimentAnalyzer(),
            "reco": MockRecommendationEngine(),
            "scraper": MockScraperProvider(),
        }

    # Default: mocks (local dev without credentials)
    return {
        "google_oauth": MockGoogleOAuth(),
        "google_calendar": MockGoogleCalendar(),
        "email": MockEmailSender(),
        "notification": MockNotificationSender(),
        "qr": MockQRCodeGenerator(),
        "pdf": MockPDFReportGenerator(),
        "sentiment": MockSentimentAnalyzer(),
        "reco": MockRecommendationEngine(),
        "scraper": MockScraperProvider(),
    }
