# Daily Job Hub

Production-oriented AI-powered internship + new grad job platform with:
- `apps/web` (Next.js 15 App Router)
- `apps/api` (FastAPI microservice for AI + scraping)
- `prisma` (Postgres + pgvector schema)
- shared packages (`ui`, `types`, `utils`)

## 1) Monorepo Structure

```txt
.
├── apps
│   ├── web
│   │   ├── app
│   │   │   ├── page.tsx
│   │   │   ├── jobs
│   │   │   ├── search
│   │   │   ├── dashboard
│   │   │   ├── resume-analysis
│   │   │   ├── saved-jobs
│   │   │   ├── settings
│   │   │   └── admin/scrapers
│   │   ├── lib
│   │   └── store
│   └── api
│       └── app
│           ├── api/routes
│           ├── core
│           ├── schemas
│           ├── services
│           └── scrapers
├── packages
│   ├── ui
│   ├── types
│   └── utils
├── prisma
│   └── schema.prisma
├── turbo.json
└── .env.example
```

## 2) MVP Implementation Order

1. **Infrastructure and schema**
   - Monorepo + app boundaries
   - Prisma schema with `pgvector` column types
2. **Core API**
   - `/jobs`, `/search`, `/ai/resume/upload`, `/ai/resume/analyze`, `/ai/messages/generate`, `/recommendations`
3. **Core frontend routes**
   - Landing, listings, AI search, dashboard, resume analysis, saved jobs, settings, admin scraper monitor
4. **Auth + user data**
   - Auth.js + Prisma adapter + route protection middleware
5. **Real scraping + pipelines**
   - Greenhouse, Lever, Ashby, YC + dedupe + job freshness checks
6. **Production hardening**
   - rate limiting, caching, observability, retry policies, dead-letter queues

## 3) API Surface (MVP)

- `GET /health`
- `GET /jobs`
- `GET /search?query=...`
- `POST /ai/resume/upload` (PDF upload + parsing)
- `POST /ai/resume/analyze`
- `POST /ai/messages/generate`
- `GET /recommendations?user_id=...`

## 4) Required Environment Variables

- `DATABASE_URL` Postgres connection string
- `DIRECT_URL` direct DB URL for migrations
- `REDIS_URL` queue/cache endpoint
- `OPENAI_API_KEY` embeddings + generation
- `NEXTAUTH_SECRET` auth signing secret
- `NEXTAUTH_URL` canonical web app URL
- `AUTH_GITHUB_ID` OAuth provider ID
- `AUTH_GITHUB_SECRET` OAuth provider secret
- `RATE_LIMIT_PER_MINUTE` API throttling guardrail
- `SCRAPER_RUN_INTERVAL_MINUTES` scrape schedule
- `NEXT_PUBLIC_API_BASE_URL` frontend-to-api URL
- `CORS_ORIGINS` comma-separated allowed origins for API CORS

## 5) Deployment Plan

### Web (Vercel)
- Connect repo to Vercel
- Set root to `apps/web`
- Add env vars (all frontend + auth vars)
- Set `NEXT_PUBLIC_API_BASE_URL` to Railway/Supabase API URL

### API (Railway or Render/Fly)
- Deploy `apps/api`
- Use managed Postgres and Redis add-ons
- Run `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- Configure autoscaling and health checks using `/health`

### DB (Supabase / Railway Postgres)
- Enable `vector` extension
- Run Prisma migrations from CI:
  - `pnpm db:generate`
  - `pnpm db:migrate`

## 6) Security Best Practices

- Use signed URLs for resume upload (S3/Supabase storage)
- Validate MIME type and file size for resume PDFs
- Encrypt sensitive profile attributes at rest
- Add input/output filtering and prompt injection checks for AI prompts
- Apply row-level authorization checks for all user resources
- Store secrets in platform secret manager only (never in repo)

## 7) Caching + Rate Limiting

- Redis token bucket limit per IP + per user
- Cache hot queries:
  - search results (60-120s)
  - job listings (300s)
  - recommendations (300s)
- Queue expensive work (resume parsing/embedding/scraping) via Celery or BullMQ workers
- Use dead-letter queue + retries with exponential backoff

## 8) Run Locally

1. Install JS dependencies in monorepo:
   - `pnpm install`
2. Install Python dependencies for API:
   - `cd apps/api && pip install -e .`
3. Copy `.env.example` to `.env` and set secrets
4. Create and migrate database:
   - `pnpm db:generate`
   - `pnpm db:migrate`
   - apply `prisma/vector-indexes.sql` (if not included in migration workflow)
5. Start apps:
   - `pnpm dev` (web + api via turbo)
6. Start background workers:
   - `pnpm --filter @daily-job-hub/api worker`
   - `pnpm --filter @daily-job-hub/api beat`

## 9) Next Production Steps

1. Add Redis-backed distributed rate limiter (replace in-memory limiter)
2. Implement persisted resume storage + S3/Supabase signed uploads
3. Build scraper adapters (Playwright + BeautifulSoup + adapter pattern)
4. Persist ingestion logs and scraper run metrics for admin dashboard
5. Add evaluation pipeline for AI scoring prompt quality
6. Add tests (unit + integration + E2E) and CI pipeline
