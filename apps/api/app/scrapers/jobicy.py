"""Jobicy remote jobs API (no key required).

https://jobicy.com/api/v2/remote-jobs
"""

import httpx

from app.scrapers.common import (
    NormalizedJob,
    infer_job_type,
    is_relevant,
    parse_iso_datetime,
    strip_html,
)

API_URL = "https://jobicy.com/api/v2/remote-jobs"

# Multiple fetches to cover tags relevant to early-career tech roles.
FETCH_PARAMS = [
    {"count": 50, "geo": "usa", "industry": "tech"},
    {"count": 50, "geo": "usa", "tag": "dev"},
    {"count": 50, "geo": "usa", "tag": "engineer"},
    {"count": 50, "geo": "usa", "tag": "data"},
    {"count": 50, "geo": "usa", "tag": "marketing"},
]


def _map_item(item: dict) -> NormalizedJob | None:
    title = (item.get("jobTitle") or "").strip()
    company = (item.get("companyName") or "").strip()
    url = (item.get("url") or "").strip()
    job_id = str(item.get("id") or "").strip()
    if not title or not company or not url or not job_id:
        return None

    description = strip_html(item.get("jobDescription") or item.get("jobExcerpt"))
    geo = (item.get("jobGeo") or "").strip()
    level = (item.get("jobLevel") or "").strip()
    industries = item.get("jobIndustry") or []
    keywords = list(industries) + ([level] if level else [])

    return NormalizedJob(
        external_id=job_id,
        title=title,
        company_name=company,
        description=description,
        application_url=url,
        source_url=url,
        location=geo or "Remote",
        work_mode="REMOTE",
        posted_at=parse_iso_datetime(item.get("pubDate")),
        job_type=infer_job_type(title, description),
        keywords=keywords,
    )


def fetch_jobicy_jobs() -> list[NormalizedJob]:
    collected: dict[str, NormalizedJob] = {}

    with httpx.Client(timeout=45.0, headers={"User-Agent": "DailyJobHub/1.0"}) as client:
        for params in FETCH_PARAMS:
            try:
                response = client.get(API_URL, params=params)
                response.raise_for_status()
            except httpx.HTTPError:
                continue
            for item in response.json().get("jobs") or []:
                mapped = _map_item(item)
                if mapped and is_relevant(mapped.title, mapped.description[:400]):
                    collected[mapped.external_id] = mapped

    return list(collected.values())
