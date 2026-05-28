from psycopg import Connection

from app.schemas.user_activity import ApplicationItem, SavedJobItem


def save_job(connection: Connection, *, user_id: str, job_id: str) -> None:
    with connection.cursor() as cursor:
        cursor.execute(
            """
            INSERT INTO "SavedJob" (id, "createdAt", "userId", "jobId")
            VALUES (gen_random_uuid()::text, NOW(), %s, %s)
            ON CONFLICT ("userId", "jobId") DO NOTHING
            """,
            (user_id, job_id),
        )
    connection.commit()


def unsave_job(connection: Connection, *, user_id: str, job_id: str) -> None:
    with connection.cursor() as cursor:
        cursor.execute(
            """
            DELETE FROM "SavedJob"
            WHERE "userId" = %s AND "jobId" = %s
            """,
            (user_id, job_id),
        )
    connection.commit()


def mark_applied(connection: Connection, *, user_id: str, job_id: str) -> None:
    with connection.cursor() as cursor:
        cursor.execute(
            """
            INSERT INTO "Application" (id, status, source, "createdAt", "updatedAt", "userId", "jobId")
            VALUES (gen_random_uuid()::text, 'APPLIED', 'PLATFORM', NOW(), NOW(), %s, %s)
            ON CONFLICT ("userId", "jobId")
            DO UPDATE SET status = 'APPLIED', "updatedAt" = NOW()
            """,
            (user_id, job_id),
        )
    connection.commit()


def unmark_applied(connection: Connection, *, user_id: str, job_id: str) -> None:
    with connection.cursor() as cursor:
        cursor.execute(
            """
            DELETE FROM "Application"
            WHERE "userId" = %s AND "jobId" = %s
            """,
            (user_id, job_id),
        )
    connection.commit()


def list_saved_jobs(connection: Connection, *, user_id: str) -> list[SavedJobItem]:
    with connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT "jobId" AS job_id, "createdAt" AS created_at
            FROM "SavedJob"
            WHERE "userId" = %s
            ORDER BY "createdAt" DESC
            """,
            (user_id,),
        )
        rows = cursor.fetchall()
    return [SavedJobItem(**row) for row in rows]


def list_applications(connection: Connection, *, user_id: str) -> list[ApplicationItem]:
    with connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT "jobId" AS job_id, status, "updatedAt" AS updated_at
            FROM "Application"
            WHERE "userId" = %s
            ORDER BY "updatedAt" DESC
            """,
            (user_id,),
        )
        rows = cursor.fetchall()
    return [ApplicationItem(**row) for row in rows]
