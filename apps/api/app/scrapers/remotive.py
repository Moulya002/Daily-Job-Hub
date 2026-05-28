"""Remotive public API (no key required): https://remotive.com/api/remote-jobs"""

import httpx

from app.scrapers.common import (
    NormalizedJob,
    infer_job_type,
    is_relevant,
    parse_iso_datetime,
    strip_html,
)

REMOTIVE_URL = "https://remotive.com/api/remote-jobs"

DEFAULT_QUERIES = [
    "software intern",
    "new grad software engineer",
    "junior developer",
    "data analyst",
    "machine learning",
]

_JOB_TYPE_MAP = {
    "internship": "INTERN",
    "full_time": "FULL_TIME",
    "contract": "CONTRACT",
}


def _map_item(item: dict) -> NormalizedJob | None:
    title = (item.get("title") or "").strip()
    company = (item.get("company_name") or "").strip()
    url = (item.get("url") or "").strip()
    external_id = str(item.get("id") or "").strip()
    if not title or not company or not url or not external_id:
        return None

    description = strip_html(item.get("description"))
    category = (item.get("category") or "").strip()
    raw_type = (item.get("job_type") or "").strip().lower()
    job_type = _JOB_TYPE_MAP.get(raw_type) or infer_job_type(title, description)

    return NormalizedJob(
        external_id=external_id,
        title=title,
        company_name=company,
        description=description,
        application_url=url,
        source_url=url,
        location=(item.get("candidate_required_location") or "Remote").strip() or "Remote",
        posted_at=parse_iso_datetime(item.get("publication_date")),
        job_type=job_type,
        work_mode="REMOTE",
        keywords=[category] if category else [],
    )


def fetch_remotive_jobs(
    *,
    queries: list[str] | None = None,
    limit_per_query: int = 100,
) -> list[NormalizedJob]:
    search_queries = queries or DEFAULT_QUERIES
    collected: dict[str, NormalizedJob] = {}

    with httpx.Client(timeout=30.0, headers={"User-Agent": "DailyJobHub/1.0"}) as client:
        for query in search_queries:
            try:
                response = client.get(REMOTIVE_URL, params={"search": query, "limit": limit_per_query})
                response.raise_for_status()
            except httpx.HTTPError:
                continue
            for item in response.json().get("jobs", []) or []:
                mapped = _map_item(item)
                if mapped and is_relevant(mapped.title, " ".join(mapped.keywords)):
                    collected[mapped.external_id] = mapped

    return list(collected.values())
