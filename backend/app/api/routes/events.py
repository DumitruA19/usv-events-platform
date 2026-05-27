from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session

from app.auth.deps import get_current_user, get_optional_user, require_roles
from app.core.database import get_db
from app.models.enums import ParticipationMode, RoleName
from app.schemas.events import EventCreate, EventOut, EventUpdate, PagedEvents
from app.schemas.registrations import CheckInRequest, CheckInResponse, ParticipantOut, RegisterResponse, WaitingOut
from app.services.event_service import EventService
from app.services.registration_service import RegistrationService

router = APIRouter()


@router.get("", response_model=PagedEvents)
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
    user=Depends(get_optional_user),
):
    svc = EventService(db)
    kwargs = dict(
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
        statuses=None,
        sort_by=sort_by,
        sort_dir=sort_dir,
    )
    if user and user.role.name in [RoleName.ORGANIZER.value, RoleName.ADMIN.value]:
        items = svc.list_any(**kwargs)
    else:
        items = svc.list_public(**kwargs)

    out = []
    for e in items:
        out.append(
            {
                "id": e.id,
                "title": e.title,
                "start_dt": e.start_dt,
                "end_dt": e.end_dt,
                "location_name": e.location.name if e.location else None,
                "category_name": e.category.name if e.category else None,
                "organizer_name": e.organizer.username if e.organizer else None,
                "status": e.status,
                "participation_mode": e.participation_mode,
                "free_entry": e.free_entry,
                "requires_registration": e.requires_registration,
                "has_qr_code": e.has_qr_code,
            }
        )
    return {"items": out, "total": len(out)}


@router.get("/calendar")
def calendar(db: Session = Depends(get_db)):
    svc = EventService(db)
    items = svc.list_public(
        q=None,
        date_from=None,
        date_to=None,
        category_id=None,
        organizer_id=None,
        location_id=None,
        faculty_department_id=None,
        participation_mode=None,
        free_entry=None,
        requires_registration=None,
        has_qr_code=None,
        filter_operator="AND",
        statuses=None,
        sort_by="date",
        sort_dir="asc",
    )
    return {"items": [{"id": e.id, "title": e.title, "start_dt": e.start_dt, "end_dt": e.end_dt} for e in items]}


@router.get("/{event_id}", response_model=EventOut)
def get_event(event_id: int, db: Session = Depends(get_db)):
    svc = EventService(db)
    e = svc.get(event_id)
    return {
        "id": e.id,
        "title": e.title,
        "description": e.description,
        "start_dt": e.start_dt,
        "end_dt": e.end_dt,
        "location_name": e.location.name if e.location else None,
        "category_name": e.category.name if e.category else None,
        "organizer_name": e.organizer.username if e.organizer else None,
        "status": e.status,
        "participation_mode": e.participation_mode,
        "registration_link": e.registration_link,
        "free_entry": e.free_entry,
        "requires_registration": e.requires_registration,
        "requires_ticket": e.requires_ticket,
        "capacity": e.capacity,
        "has_qr_code": e.has_qr_code,
        "sponsors": [{"name": es.sponsor.name, "logo_path": es.sponsor.logo_path} for es in e.sponsors],
        "materials": [{"id": m.id, "filename": m.filename, "size_bytes": m.size_bytes} for m in e.materials],
    }


@router.post("", response_model=EventOut)
def create_event(payload: EventCreate, db: Session = Depends(get_db), user=Depends(require_roles(RoleName.ORGANIZER))):
    svc = EventService(db)
    e = svc.create(user, payload)
    db.commit()
    return get_event(e.id, db)


@router.put("/{event_id}", response_model=EventOut)
def update_event(event_id: int, payload: EventUpdate, db: Session = Depends(get_db), user=Depends(get_current_user)):
    svc = EventService(db)
    e = svc.update(user, event_id, payload)
    db.commit()
    return get_event(e.id, db)


@router.delete("/{event_id}")
def delete_event(event_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    svc = EventService(db)
    svc.delete(user, event_id)
    db.commit()
    return {"status": "deleted"}


@router.post("/{event_id}/submit-for-approval")
def submit_for_approval(event_id: int, db: Session = Depends(get_db), user=Depends(require_roles(RoleName.ORGANIZER))):
    svc = EventService(db)
    e = svc.submit_for_approval(user, event_id)
    db.commit()
    return {"status": e.status}


@router.post("/{event_id}/approve")
def approve(event_id: int, db: Session = Depends(get_db), user=Depends(require_roles(RoleName.ADMIN))):
    svc = EventService(db)
    e = svc.approve(user, event_id)
    db.commit()
    return {"status": e.status}


@router.post("/{event_id}/reject")
def reject(event_id: int, db: Session = Depends(get_db), user=Depends(require_roles(RoleName.ADMIN))):
    svc = EventService(db)
    e = svc.reject(user, event_id)
    db.commit()
    return {"status": e.status}


@router.get("/{event_id}/ics")
def export_ics(event_id: int, db: Session = Depends(get_db)):
    svc = EventService(db)
    ics = svc.export_ics(event_id)
    return Response(content=ics, media_type="text/calendar")


@router.post("/{event_id}/mock-google-calendar")
def mock_google_calendar(event_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    # Production: no mock calendar writes.
    from app.core.config import settings

    if settings.integrations_mode == "real":
        return {"status": "disabled"}
    svc = EventService(db)
    out = svc.mock_google_calendar(user, event_id)
    db.commit()
    return out


@router.post("/{event_id}/register", response_model=RegisterResponse)
def register(event_id: int, db: Session = Depends(get_db), user=Depends(require_roles(RoleName.STUDENT))):
    svc = RegistrationService(db)
    out = svc.register(user, event_id)
    db.commit()
    return out


@router.delete("/{event_id}/register")
def cancel_registration(event_id: int, db: Session = Depends(get_db), user=Depends(require_roles(RoleName.STUDENT))):
    svc = RegistrationService(db)
    out = svc.cancel(user, event_id)
    db.commit()
    return out


@router.get("/{event_id}/participants", response_model=list[ParticipantOut])
def participants(event_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    svc = RegistrationService(db)
    items = svc.list_participants(user, event_id)
    return [
        {
            "student_id": r.student_id,
            "email": r.student.email if r.student else None,
            "status": r.status,
            "registered_at": r.registered_at,
            "ticket_qr_payload": r.ticket.qr_payload if r.ticket else None,
        }
        for r in items
    ]


@router.get("/{event_id}/waiting-list", response_model=list[WaitingOut])
def waiting_list(event_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    svc = RegistrationService(db)
    items = svc.list_waiting(user, event_id)
    return [
        {"student_id": w.student_id, "email": w.student.email if w.student else None, "position": w.position, "created_at": w.created_at}
        for w in items
    ]


@router.get("/{event_id}/participants/export")
def export_participants(event_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    svc = RegistrationService(db)
    csv_text = svc.export_participants_csv(user, event_id)
    return Response(content=csv_text, media_type="text/csv")


@router.post("/{event_id}/check-in", response_model=CheckInResponse)
def check_in(event_id: int, payload: CheckInRequest, db: Session = Depends(get_db), user=Depends(get_current_user)):
    svc = RegistrationService(db)
    out = svc.check_in(user, event_id, payload.qr_payload)
    db.commit()
    return out

