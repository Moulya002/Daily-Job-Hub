from datetime import datetime
from pydantic import BaseModel


class JobOut(BaseModel):
    id: str
    title: str
    company_name: str
    location: str | None = None
    work_mode: str | None = None
    summary: str
    posted_at: datetime | None = None


class SemanticSearchResult(BaseModel):
    id: str
    title: str
    company_name: str
    location: str | None = None
    work_mode: str | None = None
    summary: str
    score: float
