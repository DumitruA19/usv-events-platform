from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.auth.deps import require_roles
from app.core.database import get_db
from app.models.enums import ParticipationMode, RoleName
from app.schemas.admin import EventCancelRequest, EventRejectRequest, OrganizerCreate, OrganizerUpdate, UserOut, UserUpdate
from app.services.admin_service import AdminService

router = APIRouter()


@router.get("/users", response_model=list[UserOut])
def list_users(db: Session = Depends(get_db), user=Depends(require_roles(RoleName.ADMIN))):
    svc = AdminService(db)
    items = svc.list_users(user)
    return [{"id": u.id, "email": u.email, "username": u.username, "role": u.role.name, "is_active": u.is_active} for u in items]


@router.patch("/users/{user_id}", response_model=UserOut)
def update_user(user_id: int, payload: UserUpdate, db: Session = Depends(get_db), user=Depends(require_roles(RoleName.ADMIN))):
    svc = AdminService(db)
    u = svc.update_user(user, user_id, role=payload.role, is_active=payload.is_active)
    db.commit()
    return {"id": u.id, "email": u.email, "username": u.username, "role": u.role.name, "is_active": u.is_active}


@router.post("/organizers", response_model=UserOut)
def create_organizer(payload: OrganizerCreate, db: Session = Depends(get_db), user=Depends(require_roles(RoleName.ADMIN))):
    svc = AdminService(db)
    u = svc.create_organizer(user, payload.username, payload.password, payload.display_name, payload.faculty_department_id)
    db.commit()
    return {"id": u.id, "email": u.email, "username": u.username, "role": u.role.name, "is_active": u.is_active}


@router.put("/organizers/{organizer_id}", response_model=UserOut)
def update_organizer(
    organizer_id: int, payload: OrganizerUpdate, db: Session = Depends(get_db), user=Depends(require_roles(RoleName.ADMIN))
):
    svc = AdminService(db)
    u = svc.update_organizer(user, organizer_id, **payload.model_dump(exclude_unset=True))
    db.commit()
    return {"id": u.id, "email": u.email, "username": u.username, "role": u.role.name, "is_active": u.is_active}


@router.delete("/organizers/{organizer_id}")
def delete_organizer(organizer_id: int, db: Session = Depends(get_db), user=Depends(require_roles(RoleName.ADMIN))):
    svc = AdminService(db)
    svc.deactivate_organizer(user, organizer_id)
    db.commit()
    return {"status": "deactivated"}


@router.get("/events/pending")
def pending_events(db: Session = Depends(get_db), user=Depends(require_roles(RoleName.ADMIN))):
    svc = AdminService(db)
    items = svc.pending_events(user)
    return {"items": [{"id": e.id, "title": e.title, "organizer_id": e.organizer_id, "start_dt": e.start_dt, "status": e.status} for e in items]}


@router.get("/events")
def list_events(
    q: str | None = None,
    date_from: datetime | None = None,
    date_to: datetime | None = None,
    category_id: int | None = None,
    organizer_id: int | None = None,
    location_id: int | None = None,
    faculty_department_id: int | None = None,
    participation_mode: ParticipationMode | None = None,
    free_entry: bool | None = None,
    requires_registration: bool | None = None,
    has_qr_code: bool | None = None,
    filter_operator: str = "AND",
    sort_by: str = "date",
    sort_dir: str = "asc",
    db: Session = Depends(get_db),
    user=Depends(require_roles(RoleName.ADMIN)),
):
    svc = AdminService(db)
    items = svc.list_events(
        user,
        q=q,
        date_from=date_from,
        date_to=date_to,
        category_id=category_id,
        organizer_id=organizer_id,
        location_id=location_id,
        faculty_department_id=faculty_department_id,
        participation_mode=participation_mode,
        free_entry=free_entry,
        requires_registration=requires_registration,
        has_qr_code=has_qr_code,
        filter_operator=filter_operator,
        sort_by=sort_by,
        sort_dir=sort_dir,
    )
    return {
        "items": [
            {
                "id": e.id,
                "title": e.title,
                "organizer_id": e.organizer_id,
                "start_dt": e.start_dt,
                "end_dt": e.end_dt,
                "status": e.status,
            }
            for e in items
        ],
        "total": len(items),
    }


@router.post("/events/{event_id}/reject")
def reject_event(event_id: int, payload: EventRejectRequest, db: Session = Depends(get_db), user=Depends(require_roles(RoleName.ADMIN))):
    svc = AdminService(db)
    e = svc.reject_event(user, event_id, reason=payload.reason)
    db.commit()
    return {"id": e.id, "status": e.status}


@router.post("/events/{event_id}/cancel")
def cancel_event(event_id: int, payload: EventCancelRequest, db: Session = Depends(get_db), user=Depends(require_roles(RoleName.ADMIN))):
    svc = AdminService(db)
    e = svc.cancel_event(user, event_id, reason=payload.reason)
    db.commit()
    return {"id": e.id, "status": e.status}


@router.get("/reports/events-per-month")
def report_events_per_month(db: Session = Depends(get_db), user=Depends(require_roles(RoleName.ADMIN))):
    svc = AdminService(db)
    return {"items": svc.report_events_per_month(user)}


@router.get("/reports/participation")
def report_participation(db: Session = Depends(get_db), user=Depends(require_roles(RoleName.ADMIN))):
    svc = AdminService(db)
    return {"items": svc.report_participation(user)}


@router.get("/reports/by-organizer")
def report_by_organizer(db: Session = Depends(get_db), user=Depends(require_roles(RoleName.ADMIN))):
    svc = AdminService(db)
    return {"items": svc.report_by_organizer(user)}


@router.get("/reports/export-pdf")
def export_pdf(db: Session = Depends(get_db), user=Depends(require_roles(RoleName.ADMIN))):
    svc = AdminService(db)
    out = svc.export_reports_pdf(user)
    db.commit()
    return out

