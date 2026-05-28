"""Shared types and helpers for all job-board ingestion sources."""

from dataclasses import dataclass, field
from datetime import datetime
import hashlib
import re

# Keywords used to keep ingestion focused on intern / new-grad / early-career tech roles.
# Kept specific to avoid false positives like "AI Sales" or "Data Entry".
RELEVANT_KEYWORDS = (
    "intern",
    "internship",
    "co-op",
    "co op",
    "new grad",
    "new graduate",
    "early career",
    "entry level",
    "entry-level",
    "graduate",
    "junior",
    "software",
    "engineer",
    "developer",
    "programmer",
    "data scientist",
    "data analyst",
    "data engineer",
    "machine learning",
    "artificial intelligence",
    "frontend",
    "front-end",
    "backend",
    "back-end",
    "full stack",
    "full-stack",
    "devops",
    "web developer",
    "mobile developer",
    "ios developer",
    "android developer",
)

_TAG_RE = re.compile(r"<[^>]+>")
_WS_RE = re.compile(r"\s+")


@dataclass
class NormalizedJob:
    external_id: str
    title: str
    company_name: str
    description: str
    application_url: str
    source_url: str
    location: str | None = None
    salary_min: int | None = None
    salary_max: int | None = None
    posted_at: datetime | None = None
    job_type: str = "FULL_TIME"
    work_mode: str | None = None
    keywords: list[str] = field(default_factory=list)


def normalize_text(value: str) -> str:
    return _WS_RE.sub(" ", value.strip().lower())


def strip_html(value: str | None) -> str:
    if not value:
        return ""
    text = _TAG_RE.sub(" ", value)
    text = (
        text.replace("&amp;", "&")
        .replace("&lt;", "<")
        .replace("&gt;", ">")
        .replace("&quot;", '"')
        .replace("&#39;", "'")
        .replace("&nbsp;", " ")
    )
    return _WS_RE.sub(" ", text).strip()


def infer_job_type(title: str, description: str = "") -> str:
    text = f"{title} {description}".lower()
    if any(token in text for token in ("intern", "internship", "co-op", "co op")):
        return "INTERN"
    if any(token in text for token in ("new grad", "new graduate", "entry level", "entry-level", "early career")):
        return "NEW_GRAD"
    return "FULL_TIME"


def is_relevant(title: str, extra: str = "") -> bool:
    text = f"{title} {extra}".lower()
    return any(token in text for token in RELEVANT_KEYWORDS)


def parse_iso_datetime(raw: str | None) -> datetime | None:
    if not raw:
        return None
    try:
        return datetime.fromisoformat(raw.replace("Z", "+00:00"))
    except (ValueError, AttributeError):
        return None


def build_dedupe_hash(job: NormalizedJob) -> str:
    raw = f"{normalize_text(job.company_name)}|{normalize_text(job.title)}|{job.application_url}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()
