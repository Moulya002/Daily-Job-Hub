import hashlib
import re
from dataclasses import dataclass
from datetime import datetime

import httpx

from app.core.config import settings
from app.scrapers.common import strip_html

ADZUNA_BASE = "https://api.adzuna.com/v1/api/jobs"

DEFAULT_QUERIES = [
    "software engineer internship",
    "software intern",
    "new grad software engineer",
    "entry level software engineer",
    "machine learning intern",
    "data science intern",
    "backend intern",
    "frontend intern",
    "full stack intern",
    "computer science intern",
    "graduate software engineer",
    "university graduate engineer",
    "associate software engineer",
    "junior software developer",
    "data engineer intern",
    "devops intern",
    "product engineer intern",
    "ai engineer intern",
    "2026 software engineer",
    "campus software engineer",
]


@dataclass
class AdzunaJob:
    external_id: str
    title: str
    company_name: str
    description: str
    application_url: str
    source_url: str
    location: str | None
    salary_min: int | None
    salary_max: int | None
    posted_at: datetime | None
    job_type: str
    keywords: list[str]


def _normalize_text(value: str) -> str:
    return re.sub(r"\s+", " ", value.strip().lower())


def _infer_job_type(title: str, description: str) -> str:
    text = f"{title} {description}".lower()
    if any(token in text for token in ("intern", "internship", "co-op", "co op")):
        return "INTERN"
    if any(token in text for token in ("new grad", "new graduate", "entry level", "early career")):
        return "NEW_GRAD"
    return "FULL_TIME"


def _parse_posted_at(raw: str | None) -> datetime | None:
    if not raw:
        return None
    try:
        return datetime.fromisoformat(raw.replace("Z", "+00:00"))
    except ValueError:
        return None


def _map_result(item: dict) -> AdzunaJob | None:
    title = (item.get("title") or "").strip()
    company = ((item.get("company") or {}).get("display_name") or "").strip()
    description = strip_html(item.get("description"))
    redirect_url = (item.get("redirect_url") or item.get("url") or "").strip()
    external_id = str(item.get("id") or "").strip()

    if not title or not company or not redirect_url or not external_id:
        return None

    location_data = item.get("location") or {}
    location = (location_data.get("display_name") or "").strip() or None
    category_label = ((item.get("category") or {}).get("label") or "").strip()
    keywords = [category_label] if category_label else []

    return AdzunaJob(
        external_id=external_id,
        title=title,
        company_name=company,
        description=description,
        application_url=redirect_url,
        source_url=redirect_url,
        location=location,
        salary_min=item.get("salary_min"),
        salary_max=item.get("salary_max"),
        posted_at=_parse_posted_at(item.get("created")),
        job_type=_infer_job_type(title, description),
        keywords=keywords,
    )


def fetch_adzuna_jobs(
    *,
    queries: list[str] | None = None,
    max_pages_per_query: int | None = None,
) -> list[AdzunaJob]:
    if not settings.adzuna_app_id or not settings.adzuna_app_key:
        raise ValueError("ADZUNA_APP_ID and ADZUNA_APP_KEY must be set in environment.")

    search_queries = queries or DEFAULT_QUERIES
    pages = max_pages_per_query or settings.adzuna_max_pages_per_query
    country = settings.adzuna_country
    collected: dict[str, AdzunaJob] = {}

    with httpx.Client(timeout=30.0) as client:
        for query in search_queries:
            for page in range(1, pages + 1):
                response = client.get(
                    f"{ADZUNA_BASE}/{country}/search/{page}",
                    params={
                        "app_id": settings.adzuna_app_id,
                        "app_key": settings.adzuna_app_key,
                        "what": query,
                        "results_per_page": 50,
                        "content-type": "application/json",
                    },
                )
                response.raise_for_status()
                payload = response.json()
                results = payload.get("results") or []
                if not results:
                    break

                for item in results:
                    mapped = _map_result(item)
                    if mapped:
                        collected[mapped.external_id] = mapped

    return list(collected.values())


def build_dedupe_hash(job: AdzunaJob) -> str:
    raw = f"{_normalize_text(job.company_name)}|{_normalize_text(job.title)}|{job.application_url}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()
