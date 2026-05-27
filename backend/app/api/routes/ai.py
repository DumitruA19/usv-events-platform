from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from app.auth.deps import get_current_user, require_roles
from app.core.database import get_db
from app.models.enums import RoleName
from app.schemas.ai import ChatRequest, ChatResponse, ScrapeRunRequest, ScrapeRunResponse, ScrapeSourceCreate
from app.ai.chatbot_service import ChatbotService
from app.ai.ingestion_service import IngestionService
from app.services.ai_scrape_service import AIScrapeService

router = APIRouter()


@router.post("/chat", response_model=ChatResponse)
def chat(payload: ChatRequest, db: Session = Depends(get_db), user=Depends(get_current_user)):
    print(f"AI_ROUTE_START chat user_id={getattr(user, 'id', None)}")
    try:
        svc = ChatbotService(db)
        out = svc.ask(user_id=str(user.id), session_id=payload.session_id, message=payload.message)
        db.commit()
        used_groq = str(out.get("provider") or "").lower() == "groq" and str(out.get("status") or "") == "ok"
        print(
            "AI_CHAT_OK "
            f"session_id={out.get('session_id')} used_groq={used_groq} status={out.get('status')} provider={out.get('provider')}"
        )
        return {"reply": out.get("reply") or "", "used_groq": used_groq, "session_id": out.get("session_id")}
    except SQLAlchemyError as e:
        # Common demo failure: migrations not applied on Supabase yet. Do not 500 in the UI.
        db.rollback()
        print(f"AI_CHAT_DB_ERROR detail={type(e).__name__}: {e}")
        return {
            "reply": "Modulul AI nu este initializat in baza de date (migrari lipsa) sau baza este indisponibila.",
            "used_groq": False,
            "session_id": None,
        }
    except Exception as e:
        db.rollback()
        print(f"AI_CHAT_ERROR detail={type(e).__name__}: {e}")
        return {
            "reply": "Asistentul nu este disponibil momentan (eroare interna controlata).",
            "used_groq": False,
            "session_id": None,
        }


@router.post("/ingestion/run")
def ingestion_run(payload: ScrapeRunRequest, db: Session = Depends(get_db), user=Depends(require_roles(RoleName.ADMIN))):
    if not payload.url:
        return {"error": "missing_url"}
    svc = IngestionService(db)
    out = svc.ingest_url(url=str(payload.url), requested_by=int(user.id))
    db.commit()
    return out


@router.get("/ingestion/jobs")
def ingestion_jobs(db: Session = Depends(get_db), user=Depends(require_roles(RoleName.ADMIN))):
    svc = IngestionService(db)
    return svc.list_jobs(limit=50)


@router.post("/scrape/sources")
def add_source(payload: ScrapeSourceCreate, db: Session = Depends(get_db), user=Depends(require_roles(RoleName.ADMIN))):
    svc = AIScrapeService(db)
    src = svc.add_source(user, str(payload.url))
    db.commit()
    return {"id": src.id, "url": src.url, "is_active": src.is_active}


@router.get("/scrape/results")
def list_results(db: Session = Depends(get_db), user=Depends(require_roles(RoleName.ADMIN))):
    print(f"AI_ROUTE_START scrape_results admin_id={getattr(user, 'id', None)}")
    try:
        svc = AIScrapeService(db)
        items = svc.list_results(user)
        out = [
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
        print(f"AI_SCRAPE_RESULTS_OK total={len(out)}")
        # New shape (preferred) + keep backward-compat via frontend adapter.
        return {"items": out, "total": len(out), "message": "OK"}
    except SQLAlchemyError as e:
        db.rollback()
        print(f"AI_SCRAPE_RESULTS_DB_ERROR detail={type(e).__name__}: {e}")
        return {"items": [], "total": 0, "message": "Nu exista rezultate de scraping."}
    except Exception as e:
        db.rollback()
        print(f"AI_SCRAPE_RESULTS_ERROR detail={type(e).__name__}: {e}")
        return {"items": [], "total": 0, "message": "Nu exista rezultate de scraping."}


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
