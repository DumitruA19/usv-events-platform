# USV University Events Management Platform

Monorepo cu `FastAPI` + `React/Vite` pentru gestionarea evenimentelor universitare. Supabase rămâne serviciu extern pentru Postgres și chei asociate.

## Structură
- `backend/` API FastAPI, SQLAlchemy, Alembic
- `frontend/` aplicația React/Vite
- `docker/` Dockerfile-uri și `docker-compose.yml`
- `docs/` documentație tehnică și funcțională

## Instalare locală

### Backend
```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend
```powershell
cd frontend
npm install
npm run dev
```

### Configurare `.env`
- copiază `backend/.env.example` în `backend/.env`
- copiază `frontend/.env.example` în `frontend/.env`
- configurează:
  - `DATABASE_URL`
  - `GOOGLE_CLIENT_ID`
  - `GOOGLE_CLIENT_SECRET`
  - `GOOGLE_REDIRECT_URI`
  - `FRONTEND_BASE_URL`
  - `VITE_API_BASE_URL`
  - `SUPABASE_URL`
  - `SUPABASE_ANON_KEY`
  - `SUPABASE_SERVICE_ROLE_KEY`
  - `GROQ_API_KEY`
  - `GROQ_MODEL`

## Build production

### Frontend
```powershell
cd frontend
npm install
npm run build
npm run start
```

### Backend
```powershell
cd backend
.\.venv\Scripts\python.exe -m pytest app\tests\test_core_flows.py -q
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## Rulare Docker
```powershell
docker compose -f docker/docker-compose.yml build
docker compose -f docker/docker-compose.yml up -d
docker compose -f docker/docker-compose.yml logs -f
```

Note:
- frontendul este build-uit static și servit prin Nginx pe `http://localhost:5173`
- backendul este expus pe `http://localhost:8000`
- `backend/.env` este citit de containerul backend
- `VITE_API_BASE_URL` este injectat la build-ul frontendului
- Supabase nu este dockerizat local

## Deploy / hosting
- `Vercel` nu este prima alegere aici, deoarece frontendul depinde de un backend separat FastAPI
- `Docker VPS` este cea mai simplă variantă pentru aplicația completă
- `Render`, `Railway` sau `Fly.io` sunt potrivite pentru deploy containerizat
- `Supabase` rămâne extern pentru baza de date și cheile aferente

## Variabile de mediu necesare

### Backend
- `APP_NAME` numele aplicației
- `ENV` mod de rulare
- `DATABASE_URL` conexiune Postgres / Supabase
- `JWT_SECRET_KEY` secret JWT
- `JWT_ALGORITHM` algoritm JWT
- `JWT_ACCESS_TOKEN_EXPIRES_MINUTES` expirare access token
- `JWT_REFRESH_TOKEN_EXPIRES_DAYS` expirare refresh token
- `STORAGE_DIR` stocare locală fișiere
- `INTEGRATIONS_MODE` `real` pentru Google OAuth/Calendar
- `FRONTEND_BASE_URL` URL frontend
- `OAUTH_STATE_SECRET_KEY` semnare stare OAuth
- `STUDENT_EMAIL_DOMAINS` domenii permise pentru student
- `GOOGLE_CLIENT_ID` client Google OAuth
- `GOOGLE_CLIENT_SECRET` secret Google OAuth
- `GOOGLE_REDIRECT_URI` callback backend
- `GOOGLE_CALENDAR_ID` calendar țintă
- `DEFAULT_TIMEZONE` timezone implicit
- `SUPABASE_URL` URL proiect Supabase
- `SUPABASE_ANON_KEY` cheie publică Supabase
- `SUPABASE_SERVICE_ROLE_KEY` cheie server-side only
- `AI_FEATURE_ENABLED` activează fallback AI
- `GROQ_API_KEY` cheie Groq
- `GROQ_MODEL` model Groq
- `SCRAPER_USER_AGENT` user agent scraping
- `SCRAPER_MAX_PAGES` limită pagini scraping

### Frontend
- `VITE_API_BASE_URL` URL public al backendului
- `VITE_APP_URL` URL public al frontendului

## Verificări executate
- `npm run build` în `frontend` trece
- `pytest backend/app/tests/test_core_flows.py -q` trece

## Observații
- autentificarea Google funcționează doar dacă `DATABASE_URL` este accesibil real din rețeaua mașinii
- dacă Supabase pooler sau hostul DB sunt blocate de firewall/rețea, login-ul Google va eșua la etapa de persistare utilizator
