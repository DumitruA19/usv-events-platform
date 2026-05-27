from __future__ import annotations

from dataclasses import dataclass

from app.core.config import settings


@dataclass(frozen=True)
class SupabaseConfig:
    url: str | None
    anon_key: str | None
    service_role_key: str | None

    @property
    def is_configured(self) -> bool:
        return bool(self.url and (self.anon_key or self.service_role_key))

    def auth_headers(self, *, use_service_role: bool = False) -> dict[str, str]:
        """
        Returns HTTP headers suitable for calling Supabase REST endpoints.

        Never use `service_role_key` in frontend code. Keep it backend-only.
        """
        key = self.service_role_key if use_service_role else self.anon_key
        if not self.url or not key:
            return {}
        return {"apikey": key, "Authorization": f"Bearer {key}"}


def get_supabase_config() -> SupabaseConfig:
    return SupabaseConfig(
        url=settings.supabase_url,
        anon_key=settings.supabase_anon_key,
        service_role_key=settings.supabase_service_role_key,
    )

