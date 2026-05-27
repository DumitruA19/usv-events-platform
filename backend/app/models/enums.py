from __future__ import annotations

import enum


class RoleName(str, enum.Enum):
    STUDENT = "STUDENT"
    ORGANIZER = "ORGANIZER"
    ADMIN = "ADMIN"


class EventStatus(str, enum.Enum):
    DRAFT = "DRAFT"
    PENDING_APPROVAL = "PENDING_APPROVAL"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    PUBLISHED = "PUBLISHED"
    CANCELLED = "CANCELLED"
    ARCHIVED = "ARCHIVED"


class ParticipationMode(str, enum.Enum):
    PHYSICAL = "PHYSICAL"
    ONLINE = "ONLINE"
    HYBRID = "HYBRID"


class RegistrationStatus(str, enum.Enum):
    REGISTERED = "REGISTERED"
    CANCELLED = "CANCELLED"
    WAITING_LIST = "WAITING_LIST"
    CHECKED_IN = "CHECKED_IN"


class ScrapedDraftStatus(str, enum.Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    DUPLICATE = "DUPLICATE"

