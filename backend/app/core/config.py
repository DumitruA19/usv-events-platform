from __future__ import annotations

from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Anchor `.env` to the backend folder regardless of current working directory.
    # Otherwise running from repo root can accidentally load the wrong `.env`.
    model_config = SettingsConfigDict(
        env_file=str(Path(__file__).resolve().parents[2] / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "USV University Events Management Platform"
    env: str = "local"
    integrations_mode: str = "mock"  # "mock" | "real"

    database_url: str = "sqlite:///./data/app.db"

    jwt_secret_key: str = "CHANGE_ME_LOCAL_DEV_ONLY"
    jwt_algorithm: str = "HS256"
    jwt_access_token_expires_minutes: int = 60
    jwt_refresh_token_expires_days: int = 14

    storage_dir: str = "./storage"

    cors_allow_origins: list[str] = ["http://127.0.0.1:5173", "http://localhost:5173"]
    allowed_origins: str = "http://localhost:5173,http://127.0.0.1:5173,http://localhost:3000,http://127.0.0.1:3000"

    # Google OAuth / Calendar (real integrations)
    frontend_base_url: str = "http://localhost:5173"
    oauth_state_secret_key: str = "CHANGE_ME_LOCAL_DEV_ONLY"
    # Preferred: comma-separated allowlist, e.g. "student.usv.ro,usm.ro"
    student_email_domains: str = "student.usv.ro"
    # Back-compat (deprecated): single domain value. If set, it is merged into the allowlist above.
    student_email_domain: str | None = None

    google_client_id: str | None = None
    google_client_secret: str | None = None
    google_redirect_uri: str = "http://localhost:8000/auth/google/callback"
    google_calendar_id: str = "primary"
    default_timezone: str = "Europe/Bucharest"

    # Supabase (optional; keep SERVICE_ROLE_KEY server-side only)
    supabase_url: str | None = None
    supabase_anon_key: str | None = None
    supabase_service_role_key: str | None = None

    # AI / RAG (optional; no external calls by default)
    ai_feature_enabled: bool = False
    ai_provider: str = "disabled"  # "disabled" | "openai" | "azure-openai" | ...
    ai_model: str = "unset"
    ai_api_key: str | None = None
    ai_allow_external_calls: bool = False

    # Groq (optional). Used only when explicitly enabled by AI_FEATURE_ENABLED=true.
    groq_api_key: str | None = None
    groq_model: str = "llama-3.1-8b-instant"
    groq_temperature: float = 0.2
    groq_max_tokens: int = 256

    # Scraper / ingestion (safe defaults)
    scraper_user_agent: str = "usv-events-platform/0.1 (local-dev)"
    scraper_max_pages: int = 25
    scrape_timeout_seconds: int = 12
    scrape_max_text_chars: int = 6000

    # Demo-only auth escape hatch (local only; never for production).
    demo_auth_fallback: bool = False
    demo_admin_password: str | None = None
    demo_organizer_password: str | None = None


settings = Settings()

def _looks_like_placeholder(value: str) -> bool:
    v = (value or "").strip().lower()
    if not v:
        return True
    if "change_me" in v or v in {"unset", "disabled", "none"}:
        return True
    return False


def normalized_database_url() -> str:
    """
    Normalize database URLs so SQLAlchemy uses the installed driver explicitly.

    This keeps local `.env` files compatible with common Supabase examples that
    start with `postgresql://...` while this project installs `psycopg` v3.
    """
    url = settings.database_url.strip()
    if url.startswith("postgresql://"):
        return url.replace("postgresql://", "postgresql+psycopg://", 1)
    if url.startswith("sqlite:///"):
        raw_path = url.split("sqlite:///", 1)[1]
        path = Path(raw_path)
        if not path.is_absolute():
            backend_dir = Path(__file__).resolve().parents[2]
            path = (backend_dir / path).resolve()
            return f"sqlite:///{path.as_posix()}"
    return url


def validate_runtime_config() -> str | None:
    """
    Fail fast with clear messages for misconfigured Supabase/Postgres setups.
    """
    url = normalized_database_url()
    if url.startswith("sqlite:"):
        return None

    missing: list[str] = []
    if not settings.database_url:
        missing.append("DATABASE_URL")
    if settings.supabase_url is None or not str(settings.supabase_url).strip():
        missing.append("SUPABASE_URL")
    if settings.supabase_anon_key is None or not str(settings.supabase_anon_key).strip():
        missing.append("SUPABASE_ANON_KEY")

    if missing:
        return (
            "Missing required environment variables for Supabase/PostgreSQL: "
            + ", ".join(missing)
            + ". Configure `backend/.env` based on `backend/.env.example`."
        )

    # Service role key is optional unless a feature explicitly needs it.
    if settings.supabase_service_role_key and _looks_like_placeholder(str(settings.supabase_service_role_key)):
        return "SUPABASE_SERVICE_ROLE_KEY looks like a placeholder; remove it or set a real value."

    return None


def allowed_student_email_domains() -> list[str]:
    """
    Returns the institutional email domains that are allowed to use Google login.

    Sources (merged):
    - STUDENT_EMAIL_DOMAINS="student.usv.ro,usm.ro"
    - (deprecated) STUDENT_EMAIL_DOMAIN="student.usv.ro"
    """
    out: list[str] = []
    for raw in [settings.student_email_domains, settings.student_email_domain or ""]:
        for part in (raw or "").split(","):
            d = part.strip().lower().lstrip("@")
            if d and d not in out:
                out.append(d)
    return out


def allowed_cors_origins() -> list[str]:
    out: list[str] = []
    for raw in [*settings.cors_allow_origins, settings.allowed_origins]:
        if isinstance(raw, str):
            parts = raw.split(",")
        else:
            parts = [raw]
        for part in parts:
            item = str(part).strip()
            if item and item not in out:
                out.append(item)
    return out
