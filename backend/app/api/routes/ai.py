from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.auth.deps import get_current_user, require_roles
from app.core.database import get_db
from app.models.enums import RoleName
from app.schemas.ai import ChatRequest, ChatResponse, ScrapeRunRequest, ScrapeRunResponse, ScrapeSourceCreate
from app.services.ai_scrape_service import AIScrapeService
from app.services.assistant_service import AssistantService

router = APIRouter()


@router.post("/chat", response_model=ChatResponse)
def chat(payload: ChatRequest, db: Session = Depends(get_db), user=Depends(get_current_user)):
    svc = AssistantService(db)
    out = svc.chat(user=user, message=payload.message, page=payload.page, history=payload.history)
    return out


@router.post("/scrape/sources")
def add_source(payload: ScrapeSourceCreate, db: Session = Depends(get_db), user=Depends(require_roles(RoleName.ADMIN))):
    svc = AIScrapeService(db)
    src = svc.add_source(user, str(payload.url))
    db.commit()
    return {"id": src.id, "url": src.url, "is_active": src.is_active}


@router.get("/scrape/results")
def list_results(db: Session = Depends(get_db), user=Depends(require_roles(RoleName.ADMIN))):
    svc = AIScrapeService(db)
    items = svc.list_results(user)
    return [
        {
            "id": d.id,
            "source": d.source,
            "status": d.status,
            "source_url": d.source_url,
            "image_url": d.image_url,
            "rejection_reason": d.rejection_reason,
            "title": d.title,
            "start_dt": d.start_dt,
            "end_dt": d.end_dt,
            "location_text": d.location_text,
            "category_text": d.category_text,
        }
        for d in items
    ]


@router.post("/scrape/run", response_model=ScrapeRunResponse)
def run(payload: ScrapeRunRequest, db: Session = Depends(get_db), user=Depends(require_roles(RoleName.ADMIN))):
    svc = AIScrapeService(db)
    stats = svc.run(user, url=str(payload.url) if payload.url else None)
    db.commit()
    return {"created": stats.created, "duplicates": stats.duplicates, "errors": stats.errors}


@router.post("/scrape/results/{draft_id}/approve")
def approve(draft_id: int, db: Session = Depends(get_db), user=Depends(require_roles(RoleName.ADMIN))):
    svc = AIScrapeService(db)
    event_id = svc.approve(user, draft_id)
    db.commit()
    return {"event_id": event_id}


@router.post("/scrape/results/{draft_id}/reject")
def reject(draft_id: int, db: Session = Depends(get_db), user=Depends(require_roles(RoleName.ADMIN))):
    svc = AIScrapeService(db)
    svc.reject(user, draft_id)
    db.commit()
    return {"status": "rejected"}
