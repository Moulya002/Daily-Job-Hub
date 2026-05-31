"""Arbeitnow public job board API (no key required).

https://www.arbeitnow.com/api/job-board-api
"""

import httpx

from app.scrapers.common import (
    NormalizedJob,
    infer_job_type,
    is_relevant,
    parse_iso_datetime,
    strip_html,
)

API_URL = "https://www.arbeitnow.com/api/job-board-api"
MAX_PAGES = 15


def _map_item(item: dict) -> NormalizedJob | None:
    title = (item.get("title") or "").strip()
    company = (item.get("company_name") or "").strip()
    url = (item.get("url") or "").strip()
    slug = (item.get("slug") or "").strip()
    if not title or not company or not url:
        return None

    description = strip_html(item.get("description"))
    location = (item.get("location") or "").strip() or None
    if item.get("remote"):
        location = f"{location} (Remote)" if location else "Remote"

    return NormalizedJob(
        external_id=slug or url,
        title=title,
        company_name=company,
        description=description,
        application_url=url,
        source_url=url,
        location=location,
        posted_at=parse_iso_datetime(item.get("created_at")),
        job_type=infer_job_type(title, description),
        keywords=item.get("tags") or [],
    )


def fetch_arbeitnow_jobs() -> list[NormalizedJob]:
    collected: dict[str, NormalizedJob] = {}
    next_url: str | None = API_URL

    with httpx.Client(timeout=30.0, headers={"User-Agent": "DailyJobHub/1.0"}) as client:
        for _ in range(MAX_PAGES):
            if not next_url:
                break
            try:
                response = client.get(next_url)
                response.raise_for_status()
            except httpx.HTTPError:
                break
            payload = response.json()
            for item in payload.get("data") or []:
                mapped = _map_item(item)
                if mapped and is_relevant(mapped.title, mapped.description[:400]):
                    collected[mapped.external_id] = mapped
            next_url = (payload.get("links") or {}).get("next")

    return list(collected.values())
