from psycopg import Connection
from psycopg.rows import dict_row

from app.core.categories import categorize_company
from app.scrapers.common import plain_text_summary
from app.schemas.jobs import JobOut, SemanticSearchResult


def list_jobs(
    connection: Connection,
    limit: int = 400,
    *,
    level: str | None = None,
    category: str | None = None,
) -> list[JobOut]:
    """Return active jobs, optionally filtered by level (jobType) and category.

    ``category`` (FAANG+/Quant/Other) is derived from the company name in
    Python, so it is applied after fetching. ``level`` maps to the jobType
    column and is filtered in SQL.
    """
    params: list[object] = []
    where = ["j.status = 'ACTIVE'"]
    if level and level.upper() != "ALL":
        where.append('j."jobType" = %s')
        params.append(level.upper())

    # Fetch a generous window so the in-Python category filter still has rows.
    fetch_limit = max(limit * 4, limit) if category and category.lower() != "all" else limit
    params.append(fetch_limit)

    sql = f"""
        SELECT j.id, j.title, c.name AS "companyName", j.location,
               j."workMode" AS "workMode", j."jobType" AS "jobType",
               j."salaryMin" AS "salaryMin", j."salaryMax" AS "salaryMax",
               j.currency, j."applicationUrl" AS "applyUrl",
               j."postedAt" AS "postedAt",
               j.description AS summary
        FROM "Job" j
        JOIN "Company" c ON c.id = j."companyId"
        WHERE {" AND ".join(where)}
        ORDER BY j."postedAt" DESC NULLS LAST, j."createdAt" DESC
        LIMIT %s
    """

    with connection.cursor(row_factory=dict_row) as cursor:
        cursor.execute(sql, tuple(params))
        rows = cursor.fetchall()

    jobs: list[JobOut] = []
    wanted = category.strip() if category else None
    for row in rows:
        row["category"] = categorize_company(row["companyName"])
        row["summary"] = plain_text_summary(row.get("summary"))
        if wanted and wanted.lower() != "all" and row["category"] != wanted:
            continue
        jobs.append(JobOut(**row))
        if len(jobs) >= limit:
            break
    return jobs


def semantic_search_jobs(
    connection: Connection,
    query_embedding: list[float],
    limit: int = 25,
) -> list[SemanticSearchResult]:
    vector_literal = "[" + ",".join(str(x) for x in query_embedding) + "]"
    with connection.cursor(row_factory=dict_row) as cursor:
        cursor.execute(
            """
            SELECT
              j.id,
              j.title,
              c.name AS "companyName",
              j.location,
              j."workMode" AS "workMode",
              j.description AS summary,
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
    results: list[SemanticSearchResult] = []
    for row in rows:
        row["category"] = categorize_company(row["companyName"])
        row["summary"] = plain_text_summary(row.get("summary"))
        results.append(SemanticSearchResult(**row))
    return results
