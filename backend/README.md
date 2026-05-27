# Backend (FastAPI)

## Run
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python .\scripts\init_local.py
uvicorn app.main:app --reload
```

## Notes
- SQLite by default (`DATABASE_URL`).
- All integrations are mocked by default (OAuth, calendar, email, notifications, QR, PDF, sentiment, recommendations, scraper).
- Frontend supports Romanian/English UI and light/dark themes (client-side toggles).

## Troubleshooting
- If you hit SQLite `disk I/O error` (often from a stale `app.db-journal` or file locking), run `python .\scripts\reset_db.py` then `python .\scripts\init_local.py`.
- If `DATABASE_URL` points to Supabase/Postgres, install `backend/requirements.txt` and prefer a `postgresql+psycopg://...` URL. The app also normalizes plain `postgresql://...` URLs for local convenience.

