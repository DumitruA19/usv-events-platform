# Application Documentation

UI note: the frontend supports Romanian (default) + English, and light/dark themes via header toggles.

This repository implements the **USV University Events Management Platform** with a clean 3‑layer architecture:
- Presentation: React + Vite + Tailwind (`frontend/`)
- Application/Business: FastAPI services and REST API (`backend/app/`)
- Data Access: SQLAlchemy + SQLite + Alembic (`backend/app/models/`, `backend/alembic/`)

All external integrations are implemented via **replaceable adapters with mock implementations** for local development.
