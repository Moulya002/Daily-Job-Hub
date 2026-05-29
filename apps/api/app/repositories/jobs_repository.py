from psycopg import Connection

from app.schemas.jobs import JobOut, SemanticSearchResult


def list_jobs(connection: Connection, limit: int = 100) -> list[JobOut]:
    with connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT j.id, j.title, c.name AS company_name, j.location,
                   j."workMode" AS work_mode,
                   LEFT(j.description, 240) AS summary, j."postedAt" AS posted_at
            FROM "Job" j
            JOIN "Company" c ON c.id = j."companyId"
            ORDER BY j."postedAt" DESC NULLS LAST, j."createdAt" DESC
            LIMIT %s
            """,
            (limit,),
        )
        rows = cursor.fetchall()
    return [JobOut(**row) for row in rows]


def semantic_search_jobs(
    connection: Connection,
    query_embedding: list[float],
    limit: int = 25,
) -> list[SemanticSearchResult]:
    vector_literal = "[" + ",".join(str(x) for x in query_embedding) + "]"
    with connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT
              j.id,
              j.title,
              c.name AS company_name,
              j.location,
              j."workMode" AS work_mode,
              LEFT(j.description, 240) AS summary,
              1 - (e.vector <=> %s::vector) AS score
            FROM "Job" j
            JOIN "Company" c ON c.id = j."companyId"
            JOIN "Embedding" e ON e."jobId" = j.id
            WHERE e."entityType" = 'JOB'
            ORDER BY e.vector <=> %s::vector
            LIMIT %s
            """,
            (vector_literal, vector_literal, limit),
        )
        rows = cursor.fetchall()
    return [SemanticSearchResult(**row) for row in rows]
