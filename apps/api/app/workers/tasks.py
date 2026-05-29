import logging

from app.db.postgres import open_db_connection
from app.scrapers.sources import (
    scrape_ashby_jobs,
    scrape_greenhouse_jobs,
    scrape_lever_jobs,
    scrape_yc_jobs,
)
from app.services.embedding_service import backfill_job_embeddings
from app.services.ingestion_service import ingest_adzuna_jobs, ingest_all_sources
from app.workers.celery_app import celery_app

logger = logging.getLogger(__name__)


@celery_app.task(bind=True, max_retries=3)
def ingest_all_sources_task(self, embed: bool = True, embed_limit: int = 500) -> dict:
    """Daily pipeline: ingest every configured source, then backfill embeddings.

    This is the task the beat scheduler runs so the board refreshes itself
    without any manual trigger.
    """
    connection = open_db_connection()
    try:
        result = ingest_all_sources(connection)
        if embed:
            result["embeddings"] = backfill_job_embeddings(connection, limit=embed_limit)
        logger.info(
            "Daily ingest complete: inserted=%s updated=%s",
            result.get("total_jobs_inserted"),
            result.get("total_jobs_updated"),
        )
        return result
    except Exception as exc:  # pragma: no cover
        logger.exception("Daily ingest failed")
        raise self.retry(exc=exc, countdown=300) from exc
    finally:
        connection.close()


@celery_app.task(bind=True, max_retries=3)
def scrape_all_sources(self) -> dict[str, int]:
    try:
        return {
            "greenhouse": len(scrape_greenhouse_jobs()),
            "lever": len(scrape_lever_jobs()),
            "ashby": len(scrape_ashby_jobs()),
            "yc": len(scrape_yc_jobs()),
        }
    except Exception as exc:  # pragma: no cover
        raise self.retry(exc=exc) from exc


@celery_app.task(bind=True, max_retries=3)
def ingest_adzuna(self) -> dict:
    connection = open_db_connection()
    try:
        return ingest_adzuna_jobs(connection)
    except Exception as exc:  # pragma: no cover
        raise self.retry(exc=exc) from exc
    finally:
        connection.close()


@celery_app.task(bind=True, max_retries=3)
def generate_job_embeddings(self, limit: int = 200) -> dict:
    connection = open_db_connection()
    try:
        return backfill_job_embeddings(connection, limit=limit)
    except Exception as exc:  # pragma: no cover
        raise self.retry(exc=exc) from exc
    finally:
        connection.close()
