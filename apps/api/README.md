# API Architecture

## Core modules

- `api/routes`: REST endpoints
- `schemas`: request/response contracts
- `services`: AI, search, recommendation business logic
- `scrapers`: source-specific extractors
- `workers` (next): background jobs and queue consumers

## Production extension points

- Add database repository layer under `db/` to keep route handlers thin
- Add `workers/queue.py` for Celery app and periodic scrape tasks
- Add structured logging and distributed tracing middleware
- Add Redis-based rate limiter dependency

## Adzuna ingestion

1. Create a free app at https://developer.adzuna.com/
2. Add to root `.env`:
   - `ADZUNA_APP_ID`
   - `ADZUNA_APP_KEY`
   - `ADZUNA_COUNTRY=us` (optional)
3. Trigger ingestion:
   - `POST http://localhost:8000/ingest/adzuna`
   - Optional query: `?queries=software%20internship,new%20grad&max_pages=2`
4. Verify jobs:
   - `GET http://localhost:8000/jobs`
   - Refresh `http://localhost:3001/jobs`

## Embedding backfill (semantic search)

Requires `OPENAI_API_KEY` in `.env`.

- Auto-runs after `POST /ingest/adzuna`
- Manual trigger:
  - `POST http://localhost:8000/ingest/embeddings?limit=200`
- Then test semantic search:
  - `GET http://localhost:8000/search?query=remote%20ai%20internship`
