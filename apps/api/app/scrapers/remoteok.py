"""RemoteOK public API (no key required): https://remoteok.com/api

The first array element is API metadata/legal notice and is skipped.
"""

import httpx

from app.scrapers.common import (
    NormalizedJob,
    infer_job_type,
    is_relevant,
    parse_iso_datetime,
    strip_html,
)

REMOTEOK_URL = "https://remoteok.com/api"


def _map_item(item: dict) -> NormalizedJob | None:
    title = (item.get("position") or item.get("title") or "").strip()
    company = (item.get("company") or "").strip()
    url = (item.get("url") or "").strip()
    external_id = str(item.get("id") or item.get("slug") or "").strip()
    if not title or not company or not url or not external_id:
        return None

    description = strip_html(item.get("description"))
    tags = [t for t in (item.get("tags") or []) if isinstance(t, str)]

    return NormalizedJob(
        external_id=external_id,
        title=title,
        company_name=company,
        description=description,
        application_url=url,
        source_url=url,
        location=(item.get("location") or "Remote").strip() or "Remote",
        salary_min=item.get("salary_min") if isinstance(item.get("salary_min"), int) else None,
        salary_max=item.get("salary_max") if isinstance(item.get("salary_max"), int) else None,
        posted_at=parse_iso_datetime(item.get("date")),
        job_type=infer_job_type(title, description),
        work_mode="REMOTE",
        keywords=tags[:10],
    )


def fetch_remoteok_jobs() -> list[NormalizedJob]:
    collected: dict[str, NormalizedJob] = {}
    with httpx.Client(timeout=30.0, headers={"User-Agent": "DailyJobHub/1.0"}) as client:
        try:
            response = client.get(REMOTEOK_URL)
            response.raise_for_status()
        except httpx.HTTPError:
            return []
        for item in response.json() or []:
            if not isinstance(item, dict) or not item.get("position"):
                continue
            mapped = _map_item(item)
            if mapped and is_relevant(mapped.title, " ".join(mapped.keywords)):
                collected[mapped.external_id] = mapped

    return list(collected.values())
