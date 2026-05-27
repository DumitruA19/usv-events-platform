# Deployment Notes

UI note: the frontend supports Romanian (default) + English, and light/dark themes via header toggles.

This repo ships generic Docker assets (`docker/`) but does not require Docker for local development.

## Containerization later
- Replace mock integrations with real adapters (Google OAuth, calendar, email, storage).
- Switch `DATABASE_URL` to PostgreSQL.
- Use a secret manager for JWT secrets.
- Enable HTTPS, security headers, and request rate limiting.

## Environment variables
- Backend: `backend/.env.example`
- Frontend: `frontend/.env.example`
