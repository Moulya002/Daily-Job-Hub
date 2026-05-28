from psycopg import Connection

from app.schemas.jobs import JobOut


def recommendations_for_user(connection: Connection, user_id: str, limit: int = 15) -> list[JobOut]:
    with connection.cursor() as cursor:
        cursor.execute(
            """
            WITH preferred_embeddings AS (
              SELECT e.vector
              FROM "SavedJob" sj
              JOIN "Embedding" e ON e."jobId" = sj."jobId"
              WHERE sj."userId" = %s
                AND e."entityType" = 'JOB'
              ORDER BY sj."createdAt" DESC
              LIMIT 20
            )
            SELECT j.id, j.title, c.name AS company_name, j.location, j."workMode" AS work_mode,
                   LEFT(j.description, 240) AS summary, j."postedAt" AS posted_at
            FROM "Job" j
            JOIN "Company" c ON c.id = j."companyId"
            JOIN "Embedding" je ON je."jobId" = j.id
            WHERE je."entityType" = 'JOB'
              AND NOT EXISTS (
                SELECT 1 FROM "Application" a WHERE a."userId" = %s AND a."jobId" = j.id
              )
            ORDER BY (
              SELECT AVG(je.vector <=> p.vector)
              FROM preferred_embeddings p
            ) ASC NULLS LAST,
            j."postedAt" DESC NULLS LAST
            LIMIT %s
            """,
            (user_id, user_id, limit),
        )
        rows = cursor.fetchall()
    return [JobOut(**row) for row in rows]
