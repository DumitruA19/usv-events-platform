# Database Schema

UI note: the frontend supports Romanian (default) + English, and light/dark themes via header toggles.

Database: SQLite by default (`backend/data/app.db`).

Core tables:
- `roles`, `users`, `student_profiles`, `organizer_profiles`
- `event_categories`, `faculty_departments`, `locations`
- `events`, `sponsors`, `event_sponsors`, `event_materials`
- `event_registrations`, `waiting_list_entries`, `tickets`
- `feedback`, `favorite_events`
- `notifications`, `reminders`, `reports`, `audit_logs`
- `scraped_event_drafts`

Enums:
- Event status: `DRAFT`, `PENDING_APPROVAL`, `APPROVED`, `REJECTED`, `PUBLISHED`, `CANCELLED`, `ARCHIVED`
- Registration status: `REGISTERED`, `CANCELLED`, `WAITING_LIST`, `CHECKED_IN`
- Roles: `STUDENT`, `ORGANIZER`, `ADMIN`
