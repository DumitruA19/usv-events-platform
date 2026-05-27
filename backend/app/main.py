from __future__ import annotations

from fastapi import FastAPI
from fastapi import Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import JSONResponse

from app.api.router import api_router
from app.core.config import allowed_cors_origins, settings, validate_runtime_config
from app.core.database import init_storage_dirs


def create_app() -> FastAPI:
    app = FastAPI(title=settings.app_name)

    app.state.startup_error = None

    # CORS should wrap as early as possible so even error responses include headers.
    cors_origins = allowed_cors_origins()
    app.add_middleware(
        CORSMiddleware,
        allow_origins=cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.middleware("http")
    async def _block_on_startup_error(request: Request, call_next):
        err = getattr(app.state, "startup_error", None)
        if err and request.url.path not in {"/healthz", "/docs", "/openapi.json"}:
            return JSONResponse({"error": "CONFIG_ERROR", "message": err}, status_code=503)
        return await call_next(request)

    @app.get("/healthz")
    def _healthz():
        err = getattr(app.state, "startup_error", None)
        if err:
            return {"ok": False, "error": err}
        return {"ok": True}

    # Support both direct API paths (e.g. `/auth/...`) and `/api/...` paths.
    # Some frontend/env setups use `/api` as a prefix.
    app.include_router(api_router)
    app.include_router(api_router, prefix="/api")

    @app.on_event("startup")
    def _startup() -> None:
        err = validate_runtime_config()
        if err:
            app.state.startup_error = err
            return
        init_storage_dirs()

    return app


app = create_app()

