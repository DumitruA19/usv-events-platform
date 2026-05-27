from __future__ import annotations

from dataclasses import dataclass

from app.core.config import settings
from app.ai.groq_client import GroqClient


@dataclass(frozen=True)
class AIResult:
    content: str
    status: str  # "ok" | "skipped"
    model: str
    provider: str


class AIClient:
    """
    Safe-by-default AI abstraction.

    - Does NOT call external APIs unless BOTH:
      - AI_ALLOW_EXTERNAL_CALLS=true
      - AI_API_KEY is set
    """

    def generate(self, prompt: str) -> AIResult:
        provider = (settings.ai_provider or "disabled").lower()
        model = settings.ai_model

        if not settings.ai_allow_external_calls:
            return AIResult(
                content="AI extern este dezactivat (AI_ALLOW_EXTERNAL_CALLS=false).",
                status="skipped",
                model=model,
                # Keep logs/UI clear regardless of what AI_PROVIDER is set to.
                provider="disabled",
            )

        # Groq (OpenAI-compatible) is implemented in this repo.
        if provider in ("groq", "auto"):
            groq = GroqClient()
            if not groq.is_configured():
                return AIResult(content="AI nu este configurat (lipsește GROQ_API_KEY sau AI_FEATURE_ENABLED=false).", status="skipped", model=settings.groq_model, provider="groq")
            # Ask for a plain text answer (not JSON).
            system = (
                "You are a helpful assistant for the USV Events Platform. "
                "Answer using the provided context. If context is insufficient, say you don't know."
            )
            res = groq.chat_json(system=f'{system} Return ONLY JSON: {{"reply":"..."}}', user=prompt)
            if res.status != "ok":
                return AIResult(content="AI indisponibil momentan.", status="error", model=settings.groq_model, provider="groq")
            try:
                import json

                data = json.loads(res.content)
                content = str(data.get("reply") or "").strip()
            except Exception:
                content = ""
            if not content:
                content = "Nu am putut genera un răspuns."
            return AIResult(content=content, status="ok", model=settings.groq_model, provider="groq")

        # Other providers not implemented.
        return AIResult(
            content="AI_PROVIDER neimplementat. Folosește AI_PROVIDER=groq și setează GROQ_API_KEY.",
            status="skipped",
            model=model,
            provider=provider,
        )

