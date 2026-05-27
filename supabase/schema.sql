-- Supabase / Postgres schema for AI chatbot + scraping ingestion.
-- Safe-by-default: no external embedding provider required.
--
-- Apply in Supabase SQL Editor, or via `supabase db reset` in a local stack.

create extension if not exists pgcrypto;

-- Optional: pgvector (NOT required). If you want vector search:
--   create extension if not exists vector;
-- and consider adding a `vector(...)` column to `kb_chunks`.

-- --- utility: updated_at trigger ---
create or replace function public.set_updated_at()
returns trigger
language plpgsql
as $$
begin
  new.updated_at = now();
  return new;
end;
$$;

-- --- users / profiles ---
-- Supabase provides `auth.users`. This table stores app-specific profile data.
create table if not exists public.profiles (
  id uuid primary key references auth.users(id) on delete cascade,
  display_name text,
  avatar_url text,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);
comment on table public.profiles is 'App user profile metadata (1:1 with auth.users).';

create trigger trg_profiles_updated_at
before update on public.profiles
for each row execute function public.set_updated_at();

alter table public.profiles enable row level security;
create policy "profiles_select_own"
on public.profiles for select
using (auth.uid() = id);
create policy "profiles_upsert_own"
on public.profiles for insert
with check (auth.uid() = id);
create policy "profiles_update_own"
on public.profiles for update
using (auth.uid() = id)
with check (auth.uid() = id);

-- --- AI providers / models ---
create table if not exists public.ai_models (
  id uuid primary key default gen_random_uuid(),
  provider text not null,
  model text not null,
  is_active boolean not null default true,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  constraint ai_models_provider_chk check (length(provider) > 0),
  constraint ai_models_model_chk check (length(model) > 0),
  constraint ai_models_provider_model_uniq unique (provider, model)
);
comment on table public.ai_models is 'Catalog of AI providers/models (for auditing + selection).';

create index if not exists ai_models_active_idx on public.ai_models (is_active);
create trigger trg_ai_models_updated_at
before update on public.ai_models
for each row execute function public.set_updated_at();

-- --- chat sessions / messages ---
create table if not exists public.chat_sessions (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users(id) on delete cascade,
  title text,
  status text not null default 'active',
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  constraint chat_sessions_status_chk check (status in ('active','archived'))
);
comment on table public.chat_sessions is 'Per-user chat sessions.';

create index if not exists chat_sessions_user_created_idx on public.chat_sessions (user_id, created_at desc);
create trigger trg_chat_sessions_updated_at
before update on public.chat_sessions
for each row execute function public.set_updated_at();

alter table public.chat_sessions enable row level security;
create policy "chat_sessions_select_own"
on public.chat_sessions for select
using (auth.uid() = user_id);
create policy "chat_sessions_insert_own"
on public.chat_sessions for insert
with check (auth.uid() = user_id);
create policy "chat_sessions_update_own"
on public.chat_sessions for update
using (auth.uid() = user_id)
with check (auth.uid() = user_id);

create table if not exists public.chat_messages (
  id uuid primary key default gen_random_uuid(),
  session_id uuid not null references public.chat_sessions(id) on delete cascade,
  user_id uuid not null references auth.users(id) on delete cascade,
  role text not null,
  content text not null,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  constraint chat_messages_role_chk check (role in ('user','assistant','system')),
  constraint chat_messages_content_chk check (length(content) > 0)
);
comment on table public.chat_messages is 'Chat messages (user + assistant + optional system).';

create index if not exists chat_messages_session_created_idx on public.chat_messages (session_id, created_at asc);
create index if not exists chat_messages_user_created_idx on public.chat_messages (user_id, created_at desc);
create trigger trg_chat_messages_updated_at
before update on public.chat_messages
for each row execute function public.set_updated_at();

alter table public.chat_messages enable row level security;
create policy "chat_messages_select_own"
on public.chat_messages for select
using (auth.uid() = user_id);
create policy "chat_messages_insert_own"
on public.chat_messages for insert
with check (auth.uid() = user_id);

-- --- AI request logs (auditing + cost tracking) ---
create table if not exists public.ai_requests (
  id uuid primary key default gen_random_uuid(),
  user_id uuid references auth.users(id) on delete set null,
  session_id uuid references public.chat_sessions(id) on delete set null,
  model_id uuid references public.ai_models(id) on delete set null,
  provider_request_id text,
  status text not null default 'skipped',
  prompt_tokens integer,
  completion_tokens integer,
  total_tokens integer,
  latency_ms integer,
  error_message text,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  constraint ai_requests_status_chk check (status in ('ok','error','skipped'))
);
comment on table public.ai_requests is 'Request/response metadata for AI calls (or skipped placeholders).';

create index if not exists ai_requests_user_created_idx on public.ai_requests (user_id, created_at desc);
create index if not exists ai_requests_session_created_idx on public.ai_requests (session_id, created_at desc);
create trigger trg_ai_requests_updated_at
before update on public.ai_requests
for each row execute function public.set_updated_at();

alter table public.ai_requests enable row level security;
create policy "ai_requests_select_own"
on public.ai_requests for select
using (auth.uid() = user_id);
create policy "ai_requests_insert_own"
on public.ai_requests for insert
with check (auth.uid() = user_id);

-- --- scraped sources + pages ---
create table if not exists public.scraped_sources (
  id uuid primary key default gen_random_uuid(),
  owner_user_id uuid references auth.users(id) on delete set null,
  name text not null,
  base_url text,
  kind text not null default 'mock',
  is_active boolean not null default true,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  constraint scraped_sources_kind_chk check (kind in ('mock','http','file','rss','api')),
  constraint scraped_sources_name_chk check (length(name) > 0)
);
comment on table public.scraped_sources is 'Registered ingestion sources. Use kind=mock by default.';

create index if not exists scraped_sources_active_idx on public.scraped_sources (is_active);
create index if not exists scraped_sources_owner_idx on public.scraped_sources (owner_user_id);
create trigger trg_scraped_sources_updated_at
before update on public.scraped_sources
for each row execute function public.set_updated_at();

alter table public.scraped_sources enable row level security;
create policy "scraped_sources_select_owner_or_public"
on public.scraped_sources for select
using (owner_user_id is null or auth.uid() = owner_user_id);
create policy "scraped_sources_write_owner"
on public.scraped_sources for insert
with check (owner_user_id is null or auth.uid() = owner_user_id);
create policy "scraped_sources_update_owner"
on public.scraped_sources for update
using (owner_user_id is null or auth.uid() = owner_user_id)
with check (owner_user_id is null or auth.uid() = owner_user_id);

create table if not exists public.scraped_pages (
  id uuid primary key default gen_random_uuid(),
  source_id uuid not null references public.scraped_sources(id) on delete cascade,
  url text not null,
  title text,
  content_text text not null,
  content_hash text,
  fetched_at timestamptz not null default now(),
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  constraint scraped_pages_url_chk check (length(url) > 0),
  constraint scraped_pages_content_chk check (length(content_text) > 0)
);
comment on table public.scraped_pages is 'Raw extracted page/document text (post-cleaning).';

create unique index if not exists scraped_pages_source_url_uniq on public.scraped_pages (source_id, url);
create index if not exists scraped_pages_source_fetched_idx on public.scraped_pages (source_id, fetched_at desc);
create trigger trg_scraped_pages_updated_at
before update on public.scraped_pages
for each row execute function public.set_updated_at();

-- --- knowledge base chunks (for retrieval) ---
create table if not exists public.kb_chunks (
  id uuid primary key default gen_random_uuid(),
  page_id uuid not null references public.scraped_pages(id) on delete cascade,
  chunk_index integer not null,
  content text not null,
  token_count integer,
  embedding real[], -- optional: store raw embedding floats without pgvector
  embedding_model text,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  constraint kb_chunks_chunk_index_chk check (chunk_index >= 0),
  constraint kb_chunks_content_chk check (length(content) > 0)
);
comment on table public.kb_chunks is 'Text chunks derived from scraped_pages for retrieval (optionally with embeddings).';
comment on column public.kb_chunks.embedding is 'Optional float array embedding (no provider required). Consider pgvector for similarity search.';

create unique index if not exists kb_chunks_page_chunk_uniq on public.kb_chunks (page_id, chunk_index);
create index if not exists kb_chunks_page_idx on public.kb_chunks (page_id);
create trigger trg_kb_chunks_updated_at
before update on public.kb_chunks
for each row execute function public.set_updated_at();

-- --- ingestion jobs ---
create table if not exists public.ingestion_jobs (
  id uuid primary key default gen_random_uuid(),
  source_id uuid references public.scraped_sources(id) on delete set null,
  requested_by uuid references auth.users(id) on delete set null,
  status text not null default 'queued',
  started_at timestamptz,
  finished_at timestamptz,
  stats jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  constraint ingestion_jobs_status_chk check (status in ('queued','running','succeeded','failed','canceled'))
);
comment on table public.ingestion_jobs is 'Tracks ingestion runs (mock or real).';

create index if not exists ingestion_jobs_created_idx on public.ingestion_jobs (created_at desc);
create index if not exists ingestion_jobs_status_idx on public.ingestion_jobs (status);
create trigger trg_ingestion_jobs_updated_at
before update on public.ingestion_jobs
for each row execute function public.set_updated_at();

alter table public.ingestion_jobs enable row level security;
create policy "ingestion_jobs_select_own"
on public.ingestion_jobs for select
using (requested_by is null or auth.uid() = requested_by);
create policy "ingestion_jobs_insert_own"
on public.ingestion_jobs for insert
with check (requested_by is null or auth.uid() = requested_by);

create table if not exists public.ingestion_job_logs (
  id uuid primary key default gen_random_uuid(),
  job_id uuid not null references public.ingestion_jobs(id) on delete cascade,
  level text not null default 'info',
  message text not null,
  context jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  constraint ingestion_job_logs_level_chk check (level in ('debug','info','warn','error')),
  constraint ingestion_job_logs_message_chk check (length(message) > 0)
);
comment on table public.ingestion_job_logs is 'Append-only logs for ingestion jobs.';

create index if not exists ingestion_job_logs_job_created_idx on public.ingestion_job_logs (job_id, created_at asc);
create trigger trg_ingestion_job_logs_updated_at
before update on public.ingestion_job_logs
for each row execute function public.set_updated_at();

alter table public.ingestion_job_logs enable row level security;
create policy "ingestion_job_logs_select_via_job"
on public.ingestion_job_logs for select
using (
  exists (
    select 1 from public.ingestion_jobs j
    where j.id = ingestion_job_logs.job_id
      and (j.requested_by is null or j.requested_by = auth.uid())
  )
);

-- --- knowledge references (message -> chunks) ---
create table if not exists public.chat_message_kb_refs (
  id uuid primary key default gen_random_uuid(),
  message_id uuid not null references public.chat_messages(id) on delete cascade,
  chunk_id uuid not null references public.kb_chunks(id) on delete cascade,
  score double precision,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);
comment on table public.chat_message_kb_refs is 'Links assistant replies to the chunks used as context (auditability).';

create unique index if not exists chat_message_kb_refs_uniq on public.chat_message_kb_refs (message_id, chunk_id);
create index if not exists chat_message_kb_refs_chunk_idx on public.chat_message_kb_refs (chunk_id);
create trigger trg_chat_message_kb_refs_updated_at
before update on public.chat_message_kb_refs
for each row execute function public.set_updated_at();

alter table public.chat_message_kb_refs enable row level security;
create policy "chat_message_kb_refs_select_own"
on public.chat_message_kb_refs for select
using (
  exists (
    select 1 from public.chat_messages m
    where m.id = chat_message_kb_refs.message_id
      and m.user_id = auth.uid()
  )
);

-- --- optional tags ---
create table if not exists public.tags (
  id uuid primary key default gen_random_uuid(),
  name text not null unique,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  constraint tags_name_chk check (length(name) > 0)
);
comment on table public.tags is 'Optional tags for sources/pages/chunks.';

create trigger trg_tags_updated_at
before update on public.tags
for each row execute function public.set_updated_at();

create table if not exists public.page_tags (
  id uuid primary key default gen_random_uuid(),
  page_id uuid not null references public.scraped_pages(id) on delete cascade,
  tag_id uuid not null references public.tags(id) on delete cascade,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  constraint page_tags_uniq unique (page_id, tag_id)
);
comment on table public.page_tags is 'Many-to-many tags for scraped_pages.';

create trigger trg_page_tags_updated_at
before update on public.page_tags
for each row execute function public.set_updated_at();

