from __future__ import annotations

from fastapi import APIRouter, Depends, File, UploadFile
from sqlalchemy.orm import Session

from app.auth.deps import get_current_user
from app.core.database import get_db
from app.services.material_service import MaterialService

router = APIRouter()


@router.post("/events/{event_id}/materials")
async def upload_materials(
    event_id: int,
    files: list[UploadFile] = File(...),
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    svc = MaterialService(db)
    saved = await svc.upload(user, event_id, files)
    db.commit()
    return {"items": [{"id": m.id, "filename": m.filename, "size_bytes": m.size_bytes} for m in saved]}


@router.get("/events/{event_id}/materials")
def list_materials(event_id: int, db: Session = Depends(get_db)):
    svc = MaterialService(db)
    items = svc.list(event_id)
    return {"items": [{"id": m.id, "filename": m.filename, "size_bytes": m.size_bytes} for m in items]}


@router.delete("/materials/{material_id}")
def delete_material(material_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    svc = MaterialService(db)
    svc.delete(user, material_id)
    db.commit()
    return {"status": "deleted"}

