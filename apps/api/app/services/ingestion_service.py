import re
from collections.abc import Callable

from psycopg import Connection

from app.core.config import settings
from app.repositories.jobs_ingestion_repository import (
    upsert_company,
    upsert_job_from_adzuna,
    upsert_normalized_job,
)
from app.repositories.scrape_repository import complete_scrape_run, create_scrape_run
from app.scrapers.adzuna import DEFAULT_QUERIES, fetch_adzuna_jobs
from app.scrapers.arbeitnow import fetch_arbeitnow_jobs
from app.scrapers.ashby import fetch_ashby_jobs
from app.scrapers.common import NormalizedJob
from app.scrapers.greenhouse import fetch_greenhouse_jobs
from app.scrapers.jobicy import fetch_jobicy_jobs
from app.scrapers.lever import fetch_lever_jobs
from app.scrapers.remoteok import fetch_remoteok_jobs
from app.scrapers.remotive import fetch_remotive_jobs
from app.scrapers.yc import fetch_yc_jobs


def _normalize_company_name(name: str) -> str:
    return re.sub(r"\s+", " ", name.strip().lower())


def _split_csv(value: str) -> list[str]:
    return [item.strip() for item in value.split(",") if item.strip()]


def ingest_normalized_jobs(
    connection: Connection,
    *,
    source_type: str,
    source_name: str,
    fetch: Callable[[], list[NormalizedJob]],
) -> dict[str, int | str]:
    """Run one source: create a ScrapeRun, fetch + upsert jobs, record results."""
    scrape_run_id = create_scrape_run(connection, source_type=source_type, source_name=source_name)
    inserted = 0
    updated = 0
    seen = 0

    try:
        jobs = fetch()
        seen = len(jobs)
        for job in jobs:
            company_id = upsert_company(
                connection,
                name=job.company_name,
                normalized_name=_normalize_company_name(job.company_name),
            )
            result = upsert_normalized_job(
                connection,
                company_id=company_id,
                job=job,
                source_type=source_type,
                source_name=source_name,
            )
            if result == "inserted":
                inserted += 1
            else:
                updated += 1

        complete_scrape_run(
            connection,
            scrape_run_id=scrape_run_id,
            status="SUCCEEDED",
            jobs_seen=seen,
            jobs_inserted=inserted,
            jobs_updated=updated,
        )
        return {
            "status": "SUCCEEDED",
            "source": source_name,
            "jobs_seen": seen,
            "jobs_inserted": inserted,
            "jobs_updated": updated,
        }
    except Exception as exc:  # noqa: BLE001 - record failure per source, keep others running
        complete_scrape_run(
            connection,
            scrape_run_id=scrape_run_id,
            status="FAILED",
            jobs_seen=seen,
            jobs_inserted=inserted,
            jobs_updated=updated,
            error_message=str(exc),
        )
        return {
            "status": "FAILED",
            "source": source_name,
            "jobs_seen": seen,
            "jobs_inserted": inserted,
            "jobs_updated": updated,
            "error": str(exc),
        }


def ingest_all_sources(connection: Connection) -> dict:
    """Run every configured free job source and aggregate the results."""
    greenhouse_companies = (
        _split_csv(settings.greenhouse_companies) if settings.greenhouse_companies else None
    )
    lever_companies = _split_csv(settings.lever_companies) if settings.lever_companies else None
    ashby_companies = _split_csv(settings.ashby_companies) if settings.ashby_companies else None

    sources: list[tuple[str, str, Callable[[], list[NormalizedJob]]]] = [
        ("YC", "yc", fetch_yc_jobs),
        ("ASHBY", "ashby", lambda: fetch_ashby_jobs(companies=ashby_companies)),
        ("GREENHOUSE", "greenhouse", lambda: fetch_greenhouse_jobs(companies=greenhouse_companies)),
        ("LEVER", "lever", lambda: fetch_lever_jobs(companies=lever_companies)),
        ("CUSTOM", "remotive", fetch_remotive_jobs),
        ("CUSTOM", "remoteok", fetch_remoteok_jobs),
        ("CUSTOM", "arbeitnow", fetch_arbeitnow_jobs),
        ("CUSTOM", "jobicy", fetch_jobicy_jobs),
    ]

    results = []
    total_inserted = 0
    total_updated = 0
    total_seen = 0

    if settings.adzuna_app_id and settings.adzuna_app_key:
        adzuna_result = ingest_adzuna_jobs(connection)
        results.append(
            {
                "source": "adzuna",
                "status": adzuna_result.get("status"),
                "jobs_seen": adzuna_result.get("jobs_seen", 0),
                "jobs_inserted": adzuna_result.get("jobs_inserted", 0),
                "jobs_updated": adzuna_result.get("jobs_updated", 0),
            }
        )
        total_seen += int(adzuna_result.get("jobs_seen", 0))
        total_inserted += int(adzuna_result.get("jobs_inserted", 0))
        total_updated += int(adzuna_result.get("jobs_updated", 0))

    for source_type, source_name, fetch in sources:
        result = ingest_normalized_jobs(
            connection, source_type=source_type, source_name=source_name, fetch=fetch
        )
        results.append(result)
        total_seen += int(result.get("jobs_seen", 0))
        total_inserted += int(result.get("jobs_inserted", 0))
        total_updated += int(result.get("jobs_updated", 0))

    return {
        "status": "SUCCEEDED",
        "total_jobs_seen": total_seen,
        "total_jobs_inserted": total_inserted,
        "total_jobs_updated": total_updated,
        "sources": results,
    }


def ingest_adzuna_jobs(
    connection: Connection,
    *,
    queries: list[str] | None = None,
    max_pages_per_query: int | None = None,
) -> dict[str, int | str]:
    scrape_run_id = create_scrape_run(connection, source_type="CUSTOM", source_name="adzuna")
    inserted = 0
    updated = 0
    seen = 0

    try:
        jobs = fetch_adzuna_jobs(queries=queries, max_pages_per_query=max_pages_per_query)
        seen = len(jobs)

        for job in jobs:
            company_id = upsert_company(
                connection,
                name=job.company_name,
                normalized_name=_normalize_company_name(job.company_name),
            )
            result = upsert_job_from_adzuna(connection, company_id=company_id, job=job)
            if result == "inserted":
                inserted += 1
            else:
                updated += 1

        complete_scrape_run(
            connection,
            scrape_run_id=scrape_run_id,
            status="SUCCEEDED",
            jobs_seen=seen,
            jobs_inserted=inserted,
            jobs_updated=updated,
        )
        return {
            "status": "SUCCEEDED",
            "scrape_run_id": scrape_run_id,
            "jobs_seen": seen,
            "jobs_inserted": inserted,
            "jobs_updated": updated,
            "queries": queries or DEFAULT_QUERIES,
        }
    except Exception as exc:
        complete_scrape_run(
            connection,
            scrape_run_id=scrape_run_id,
            status="FAILED",
            jobs_seen=seen,
            jobs_inserted=inserted,
            jobs_updated=updated,
            error_message=str(exc),
        )
        raise
