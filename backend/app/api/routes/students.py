from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.auth.deps import require_roles
from app.core.database import get_db
from app.models.enums import RoleName
from app.services.student_service import StudentService

router = APIRouter()


@router.get("/me/registrations")
def my_registrations(db: Session = Depends(get_db), user=Depends(require_roles(RoleName.STUDENT))):
    svc = StudentService(db)
    return {"items": svc.my_registrations(user)}


@router.get("/me/recommendations")
def recommendations(db: Session = Depends(get_db), user=Depends(require_roles(RoleName.STUDENT))):
    svc = StudentService(db)
    return {"items": svc.recommendations(user)}

