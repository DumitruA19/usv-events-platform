# Supabase AI Chatbot + Ingestion (Preparation)

UI note: the frontend supports Romanian (default) + English, and light/dark themes via header toggles.

This repo includes a **safe skeleton** for a Supabase-backed scraping/ingestion flow and a basic RAG chatbot flow.

Key properties:
- No real API keys committed.
- No external scraping runs by default (mock ingestion only).
- No external AI API calls unless explicitly enabled.

## 1) Apply the Supabase SQL schema
Run the SQL in `usv-events-platform/supabase/schema.sql` in **Supabase → SQL Editor**.

Notes:
- Requires `pgcrypto` (enabled by the script).
- `pgvector` is **optional** and not required; embeddings are stored as `real[]` for now.

## 2) Environment variables (backend)
Set these in `usv-events-platform/backend/.env` (see `usv-events-platform/backend/.env.example`):
- `DATABASE_URL` (can be Supabase Postgres connection string)
- `SUPABASE_URL`, `SUPABASE_ANON_KEY` (optional; for future use)
- `SUPABASE_SERVICE_ROLE_KEY` (server-only; never expose to frontend)
- `AI_FEATURE_ENABLED` (default `false`)
- `AI_PROVIDER`, `AI_MODEL`, `AI_API_KEY`
- `AI_ALLOW_EXTERNAL_CALLS` (default `false`)
- `SCRAPER_USER_AGENT`, `SCRAPER_MAX_PAGES`

## 3) Mock ingestion flow
Implementation: `backend/app/ai/ingestion_service.py`

What it does:
- Creates an ingestion job (`public.ingestion_jobs`)
- Registers a `mock` source (`public.scraped_sources`)
- Inserts a single mock page (`public.scraped_pages`)
- Cleans + chunks text and stores chunks (`public.kb_chunks`)
- Adds job logs (`public.ingestion_job_logs`)

Safety:
- No HTTP requests are performed.
- To ingest real URLs, implement a fetcher and restrict allowed domains/targets explicitly.

## 4) Retrieval + chatbot flow (RAG skeleton)
Implementation:
- Retrieval: `backend/app/ai/retrieval_service.py` (simple `LIKE` / `ILIKE`)
- Chatbot orchestration: `backend/app/ai/chatbot_service.py`
- AI client abstraction: `backend/app/ai/ai_client.py`

Flow:
1) Store user message (table: `public.chat_messages`)
2) Retrieve relevant chunks from `public.kb_chunks` (simple text search)
3) Build prompt: user message + retrieved chunks
4) Generate response:
   - returns a placeholder unless `AI_ALLOW_EXTERNAL_CALLS=true` and `AI_API_KEY` is set
5) Store assistant message and link used chunks (`public.chat_message_kb_refs`)
6) Store request metadata (`public.ai_requests`)

## 5) Security notes (Supabase keys)
- `SUPABASE_ANON_KEY` is safe for frontend usage only with correct RLS policies.
- `SUPABASE_SERVICE_ROLE_KEY` bypasses RLS and must be kept **server-side only**.
- Keep `.env` untracked; only `.env.example` should be committed.

## 6) Next steps for production
- Add pgvector + vector indexes for similarity search.
- Implement a real fetcher with an allowlist (domains/paths) and rate limiting.
- Add a real AI provider adapter (OpenAI/Azure/etc) behind `AI_ALLOW_EXTERNAL_CALLS`.
- Add a dedicated “knowledge base admin” UI and background job runner.
