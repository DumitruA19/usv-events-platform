from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import api_router
from app.core.config import allowed_cors_origins, settings
from app.core.database import init_storage_dirs


def create_app() -> FastAPI:
    app = FastAPI(title=settings.app_name)

    cors_origins = allowed_cors_origins()

    app.add_middleware(
        CORSMiddleware,
        allow_origins=cors_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
        allow_headers=["Authorization", "Content-Type", "Accept"],
    )

    # Support both direct API paths (e.g. `/auth/...`) and `/api/...` paths.
    # Some frontend/env setups use `/api` as a prefix.
    app.include_router(api_router)
    app.include_router(api_router, prefix="/api")

    @app.on_event("startup")
    def _startup() -> None:
        init_storage_dirs()

    return app


app = create_app()

