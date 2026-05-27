# Architecture

UI note: the frontend supports Romanian (default) + English, and light/dark themes via header toggles.

## Layers

### Presentation Layer (`frontend/`)
- React + Vite + Tailwind
- React Router for navigation
- Axios client in `frontend/src/api/http.ts`
- Auth state stored locally in `frontend/src/store/auth.tsx`

### Application / Business Layer (`backend/app/`)
- FastAPI routers in `backend/app/api/routes/`
- Service classes in `backend/app/services/` implement business rules
- Pydantic schemas in `backend/app/schemas/`
- RBAC dependencies in `backend/app/auth/`

### Data Access Layer (`backend/app/models/`, `backend/app/repositories/`)
- SQLAlchemy models
- Repository pattern to isolate persistence
- Alembic for migrations
- Seed data script `backend/scripts/seed.py`

## Mock Integration Strategy

All integrations are expressed as interfaces in `backend/app/integrations/` and wired to mock implementations:
- Mock Google OAuth: validates `@student.usv.ro` and creates/logs-in a student
- Mock Google Calendar: accepts an event “add” call and records a local notification
- Mock Email: stores “sent emails” in the database as notifications/audit logs
- QR generator: creates deterministic QR payload strings
- PDF report generator: creates a local PDF file using `reportlab`
- Sentiment analyzer: simple lexicon scoring
- Recommendation engine: category-based ranking from favorites/registrations
- Scraper provider: reads sample local HTML and produces event-like drafts
