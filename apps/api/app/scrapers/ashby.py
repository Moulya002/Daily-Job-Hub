"""Ashby public job board API (no key required).

Per-company boards: https://api.ashbyhq.com/posting-api/job-board/{slug}
"""

import httpx

from app.scrapers.common import (
    NormalizedJob,
    infer_job_type,
    is_relevant,
    parse_iso_datetime,
    strip_html,
)

BOARD_URL = "https://api.ashbyhq.com/posting-api/job-board/{slug}"

DEFAULT_COMPANIES = [
    "openai",
    "anthropic",
    "notion",
    "linear",
    "retool",
    "vercel",
    "cursor",
    "perplexity",
    "ramp",
    "mercury",
    "deel",
    "rippling",
    "figma",
    "cognition",
    "harvey",
    "cohere",
    "mistral",
    "scale",
    "anduril",
    "palantir",
    "snowflake",
    "databricks",
    "coinbase",
    "stripe",
    "flexport",
    "gusto",
    "brex",
    "plaid",
    "affirm",
    "chime",
    "sofi",
    "discord",
    "runway",
    "elevenlabs",
    "character",
    "sierra",
    "glean",
]


def _map_item(item: dict, company: str) -> NormalizedJob | None:
    title = (item.get("title") or "").strip()
    external_id = str(item.get("id") or "").strip()
    url = (item.get("jobUrl") or item.get("applyUrl") or "").strip()
    if not title or not external_id or not url:
        return None

    description = strip_html(item.get("descriptionHtml") or item.get("descriptionPlain"))
    location = (item.get("location") or "").strip() or None
    department = (item.get("department") or "").strip()
    team = (item.get("team") or "").strip()
    keywords = [x for x in (department, team) if x]

    return NormalizedJob(
        external_id=external_id,
        title=title,
        company_name=company,
        description=description,
        application_url=url,
        source_url=url,
        location=location,
        posted_at=parse_iso_datetime(item.get("publishedAt")),
        job_type=infer_job_type(title, description),
        keywords=keywords,
    )


def fetch_ashby_jobs(*, companies: list[str] | None = None) -> list[NormalizedJob]:
    slugs = list(dict.fromkeys(companies or DEFAULT_COMPANIES))
    collected: dict[str, NormalizedJob] = {}

    with httpx.Client(timeout=45.0, headers={"User-Agent": "DailyJobHub/1.0"}) as client:
        for slug in slugs:
            try:
                response = client.get(BOARD_URL.format(slug=slug))
                response.raise_for_status()
            except httpx.HTTPError:
                continue
            company = slug.replace("-", " ").title()
            for item in response.json().get("jobs", []) or []:
                mapped = _map_item(item, company)
                if mapped and is_relevant(mapped.title, mapped.description[:500]):
                    collected[f"{slug}:{mapped.external_id}"] = mapped

    return list(collected.values())
