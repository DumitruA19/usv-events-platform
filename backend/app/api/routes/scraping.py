from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.auth.deps import require_roles
from app.core.database import get_db
from app.models.enums import RoleName
from app.schemas.scraping import ScrapedDraftOut
from app.services.scraping_service import ScrapingService

router = APIRouter()


@router.post("/mock-run", response_model=list[ScrapedDraftOut])
def mock_run(db: Session = Depends(get_db), user=Depends(require_roles(RoleName.ADMIN))):
    # Production: disable mock scraper.
    from app.core.config import settings

    if settings.integrations_mode == "real":
        raise HTTPException(status_code=404, detail="Not found")
    svc = ScrapingService(db)
    items = svc.mock_run(user)
    db.commit()
    return items


@router.get("/drafts", response_model=list[ScrapedDraftOut])
def list_drafts(db: Session = Depends(get_db), user=Depends(require_roles(RoleName.ADMIN))):
    svc = ScrapingService(db)
    return svc.list_drafts(user)


@router.post("/drafts/{draft_id}/approve")
def approve_draft(draft_id: int, db: Session = Depends(get_db), user=Depends(require_roles(RoleName.ADMIN))):
    svc = ScrapingService(db)
    e = svc.approve_draft(user, draft_id)
    db.commit()
    return {"event_id": e.id, "status": e.status}


@router.delete("/drafts/{draft_id}")
def delete_draft(draft_id: int, db: Session = Depends(get_db), user=Depends(require_roles(RoleName.ADMIN))):
    svc = ScrapingService(db)
    svc.delete_draft(user, draft_id)
    db.commit()
    return {"status": "deleted"}

