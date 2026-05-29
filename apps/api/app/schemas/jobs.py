from datetime import datetime

from pydantic import BaseModel


class JobOut(BaseModel):
    id: str
    title: str
    companyName: str
    location: str | None = None
    workMode: str | None = None
    summary: str
    jobType: str | None = None
    category: str = "Other"
    salaryMin: int | None = None
    salaryMax: int | None = None
    currency: str | None = None
    applyUrl: str | None = None
    postedAt: datetime | None = None


class SemanticSearchResult(BaseModel):
    id: str
    title: str
    companyName: str
    location: str | None = None
    workMode: str | None = None
    summary: str
    category: str = "Other"
    score: float
