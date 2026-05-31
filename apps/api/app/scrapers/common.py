"""Shared types and helpers for all job-board ingestion sources."""

import hashlib
import html
import re
from dataclasses import dataclass, field
from datetime import datetime

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

_TAG_RE = re.compile(r"<[^>]+>", re.DOTALL)
_SCRIPT_STYLE_RE = re.compile(r"<(script|style)[^>]*>.*?</\1>", re.DOTALL | re.IGNORECASE)
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
    """Turn HTML job descriptions into plain text for storage and display."""
    if not value:
        return ""
    text = html.unescape(value)
    text = _SCRIPT_STYLE_RE.sub(" ", text)
    text = _TAG_RE.sub(" ", text)
    # Some feeds double-encode entities after tags are removed.
    text = html.unescape(text)
    return _WS_RE.sub(" ", text).strip()


def plain_text_summary(value: str | None, *, max_len: int = 240) -> str:
    """Plain-text snippet for cards (never mid-tag; strips HTML first)."""
    cleaned = strip_html(value)
    if len(cleaned) <= max_len:
        return cleaned
    snippet = cleaned[:max_len]
    if " " in snippet:
        snippet = snippet.rsplit(" ", 1)[0]
    return f"{snippet}…"


def infer_job_type(title: str, description: str = "") -> str:
    text = f"{title} {description}".lower()
    if any(token in text for token in ("intern", "internship", "co-op", "co op")):
        return "INTERN"
    new_grad_tokens = (
        "new grad",
        "new graduate",
        "entry level",
        "entry-level",
        "early career",
        "university grad",
        "college grad",
        "campus hire",
        "campus recruiting",
        "2026 grad",
        "2027 grad",
        "recent graduate",
        "associate software",
        "associate engineer",
        "rotational program",
    )
    if any(token in text for token in new_grad_tokens):
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
