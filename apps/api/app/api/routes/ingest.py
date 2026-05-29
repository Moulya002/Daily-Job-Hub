from fastapi import APIRouter, Depends, HTTPException, Query, status
from psycopg import Connection

from app.api.deps.rate_limit import check_rate_limit
from app.core.config import settings
from app.db.postgres import get_db_connection
from app.scrapers.greenhouse import fetch_greenhouse_jobs
from app.scrapers.lever import fetch_lever_jobs
from app.scrapers.remoteok import fetch_remoteok_jobs
from app.scrapers.remotive import fetch_remotive_jobs
from app.services.embedding_service import backfill_job_embeddings
from app.services.ingestion_service import (
    ingest_adzuna_jobs,
    ingest_all_sources,
    ingest_normalized_jobs,
)

router = APIRouter(prefix="/ingest", tags=["ingest"])


@router.post("/adzuna")
def ingest_from_adzuna(
    queries: str | None = Query(
        None,
        description="Comma-separated search terms. Defaults to intern/new-grad software queries.",
    ),
    max_pages: int = Query(2, ge=1, le=10),
    _rate_limit: None = Depends(check_rate_limit),
    connection: Connection = Depends(get_db_connection),
) -> dict:
    if not settings.adzuna_app_id or not settings.adzuna_app_key:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Set ADZUNA_APP_ID and ADZUNA_APP_KEY in .env before ingestion.",
        )

    query_list = [q.strip() for q in queries.split(",") if q.strip()] if queries else None
    result = ingest_adzuna_jobs(connection, queries=query_list, max_pages_per_query=max_pages)
    result["embeddings"] = backfill_job_embeddings(connection)
    return result


@router.post("/remotive")
def ingest_from_remotive(
    _rate_limit: None = Depends(check_rate_limit),
    connection: Connection = Depends(get_db_connection),
) -> dict:
    result = ingest_normalized_jobs(
        connection, source_type="CUSTOM", source_name="remotive", fetch=fetch_remotive_jobs
    )
    result["embeddings"] = backfill_job_embeddings(connection)
    return result


@router.post("/remoteok")
def ingest_from_remoteok(
    _rate_limit: None = Depends(check_rate_limit),
    connection: Connection = Depends(get_db_connection),
) -> dict:
    result = ingest_normalized_jobs(
        connection, source_type="CUSTOM", source_name="remoteok", fetch=fetch_remoteok_jobs
    )
    result["embeddings"] = backfill_job_embeddings(connection)
    return result


@router.post("/greenhouse")
def ingest_from_greenhouse(
    _rate_limit: None = Depends(check_rate_limit),
    connection: Connection = Depends(get_db_connection),
) -> dict:
    result = ingest_normalized_jobs(
        connection, source_type="GREENHOUSE", source_name="greenhouse", fetch=fetch_greenhouse_jobs
    )
    result["embeddings"] = backfill_job_embeddings(connection)
    return result


@router.post("/lever")
def ingest_from_lever(
    _rate_limit: None = Depends(check_rate_limit),
    connection: Connection = Depends(get_db_connection),
) -> dict:
    result = ingest_normalized_jobs(
        connection, source_type="LEVER", source_name="lever", fetch=fetch_lever_jobs
    )
    result["embeddings"] = backfill_job_embeddings(connection)
    return result


@router.post("/all")
def ingest_from_all_sources(
    backfill: bool = Query(True, description="Generate embeddings after ingestion."),
    _rate_limit: None = Depends(check_rate_limit),
    connection: Connection = Depends(get_db_connection),
) -> dict:
    result = ingest_all_sources(connection)
    if backfill:
        result["embeddings"] = backfill_job_embeddings(connection, limit=1000)
    return result


@router.post("/embeddings")
def backfill_embeddings(
    limit: int = Query(200, ge=1, le=1000),
    _rate_limit: None = Depends(check_rate_limit),
    connection: Connection = Depends(get_db_connection),
) -> dict:
    return backfill_job_embeddings(connection, limit=limit)
