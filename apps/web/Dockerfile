# Next.js web image. Build context MUST be the repo root (pnpm workspace).
#   docker build -f apps/web/Dockerfile -t djh-web .
FROM node:20-slim AS builder

RUN npm install -g pnpm@9
WORKDIR /repo

COPY . .

RUN pnpm install
# Generate Prisma client from the root schema before building the app
RUN pnpm db:generate

ARG NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
ENV NEXT_PUBLIC_API_BASE_URL=$NEXT_PUBLIC_API_BASE_URL
ENV NEXT_TELEMETRY_DISABLED=1

RUN pnpm --filter @daily-job-hub/web build

WORKDIR /repo/apps/web
EXPOSE 3000
CMD ["pnpm", "start"]
