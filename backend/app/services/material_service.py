from __future__ import annotations

import os
from pathlib import Path

from fastapi import UploadFile
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.enums import RoleName
from app.models.event import EventMaterial
from app.repositories.event_repo import EventRepository
from app.utils.errors import bad_request, forbidden, not_found


class MaterialService:
    def __init__(self, db: Session):
        self.db = db
        self.events = EventRepository(db)

    async def upload(self, user, event_id: int, files: list[UploadFile]) -> list[EventMaterial]:
        e = self.events.get(event_id)
        if not e:
            raise not_found("Event not found")
        if user.role.name != RoleName.ORGANIZER.value or e.organizer_id != user.id:
            raise forbidden("Only the owning organizer can upload materials")

        existing_count = int(
            self.db.scalar(select(func.count()).select_from(EventMaterial).where(EventMaterial.event_id == event_id)) or 0
        )
        if existing_count + len(files) > e.max_material_files:
            raise bad_request(f"Material limit exceeded (max {e.max_material_files} files)")

        max_bytes = e.max_material_mb * 1024 * 1024
        saved: list[EventMaterial] = []
        event_dir = Path(settings.storage_dir) / "materials" / str(event_id)
        event_dir.mkdir(parents=True, exist_ok=True)

        for f in files:
            data = await f.read()
            if len(data) > max_bytes:
                raise bad_request(f"File too large (max {e.max_material_mb} MB)")
            safe_name = os.path.basename(f.filename)
            out_path = event_dir / safe_name
            out_path.write_bytes(data)
            mat = EventMaterial(
                event_id=event_id,
                filename=safe_name,
                content_type=f.content_type or "application/octet-stream",
                size_bytes=len(data),
                stored_path=str(out_path),
            )
            self.db.add(mat)
            self.db.flush()
            saved.append(mat)
        return saved

    def list(self, event_id: int) -> list[EventMaterial]:
        e = self.events.get(event_id)
        if not e:
            raise not_found("Event not found")
        return list(self.db.scalars(select(EventMaterial).where(EventMaterial.event_id == event_id).order_by(EventMaterial.uploaded_at.desc())))

    def delete(self, user, material_id: int) -> None:
        mat = self.db.get(EventMaterial, material_id)
        if not mat:
            raise not_found("Material not found")
        e = self.events.get(mat.event_id)
        if not e:
            raise not_found("Event not found")
        if user.role.name == RoleName.ORGANIZER.value and e.organizer_id != user.id:
            raise forbidden("Organizers can delete only their own materials")
        if user.role.name not in [RoleName.ORGANIZER.value, RoleName.ADMIN.value]:
            raise forbidden("Not allowed")
        try:
            Path(mat.stored_path).unlink(missing_ok=True)
        except Exception:
            pass
        self.db.delete(mat)
