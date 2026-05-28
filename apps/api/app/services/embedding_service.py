import logging
import re
import time

from psycopg import Connection

from app.core.config import settings
from app.repositories.ai_repository import upsert_job_embedding
from app.repositories.embeddings_repository import count_jobs_missing_embeddings, list_jobs_missing_embeddings
from app.services.ai_service import get_embedding

logger = logging.getLogger(__name__)

EMBEDDING_MODEL = settings.embedding_model
EMBEDDING_DIMENSIONS = settings.embedding_dimensions

_RATE_LIMIT_MAX_RETRIES = 5
_DEFAULT_RATE_LIMIT_WAIT_SECONDS = 30


def _is_rate_limit_error(exc: Exception) -> bool:
    text = f"{type(exc).__name__} {exc}"
    return "429" in text or "ResourceExhausted" in text or "exceeded your current quota" in text


def _retry_after_seconds(exc: Exception) -> float:
    match = re.search(r"retry_delay\s*{\s*seconds:\s*(\d+)", str(exc))
    if match:
        return float(match.group(1)) + 1
    match = re.search(r"retry in ([\d.]+)s", str(exc))
    if match:
        return float(match.group(1)) + 1
    return _DEFAULT_RATE_LIMIT_WAIT_SECONDS


def _vector_to_literal(vector: list[float]) -> str:
    return "[" + ",".join(str(value) for value in vector) + "]"


def _build_job_embedding_text(job: dict) -> str:
    title = job.get("title") or ""
    company = job.get("company_name") or ""
    location = job.get("location") or ""
    description = job.get("description") or ""
    return (
        f"Title: {title}\n"
        f"Company: {company}\n"
        f"Location: {location}\n"
        f"Description: {description}"
    ).strip()


def backfill_job_embeddings(
    connection: Connection,
    *,
    limit: int | None = None,
    model_name: str = EMBEDDING_MODEL,
) -> dict[str, int | str]:
    if not settings.gemini_api_key:
        return {
            "status": "SKIPPED",
            "reason": "GEMINI_API_KEY missing",
            "processed": 0,
            "remaining": count_jobs_missing_embeddings(connection, model_name=model_name),
        }

    batch_limit = limit or settings.embedding_backfill_limit
    jobs = list_jobs_missing_embeddings(connection, model_name=model_name, limit=batch_limit)

    processed = 0
    failed = 0
    last_error: str | None = None

    rpm = max(1, settings.embedding_requests_per_minute)
    min_interval = 60.0 / rpm

    for job in jobs:
        attempt = 0
        while True:
            started = time.monotonic()
            try:
                text = _build_job_embedding_text(job)
                vector = get_embedding(text)
                upsert_job_embedding(
                    connection,
                    job_id=job["id"],
                    model_name=model_name,
                    vector_literal=_vector_to_literal(vector),
                    dimensions=EMBEDDING_DIMENSIONS,
                )
                processed += 1
                # Pace requests to stay under the provider's per-minute quota.
                elapsed = time.monotonic() - started
                if min_interval > elapsed:
                    time.sleep(min_interval - elapsed)
                break
            except Exception as exc:  # noqa: BLE001 - surface real cause for debugging
                wait = _retry_after_seconds(exc)
                # Only retry short per-minute throttles; a long delay means a daily
                # quota was hit, so stop rather than hanging for many minutes.
                if _is_rate_limit_error(exc) and attempt < _RATE_LIMIT_MAX_RETRIES and wait <= 60:
                    attempt += 1
                    logger.warning(
                        "Rate limited on job %s (attempt %s); sleeping %.1fs",
                        job.get("id"),
                        attempt,
                        wait,
                    )
                    time.sleep(wait)
                    continue
                failed += 1
                last_error = f"{type(exc).__name__}: {exc}"
                logger.warning("Embedding failed for job %s: %s", job.get("id"), last_error)
                break

    remaining = count_jobs_missing_embeddings(connection, model_name=model_name)
    result: dict[str, int | str] = {
        "status": "SUCCEEDED",
        "processed": processed,
        "failed": failed,
        "remaining": remaining,
        "model_name": model_name,
    }
    if last_error:
        result["last_error"] = last_error
    return result
