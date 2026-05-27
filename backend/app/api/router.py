from __future__ import annotations

from fastapi import APIRouter

from app.api.routes import admin, ai, auth, events, feedback, materials, notifications, scraping
from app.api.routes import students

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(events.router, prefix="/events", tags=["events"])
api_router.include_router(feedback.router, prefix="/events", tags=["feedback"])
api_router.include_router(materials.router, prefix="", tags=["materials"])
api_router.include_router(admin.router, prefix="/admin", tags=["admin"])
api_router.include_router(notifications.router, prefix="/notifications", tags=["notifications"])
api_router.include_router(scraping.router, prefix="/scraping", tags=["scraping"])
api_router.include_router(students.router, prefix="/students", tags=["students"])
api_router.include_router(ai.router, prefix="/ai", tags=["ai"])
