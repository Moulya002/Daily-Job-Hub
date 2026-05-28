# Frontend Architecture

## App Router Structure

- `app/(marketing)` public SaaS pages (`/`, `/jobs`, `/search`, `/jobs/[id]`)
- `app/(app)` authenticated product pages (`/dashboard`, `/applications`, `/saved-jobs`, `/resume-analysis`, `/settings`, `/admin/scrapers`)
- `app/api/auth/[...nextauth]` Auth.js route handler

## Reusable Component System

- `components/ui`: shadcn-style primitives (`button`, `card`, `input`, `badge`, `avatar`, `separator`)
- `components/common`: composable domain widgets (`job-card`, `metric-card`, `page-header`, `empty-state`, auth actions)
- `components/layout`: product shells (`marketing-header`, `app-shell`)

## Authentication Flow

1. User signs in from public header via GitHub provider.
2. Auth.js stores session in database.
3. `middleware.ts` protects application routes.
4. `(app)` layout performs server-side session guard and redirects unauthenticated users.

## Responsive SaaS Patterns

- Sidebar shell on desktop, stacked content on mobile.
- Grid-based cards for metrics/listings.
- Reusable headers and cards keep UX consistent across pages.
