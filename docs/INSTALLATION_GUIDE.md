# Installation Guide

UI note: the frontend supports Romanian (default) + English, and light/dark themes via header toggles.

## Prerequisites
- Python 3.11+
- Node.js 18+

## Backend
```powershell
cd usv-events-platform\backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python .\scripts\init_local.py
uvicorn app.main:app --reload
```

## Frontend
```powershell
cd usv-events-platform\frontend
npm install
npm run dev
```

## Docker (Later)
See `docs/DEPLOYMENT_NOTES.md` and `docker/`.
