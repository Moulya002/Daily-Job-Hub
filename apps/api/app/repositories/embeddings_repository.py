from psycopg import Connection


def list_jobs_missing_embeddings(
    connection: Connection,
    *,
    model_name: str,
    limit: int = 100,
) -> list[dict]:
    with connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT
              j.id,
              j.title,
              c.name AS company_name,
              j.description,
              j.location
            FROM "Job" j
            JOIN "Company" c ON c.id = j."companyId"
            WHERE j.status = 'ACTIVE'
              AND NOT EXISTS (
                SELECT 1
                FROM "Embedding" e
                WHERE e."jobId" = j.id
                  AND e."entityType" = 'JOB'
                  AND e."modelName" = %s
              )
            ORDER BY j."createdAt" DESC
            LIMIT %s
            """,
            (model_name, limit),
        )
        rows = cursor.fetchall()
    return rows


def count_jobs_missing_embeddings(connection: Connection, *, model_name: str) -> int:
    with connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT COUNT(*) AS total
            FROM "Job" j
            WHERE j.status = 'ACTIVE'
              AND NOT EXISTS (
                SELECT 1
                FROM "Embedding" e
                WHERE e."jobId" = j.id
                  AND e."entityType" = 'JOB'
                  AND e."modelName" = %s
              )
            """,
            (model_name,),
        )
        row = cursor.fetchone()
    return int(row["total"])
