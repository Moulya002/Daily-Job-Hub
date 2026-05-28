from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import (
    AlertChannel,
    AlertFrequency,
    ApplicationSource,
    ApplicationStatus,
    EmbeddingEntityType,
    EmploymentLevel,
    JobStatus,
    JobType,
    MessageStatus,
    MessageType,
    ResumeStatus,
    Role,
    ScrapeRunStatus,
    ScrapeSourceType,
    WorkMode,
)


class ORMBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class UserModel(ORMBase):
    id: str
    email: str
    normalized_email: str
    role: Role
    name: str | None = None
    image: str | None = None
    university: str | None = None
    graduation_year: int | None = None
    target_roles: list[str] = Field(default_factory=list)
    target_locations: list[str] = Field(default_factory=list)
    needs_sponsorship: bool = False
    is_onboarded: bool = False
    preferences: dict[str, Any] | None = None
    created_at: datetime
    updated_at: datetime


class CompanyModel(ORMBase):
    id: str
    name: str
    normalized_name: str
    website: str | None = None
    careers_page_url: str | None = None
    sponsorship_policy: str | None = None
    tech_stack: list[str] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime


class JobModel(ORMBase):
    id: str
    source_type: ScrapeSourceType
    source_name: str
    source_url: str
    application_url: str
    title: str
    normalized_title: str
    description: str
    location: str | None = None
    location_region: str | None = None
    work_mode: WorkMode | None = None
    employment_level: EmploymentLevel | None = None
    visa_sponsorship: bool | None = None
    tech_stack: list[str] = Field(default_factory=list)
    keywords: list[str] = Field(default_factory=list)
    job_type: JobType
    status: JobStatus
    posted_at: datetime | None = None
    expires_at: datetime | None = None
    dedupe_hash: str
    company_id: str
    created_at: datetime
    updated_at: datetime


class ResumeModel(ORMBase):
    id: str
    file_name: str
    file_url: str
    file_size_bytes: int
    mime_type: str = "application/pdf"
    checksum_sha256: str
    status: ResumeStatus
    parsed_text: str | None = None
    extracted_skills: list[str] = Field(default_factory=list)
    extracted_projects: dict[str, Any] | None = None
    extracted_education: dict[str, Any] | None = None
    extracted_experience: dict[str, Any] | None = None
    user_id: str
    created_at: datetime
    updated_at: datetime


class ApplicationModel(ORMBase):
    id: str
    status: ApplicationStatus
    source: ApplicationSource
    user_id: str
    job_id: str
    notes: str | None = None
    applied_at: datetime | None = None
    deadline: datetime | None = None
    next_step_at: datetime | None = None
    rejection_reason: str | None = None
    created_at: datetime
    updated_at: datetime


class SavedJobModel(ORMBase):
    id: str
    user_id: str
    job_id: str
    preference_score: float | None = None
    created_at: datetime


class EmbeddingModel(ORMBase):
    id: str
    entity_type: EmbeddingEntityType
    model_name: str
    dimensions: int = 1536
    metadata: dict[str, Any] | None = None
    job_id: str | None = None
    resume_id: str | None = None
    user_id: str | None = None
    alert_id: str | None = None
    created_at: datetime
    updated_at: datetime


class ResumeAnalysisModel(ORMBase):
    id: str
    ats_score: int
    match_percentage: int
    missing_skills: list[str] = Field(default_factory=list)
    suggestions: list[str] = Field(default_factory=list)
    strengths: list[str] = Field(default_factory=list)
    model_name: str
    user_id: str
    resume_id: str
    job_id: str | None = None
    created_at: datetime


class AlertModel(ORMBase):
    id: str
    name: str
    query: str
    channel: AlertChannel
    frequency: AlertFrequency
    min_match_score: float = 0.65
    is_enabled: bool = True
    last_triggered_at: datetime | None = None
    user_id: str
    created_at: datetime
    updated_at: datetime


class AlertDeliveryModel(ORMBase):
    id: str
    alert_id: str
    user_id: str
    channel: AlertChannel
    jobs_count: int
    delivered_at: datetime
    opened_at: datetime | None = None
    clicked_at: datetime | None = None


class RecruiterMessageModel(ORMBase):
    id: str
    type: MessageType
    status: MessageStatus
    user_id: str
    prompt_input: str
    output_text: str
    company_name: str | None = None
    role_title: str | None = None
    model_name: str | None = None
    tokens_prompt: int | None = None
    tokens_output: int | None = None
    created_at: datetime


class InterviewModel(ORMBase):
    id: str
    application_id: str
    round_name: str
    interviewer: str | None = None
    scheduled_at: datetime | None = None
    completed_at: datetime | None = None
    feedback: str | None = None
    rating: int | None = None
    created_at: datetime
    updated_at: datetime


class ApplicationStatusHistoryModel(ORMBase):
    id: str
    application_id: str
    from_status: ApplicationStatus | None = None
    to_status: ApplicationStatus
    reason: str | None = None
    changed_at: datetime


class ScrapeRunModel(ORMBase):
    id: str
    source_type: ScrapeSourceType
    source_name: str
    status: ScrapeRunStatus
    jobs_seen: int = 0
    jobs_inserted: int = 0
    jobs_updated: int = 0
    jobs_archived: int = 0
    error_message: str | None = None
    started_at: datetime | None = None
    completed_at: datetime | None = None
    created_at: datetime


class JobScrapeEventModel(ORMBase):
    id: str
    job_id: str
    scrape_run_id: str | None = None
    event_type: str
    source_url: str | None = None
    payload: dict[str, Any] | None = None
    created_at: datetime


class RecommendationLogModel(ORMBase):
    id: str
    user_id: str
    strategy: str
    latency_ms: int | None = None
    result_count: int = 0
    requested_at: datetime
