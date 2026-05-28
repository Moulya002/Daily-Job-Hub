"""Greenhouse public job board API (no key required).

Per-company boards: https://boards-api.greenhouse.io/v1/boards/{slug}/jobs?content=true
This is where many tech recruiters/HR teams post roles directly.
"""

import httpx

from app.scrapers.common import (
    NormalizedJob,
    infer_job_type,
    is_relevant,
    parse_iso_datetime,
    strip_html,
)

BOARD_JOBS_URL = "https://boards-api.greenhouse.io/v1/boards/{slug}/jobs?content=true"
BOARD_META_URL = "https://boards-api.greenhouse.io/v1/boards/{slug}"

# Well-known companies that host on Greenhouse. Override via GREENHOUSE_COMPANIES.
DEFAULT_COMPANIES = [
    "stripe",
    "databricks",
    "robinhood",
    "coinbase",
    "figma",
    "gitlab",
    "cloudflare",
    "brex",
    "plaid",
    "dropbox",
    "reddit",
    "discord",
    "instacart",
    "doordash",
    "airtable",
    "asana",
    "ramp",
    "samsara",
    "flexport",
    "benchling",
]


def _company_name(client: httpx.Client, slug: str) -> str:
    try:
        response = client.get(BOARD_META_URL.format(slug=slug))
        response.raise_for_status()
        name = (response.json().get("name") or "").strip()
        if name:
            return name
    except httpx.HTTPError:
        pass
    return slug.replace("-", " ").title()


def _map_item(item: dict, company: str) -> NormalizedJob | None:
    title = (item.get("title") or "").strip()
    url = (item.get("absolute_url") or "").strip()
    external_id = str(item.get("id") or "").strip()
    if not title or not url or not external_id:
        return None

    description = strip_html(item.get("content"))
    location = ((item.get("location") or {}).get("name") or "").strip() or None

    return NormalizedJob(
        external_id=external_id,
        title=title,
        company_name=company,
        description=description,
        application_url=url,
        source_url=url,
        location=location,
        posted_at=parse_iso_datetime(item.get("updated_at")),
        job_type=infer_job_type(title, description),
        keywords=[],
    )


def fetch_greenhouse_jobs(*, companies: list[str] | None = None) -> list[NormalizedJob]:
    slugs = companies or DEFAULT_COMPANIES
    collected: dict[str, NormalizedJob] = {}

    with httpx.Client(timeout=30.0, headers={"User-Agent": "DailyJobHub/1.0"}) as client:
        for slug in slugs:
            try:
                response = client.get(BOARD_JOBS_URL.format(slug=slug))
                response.raise_for_status()
            except httpx.HTTPError:
                continue
            company = _company_name(client, slug)
            for item in response.json().get("jobs", []) or []:
                mapped = _map_item(item, company)
                if mapped and is_relevant(mapped.title):
                    collected[f"{slug}:{mapped.external_id}"] = mapped

    return list(collected.values())
