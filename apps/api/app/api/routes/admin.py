from fastapi import APIRouter, Depends, Query
from psycopg import Connection

from app.api.deps.rate_limit import check_rate_limit
from app.db.postgres import get_db_connection

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/scrape-runs")
async def list_scrape_runs(
    limit: int = Query(20, ge=1, le=200),
    _rate_limit: None = Depends(check_rate_limit),
    connection: Connection = Depends(get_db_connection),
) -> list[dict]:
    with connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT id, "sourceType" AS source_type, "sourceName" AS source_name, status,
                   "jobsSeen" AS jobs_seen, "jobsInserted" AS jobs_inserted, "jobsUpdated" AS jobs_updated,
                   "jobsArchived" AS jobs_archived, "errorMessage" AS error_message,
                   "startedAt" AS started_at, "completedAt" AS completed_at, "createdAt" AS created_at
            FROM "ScrapeRun"
            ORDER BY "createdAt" DESC
            LIMIT %s
            """,
            (limit,),
        )
        rows = cursor.fetchall()
    return rows


@router.get("/alert-deliveries")
async def list_alert_deliveries(
    user_id: str | None = None,
    limit: int = Query(50, ge=1, le=500),
    _rate_limit: None = Depends(check_rate_limit),
    connection: Connection = Depends(get_db_connection),
) -> list[dict]:
    with connection.cursor() as cursor:
        if user_id:
            cursor.execute(
                """
                SELECT id, "deliveredAt" AS delivered_at, channel, "jobsCount" AS jobs_count,
                       "openedAt" AS opened_at, "clickedAt" AS clicked_at, "alertId" AS alert_id, "userId" AS user_id
                FROM "AlertDelivery"
                WHERE "userId" = %s
                ORDER BY "deliveredAt" DESC
                LIMIT %s
                """,
                (user_id, limit),
            )
        else:
            cursor.execute(
                """
                SELECT id, "deliveredAt" AS delivered_at, channel, "jobsCount" AS jobs_count,
                       "openedAt" AS opened_at, "clickedAt" AS clicked_at, "alertId" AS alert_id, "userId" AS user_id
                FROM "AlertDelivery"
                ORDER BY "deliveredAt" DESC
                LIMIT %s
                """,
                (limit,),
            )
        rows = cursor.fetchall()
    return rows
