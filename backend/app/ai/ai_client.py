from __future__ import annotations

from dataclasses import dataclass

from app.core.config import settings


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
        _ = prompt
        provider = settings.ai_provider
        model = settings.ai_model

        if not settings.ai_api_key or provider == "disabled" or not settings.ai_allow_external_calls:
            return AIResult(
                content=(
                    "AI is not configured for external calls.\n\n"
                    "Set backend env vars:\n"
                    "- AI_PROVIDER (e.g. openai)\n"
                    "- AI_MODEL\n"
                    "- AI_API_KEY\n"
                    "- AI_ALLOW_EXTERNAL_CALLS=true\n"
                    "Then implement the provider adapter in app/ai/ai_client.py."
                ),
                status="skipped",
                model=model,
                provider=provider,
            )

        # Intentionally not implemented: external network calls are out of scope by default.
        return AIResult(
            content="AI external calls are enabled, but no provider adapter is implemented yet.",
            status="skipped",
            model=model,
            provider=provider,
        )

