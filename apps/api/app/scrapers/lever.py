"""Lever public postings API (no key required).

Per-company boards: https://api.lever.co/v0/postings/{slug}?mode=json
"""

from datetime import UTC, datetime

import httpx

from app.scrapers.common import (
    NormalizedJob,
    infer_job_type,
    is_relevant,
    strip_html,
)

POSTINGS_URL = "https://api.lever.co/v0/postings/{slug}?mode=json"

# Well-known companies that host on Lever. Override via LEVER_COMPANIES.
DEFAULT_COMPANIES = [
    "netflix",
    "spotify",
    "ramp",
    "plaid",
    "scaleai",
    "voleon",
    "kandji",
    "fivetran",
    "attentive",
    "mux",
    "lyft",
    "pinterest",
    "reddit",
    "robinhood",
    "affirm",
    "chime",
    "sofi",
    "gusto",
    "rippling",
    "deel",
    "remote",
    "gitlab",
    "hashicorp",
    "confluent",
    "cockroachlabs",
    "amplitude",
    "segment",
    "heap",
    "mixpanel",
    "launchdarkly",
    "vercel",
    "netlify",
    "render",
    "supabase",
    "planetscale",
    "neon",
    "retool",
    "airtable",
    "notion",
    "figma",
    "canva",
    "miro",
    "loom",
    "calendly",
    "grammarly",
    "duolingo",
    "coursera",
    "khanacademy",
    "stripe",
    "square",
    "block",
    "paypal",
    "coinbase",
    "databricks",
    "snowflake",
    "palantir",
    "anduril",
    "shieldai",
    "skydio",
    "waymo",
    "rivian",
    "tesla",
    "openai",
]


def _map_item(item: dict, company: str) -> NormalizedJob | None:
    title = (item.get("text") or "").strip()
    url = (item.get("hostedUrl") or item.get("applyUrl") or "").strip()
    external_id = str(item.get("id") or "").strip()
    if not title or not url or not external_id:
        return None

    description = strip_html(item.get("description") or item.get("descriptionPlain"))
    categories = item.get("categories") or {}
    location = (categories.get("location") or "").strip() or None
    team = (categories.get("team") or "").strip()

    posted_at = None
    created = item.get("createdAt")
    if isinstance(created, (int, float)):
        posted_at = datetime.fromtimestamp(created / 1000, tz=UTC)

    return NormalizedJob(
        external_id=external_id,
        title=title,
        company_name=company,
        description=description,
        application_url=url,
        source_url=url,
        location=location,
        posted_at=posted_at,
        job_type=infer_job_type(title, description),
        keywords=[team] if team else [],
    )


def fetch_lever_jobs(*, companies: list[str] | None = None) -> list[NormalizedJob]:
    slugs = companies or DEFAULT_COMPANIES
    collected: dict[str, NormalizedJob] = {}

    with httpx.Client(timeout=30.0, headers={"User-Agent": "DailyJobHub/1.0"}) as client:
        for slug in slugs:
            try:
                response = client.get(POSTINGS_URL.format(slug=slug))
                response.raise_for_status()
            except httpx.HTTPError:
                continue
            company = slug.replace("-", " ").title()
            for item in response.json() or []:
                mapped = _map_item(item, company)
                if mapped and is_relevant(mapped.title, " ".join(mapped.keywords)):
                    collected[f"{slug}:{mapped.external_id}"] = mapped

    return list(collected.values())
