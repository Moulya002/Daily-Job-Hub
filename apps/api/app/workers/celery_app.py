from celery import Celery
from celery.schedules import crontab

from app.core.config import settings

celery_app = Celery(
    "daily_job_hub_workers",
    broker=settings.redis_url,
    backend=settings.redis_url,
    include=["app.workers.tasks"],
)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    enable_utc=True,
    task_acks_late=True,
    task_default_retry_delay=10,
    task_routes={
        "app.workers.tasks.scrape_all_sources": {"queue": "scrapers"},
        "app.workers.tasks.ingest_all_sources_task": {"queue": "scrapers"},
        "app.workers.tasks.ingest_adzuna": {"queue": "scrapers"},
        "app.workers.tasks.generate_job_embeddings": {"queue": "embeddings"},
    },
    # Scheduled (beat) jobs so the board refreshes automatically.
    beat_schedule={
        # Full ingest + embeddings twice daily (06:00 and 18:00 UTC).
        "daily-ingest-morning": {
            "task": "app.workers.tasks.ingest_all_sources_task",
            "schedule": crontab(hour=6, minute=0),
            "kwargs": {"embed": True, "embed_limit": 500},
        },
        "daily-ingest-evening": {
            "task": "app.workers.tasks.ingest_all_sources_task",
            "schedule": crontab(hour=18, minute=0),
            "kwargs": {"embed": True, "embed_limit": 500},
        },
        # Top up any remaining embeddings every 30 minutes (rate-limit friendly).
        "embedding-backfill-topup": {
            "task": "app.workers.tasks.generate_job_embeddings",
            "schedule": crontab(minute="*/30"),
            "kwargs": {"limit": 100},
        },
    },
)
