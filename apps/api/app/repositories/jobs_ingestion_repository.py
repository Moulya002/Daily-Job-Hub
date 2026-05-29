from datetime import UTC, datetime

from psycopg import Connection

from app.scrapers.adzuna import AdzunaJob, build_dedupe_hash
from app.scrapers.common import NormalizedJob
from app.scrapers.common import build_dedupe_hash as build_normalized_dedupe_hash


def upsert_company(connection: Connection, *, name: str, normalized_name: str) -> str:
    with connection.cursor() as cursor:
        cursor.execute(
            """
            INSERT INTO "Company" (id, name, "normalizedName", "createdAt", "updatedAt")
            VALUES (gen_random_uuid()::text, %s, %s, NOW(), NOW())
            ON CONFLICT ("normalizedName")
            DO UPDATE SET
              name = EXCLUDED.name,
              "updatedAt" = NOW()
            RETURNING id
            """,
            (name, normalized_name),
        )
        row = cursor.fetchone()
    connection.commit()
    return row["id"]


def upsert_job_from_adzuna(connection: Connection, *, company_id: str, job: AdzunaJob) -> str:
    dedupe_hash = build_dedupe_hash(job)
    normalized_title = job.title.strip().lower()
    now = datetime.now(UTC)

    with connection.cursor() as cursor:
        cursor.execute(
            """
            INSERT INTO "Job" (
              id, "externalId", "sourceType", "sourceName", "sourceUrl", "applicationUrl",
              title, "normalizedTitle", description, location, "salaryMin", "salaryMax",
              "techStack", keywords, "jobType", status, "postedAt", "lastSeenAt",
              "dedupeHash", "createdAt", "updatedAt", "companyId"
            )
            VALUES (
              gen_random_uuid()::text, %s, 'CUSTOM', 'adzuna', %s, %s,
              %s, %s, %s, %s, %s, %s,
              %s, %s, %s::"JobType", 'ACTIVE', %s, %s,
              %s, NOW(), NOW(), %s
            )
            ON CONFLICT ("sourceName", "externalId")
            DO UPDATE SET
              description = EXCLUDED.description,
              location = EXCLUDED.location,
              "salaryMin" = EXCLUDED."salaryMin",
              "salaryMax" = EXCLUDED."salaryMax",
              "dedupeHash" = EXCLUDED."dedupeHash",
              "lastSeenAt" = EXCLUDED."lastSeenAt",
              "updatedAt" = NOW()
            RETURNING id, (xmax = 0) AS inserted
            """,
            (
                job.external_id,
                job.source_url,
                job.application_url,
                job.title,
                normalized_title,
                job.description,
                job.location,
                job.salary_min,
                job.salary_max,
                [],
                job.keywords,
                job.job_type,
                job.posted_at,
                now,
                dedupe_hash,
                company_id,
            ),
        )
        row = cursor.fetchone()
    connection.commit()
    return "inserted" if row["inserted"] else "updated"


def upsert_normalized_job(
    connection: Connection,
    *,
    company_id: str,
    job: NormalizedJob,
    source_type: str,
    source_name: str,
) -> str:
    dedupe_hash = build_normalized_dedupe_hash(job)
    normalized_title = job.title.strip().lower()
    now = datetime.now(UTC)

    with connection.cursor() as cursor:
        cursor.execute(
            """
            INSERT INTO "Job" (
              id, "externalId", "sourceType", "sourceName", "sourceUrl", "applicationUrl",
              title, "normalizedTitle", description, location, "salaryMin", "salaryMax",
              "techStack", keywords, "jobType", "workMode", status, "postedAt", "lastSeenAt",
              "dedupeHash", "createdAt", "updatedAt", "companyId"
            )
            VALUES (
              gen_random_uuid()::text, %s, %s::"ScrapeSourceType", %s, %s, %s,
              %s, %s, %s, %s, %s, %s,
              %s, %s, %s::"JobType", %s::"WorkMode", 'ACTIVE', %s, %s,
              %s, NOW(), NOW(), %s
            )
            ON CONFLICT ("sourceName", "externalId")
            DO UPDATE SET
              description = EXCLUDED.description,
              location = EXCLUDED.location,
              "salaryMin" = EXCLUDED."salaryMin",
              "salaryMax" = EXCLUDED."salaryMax",
              "workMode" = EXCLUDED."workMode",
              "dedupeHash" = EXCLUDED."dedupeHash",
              "lastSeenAt" = EXCLUDED."lastSeenAt",
              "updatedAt" = NOW()
            RETURNING id, (xmax = 0) AS inserted
            """,
            (
                job.external_id,
                source_type,
                source_name,
                job.source_url,
                job.application_url,
                job.title,
                normalized_title,
                job.description,
                job.location,
                job.salary_min,
                job.salary_max,
                [],
                job.keywords,
                job.job_type,
                job.work_mode,
                job.posted_at,
                now,
                dedupe_hash,
                company_id,
            ),
        )
        row = cursor.fetchone()
    connection.commit()
    return "inserted" if row["inserted"] else "updated"
