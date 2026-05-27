from __future__ import annotations

import json
from dataclasses import dataclass

import httpx

from app.core.config import settings


@dataclass(frozen=True)
class GroqChatResult:
    content: str
    status: str  # "ok" | "skipped" | "error"
    model: str


class GroqClient:
    """
    Minimal Groq client (OpenAI-compatible endpoint).

    Important: this is a fallback layer. Deterministic logic should be preferred.
    """

    API_URL = "https://api.groq.com/openai/v1/chat/completions"

    def is_configured(self) -> bool:
        return bool(settings.groq_api_key and settings.ai_feature_enabled)

    def chat_json(self, *, system: str, user: str) -> GroqChatResult:
        if not self.is_configured():
            return GroqChatResult(content="[]", status="skipped", model=settings.groq_model)

        headers = {"Authorization": f"Bearer {settings.groq_api_key}"}
        payload = {
            "model": settings.groq_model,
            "temperature": float(settings.groq_temperature),
            "max_tokens": int(settings.groq_max_tokens),
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
        }

        try:
            with httpx.Client(timeout=20) as client:
                res = client.post(self.API_URL, headers=headers, json=payload)
                res.raise_for_status()
                data = res.json()
            content = str((data.get("choices") or [{}])[0].get("message", {}).get("content") or "").strip()
            if not content:
                return GroqChatResult(content="[]", status="error", model=settings.groq_model)
            # Validate that it is JSON (still return raw content for caller parsing).
            json.loads(content)
            return GroqChatResult(content=content, status="ok", model=settings.groq_model)
        except Exception:
            return GroqChatResult(content="[]", status="error", model=settings.groq_model)
