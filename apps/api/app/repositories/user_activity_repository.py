from psycopg import Connection
from psycopg.rows import dict_row

from app.schemas.jobs import JobOut
from app.schemas.user_activity import ApplicationItem, SavedJobItem
from app.scrapers.common import plain_text_summary


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


_JOB_CARD_SQL = """
    SELECT j.id, j.title, c.name AS "companyName", j.location,
           j."workMode" AS "workMode", j."jobType" AS "jobType",
           j."salaryMin" AS "salaryMin", j."salaryMax" AS "salaryMax",
           j.currency, j."applicationUrl" AS "applyUrl",
           j."postedAt" AS "postedAt",
           j.description AS summary
    FROM "Job" j
    JOIN "Company" c ON c.id = j."companyId"
"""


def list_saved_job_cards(connection: Connection, *, user_id: str) -> list[JobOut]:
    with connection.cursor(row_factory=dict_row) as cursor:
        cursor.execute(
            f"""
            {_JOB_CARD_SQL}
            JOIN "SavedJob" s ON s."jobId" = j.id
            WHERE s."userId" = %s AND j.status = 'ACTIVE'
            ORDER BY s."createdAt" DESC
            """,
            (user_id,),
        )
        rows = cursor.fetchall()
    jobs: list[JobOut] = []
    for row in rows:
        row["category"] = "Other"
        row["summary"] = plain_text_summary(row.get("summary"))
        jobs.append(JobOut(**row))
    return jobs


def list_applied_job_cards(connection: Connection, *, user_id: str) -> list[JobOut]:
    with connection.cursor(row_factory=dict_row) as cursor:
        cursor.execute(
            f"""
            {_JOB_CARD_SQL}
            JOIN "Application" a ON a."jobId" = j.id
            WHERE a."userId" = %s AND j.status = 'ACTIVE'
            ORDER BY a."updatedAt" DESC
            """,
            (user_id,),
        )
        rows = cursor.fetchall()
    jobs: list[JobOut] = []
    for row in rows:
        row["category"] = "Other"
        row["summary"] = plain_text_summary(row.get("summary"))
        jobs.append(JobOut(**row))
    return jobs
