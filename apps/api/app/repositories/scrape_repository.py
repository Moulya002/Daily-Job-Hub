from psycopg import Connection


def create_scrape_run(connection: Connection, *, source_type: str, source_name: str) -> str:
    with connection.cursor() as cursor:
        cursor.execute(
            """
            INSERT INTO "ScrapeRun" (id, "sourceType", "sourceName", status, "createdAt")
            VALUES (gen_random_uuid()::text, %s, %s, 'RUNNING', NOW())
            RETURNING id
            """,
            (source_type, source_name),
        )
        row = cursor.fetchone()
    connection.commit()
    return row["id"]


def complete_scrape_run(
    connection: Connection,
    *,
    scrape_run_id: str,
    status: str,
    jobs_seen: int,
    jobs_inserted: int,
    jobs_updated: int,
    jobs_archived: int = 0,
    error_message: str | None = None,
) -> None:
    with connection.cursor() as cursor:
        cursor.execute(
            """
            UPDATE "ScrapeRun"
            SET status = %s,
                "jobsSeen" = %s,
                "jobsInserted" = %s,
                "jobsUpdated" = %s,
                "jobsArchived" = %s,
                "errorMessage" = %s,
                "completedAt" = NOW()
            WHERE id = %s
            """,
            (status, jobs_seen, jobs_inserted, jobs_updated, jobs_archived, error_message, scrape_run_id),
        )
    connection.commit()


def log_job_scrape_event(
    connection: Connection,
    *,
    job_id: str,
    event_type: str,
    scrape_run_id: str | None = None,
    source_url: str | None = None,
    payload: str = "{}",
) -> None:
    with connection.cursor() as cursor:
        cursor.execute(
            """
            INSERT INTO "JobScrapeEvent"
              (id, "eventType", "sourceUrl", payload, "createdAt", "jobId", "scrapeRunId")
            VALUES (gen_random_uuid()::text, %s, %s, %s::jsonb, NOW(), %s, %s)
            """,
            (event_type, source_url, payload, job_id, scrape_run_id),
        )
    connection.commit()


def create_alert_delivery(
    connection: Connection,
    *,
    alert_id: str,
    user_id: str,
    channel: str,
    jobs_count: int,
) -> None:
    with connection.cursor() as cursor:
        cursor.execute(
            """
            INSERT INTO "AlertDelivery" (id, "deliveredAt", channel, "jobsCount", "alertId", "userId")
            VALUES (gen_random_uuid()::text, NOW(), %s, %s, %s, %s)
            """,
            (channel, jobs_count, alert_id, user_id),
        )
    connection.commit()
