from celery import Celery

from app.core.config import settings

celery_app = Celery(
    "daily_job_hub_workers",
    broker=settings.redis_url,
    backend=settings.redis_url,
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
        "app.workers.tasks.ingest_adzuna": {"queue": "scrapers"},
        "app.workers.tasks.generate_job_embeddings": {"queue": "embeddings"},
    },
)
