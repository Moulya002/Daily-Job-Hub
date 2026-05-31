"""Y Combinator / Work at a Startup jobs via community hiring JSON feed.

Source: https://devasheeshg.github.io/yc-api/companies/hiring.json
Updated daily; no API key required.
"""

import re

import httpx

from app.scrapers.common import NormalizedJob, infer_job_type, is_relevant

HIRING_URL = "https://devasheeshg.github.io/yc-api/companies/hiring.json"

_SALARY_RE = re.compile(r"\$[\d,]+K?")


def _parse_salary_range(raw: str | None) -> tuple[int | None, int | None]:
    if not raw:
        return None, None
    parts = _SALARY_RE.findall(raw.upper().replace(",", ""))
    values: list[int] = []
    for part in parts:
        num = part.replace("$", "").replace("K", "")
        try:
            values.append(int(float(num) * 1000))
        except ValueError:
            continue
    if not values:
        return None, None
    if len(values) == 1:
        return values[0], values[0]
    return min(values), max(values)


def _map_job_type(yc_type: str | None, title: str, experience: str | None) -> str:
    text = f"{title} {experience or ''}".lower()
    if yc_type and "intern" in yc_type.lower():
        return "INTERN"
    if any(t in text for t in ("new grad", "new grads ok", "0-1 years", "0-2 years")):
        return "NEW_GRAD"
    return infer_job_type(title, experience or "")


def fetch_yc_jobs() -> list[NormalizedJob]:
    collected: dict[str, NormalizedJob] = {}

    with httpx.Client(timeout=120.0, headers={"User-Agent": "DailyJobHub/1.0"}) as client:
        response = client.get(HIRING_URL)
        response.raise_for_status()
        companies = response.json()

    for company in companies:
        company_name = (company.get("name") or "").strip()
        if not company_name:
            continue
        for job in company.get("jobs") or []:
            title = (job.get("title") or "").strip()
            url = (job.get("url") or "").strip()
            job_id = str(job.get("id") or "").strip()
            if not title or not url or not job_id:
                continue
            if not is_relevant(title):
                continue

            location = (job.get("location") or "").strip() or None
            skills = job.get("skills") or []
            role = job.get("role") or ""
            description_parts = [
                f"Company: {company_name}",
                f"Role: {role}",
                f"Type: {job.get('type') or ''}",
                f"Experience: {job.get('experience') or ''}",
                f"Visa: {job.get('visa') or ''}",
                f"Skills: {', '.join(skills) if skills else ''}",
            ]
            description = "\n".join(p for p in description_parts if p.strip())
            salary_min, salary_max = _parse_salary_range(job.get("salary_range"))

            mapped = NormalizedJob(
                external_id=job_id,
                title=title,
                company_name=company_name,
                description=description,
                application_url=url,
                source_url=url,
                location=location,
                salary_min=salary_min,
                salary_max=salary_max,
                job_type=_map_job_type(job.get("type"), title, job.get("experience")),
                keywords=[role] if role else [],
            )
            collected[f"yc:{job_id}"] = mapped

    return list(collected.values())
