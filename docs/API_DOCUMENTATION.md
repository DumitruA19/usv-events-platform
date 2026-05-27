# API Documentation

UI note: the frontend supports Romanian (default) + English, and light/dark themes via header toggles.

Base URL: `http://127.0.0.1:8000`

Auth uses Bearer JWT: `Authorization: Bearer <access_token>`

## Authentication
- `POST /auth/login` (Organizer/Admin)
- `POST /auth/mock-google-login` (Student)
- `POST /auth/refresh`
- `GET /auth/me`

## Events
- `GET /events`
- `GET /events/{id}`
- `POST /events`
- `PUT /events/{id}`
- `DELETE /events/{id}`
- `POST /events/{id}/submit-for-approval`
- `POST /events/{id}/approve`
- `POST /events/{id}/reject`
- `GET /events/calendar`

## Registrations
- `POST /events/{id}/register`
- `DELETE /events/{id}/register`
- `GET /events/{id}/participants`
- `GET /events/{id}/waiting-list`
- `POST /events/{id}/check-in`
- `GET /events/{id}/participants/export`

## Feedback
- `POST /events/{id}/feedback`
- `GET /events/{id}/feedback`
- `GET /events/{id}/feedback/stats`

## Calendar
- `GET /events/{id}/ics`
- `POST /events/{id}/mock-google-calendar`

## Materials
- `POST /events/{id}/materials`
- `GET /events/{id}/materials`
- `DELETE /materials/{id}`

## Admin
- `GET /admin/users`
- `POST /admin/organizers`
- `PUT /admin/organizers/{id}`
- `DELETE /admin/organizers/{id}`
- `GET /admin/events/pending`
- `GET /admin/reports/events-per-month`
- `GET /admin/reports/participation`
- `GET /admin/reports/by-organizer`
- `GET /admin/reports/export-pdf`

## Notifications
- `GET /notifications`
- `POST /notifications/mock-send-reminders`

## Scraping (Mock)
- `POST /scraping/mock-run`
- `GET /scraping/drafts`
- `POST /scraping/drafts/{id}/approve`
- `DELETE /scraping/drafts/{id}`

For request/response examples, see the interactive docs at `/docs`.
