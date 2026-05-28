from enum import StrEnum


class Role(StrEnum):
    USER = "USER"
    ADMIN = "ADMIN"


class JobType(StrEnum):
    INTERN = "INTERN"
    NEW_GRAD = "NEW_GRAD"
    FULL_TIME = "FULL_TIME"
    CONTRACT = "CONTRACT"


class WorkMode(StrEnum):
    REMOTE = "REMOTE"
    HYBRID = "HYBRID"
    ONSITE = "ONSITE"


class EmploymentLevel(StrEnum):
    ENTRY = "ENTRY"
    ASSOCIATE = "ASSOCIATE"
    MID = "MID"
    SENIOR = "SENIOR"


class JobStatus(StrEnum):
    ACTIVE = "ACTIVE"
    CLOSED = "CLOSED"
    EXPIRED = "EXPIRED"


class ApplicationSource(StrEnum):
    PLATFORM = "PLATFORM"
    COMPANY_SITE = "COMPANY_SITE"
    REFERRAL = "REFERRAL"
    RECRUITER = "RECRUITER"


class ApplicationStatus(StrEnum):
    SAVED = "SAVED"
    APPLIED = "APPLIED"
    OA = "OA"
    PHONE_SCREEN = "PHONE_SCREEN"
    INTERVIEW = "INTERVIEW"
    OFFER = "OFFER"
    REJECTED = "REJECTED"


class ResumeStatus(StrEnum):
    PROCESSING = "PROCESSING"
    READY = "READY"
    FAILED = "FAILED"


class AlertChannel(StrEnum):
    EMAIL = "EMAIL"
    IN_APP = "IN_APP"
    BOTH = "BOTH"


class AlertFrequency(StrEnum):
    INSTANT = "INSTANT"
    DAILY = "DAILY"
    WEEKLY = "WEEKLY"


class MessageType(StrEnum):
    COVER_LETTER = "COVER_LETTER"
    RECRUITER_OUTREACH = "RECRUITER_OUTREACH"
    REFERRAL_REQUEST = "REFERRAL_REQUEST"
    THANK_YOU_NOTE = "THANK_YOU_NOTE"


class MessageStatus(StrEnum):
    DRAFT = "DRAFT"
    GENERATED = "GENERATED"
    EDITED = "EDITED"
    SENT = "SENT"


class EmbeddingEntityType(StrEnum):
    JOB = "JOB"
    RESUME = "RESUME"
    USER_PROFILE = "USER_PROFILE"
    ALERT_QUERY = "ALERT_QUERY"


class ScrapeSourceType(StrEnum):
    GREENHOUSE = "GREENHOUSE"
    LEVER = "LEVER"
    ASHBY = "ASHBY"
    YC = "YC"
    CUSTOM = "CUSTOM"


class ScrapeRunStatus(StrEnum):
    QUEUED = "QUEUED"
    RUNNING = "RUNNING"
    SUCCEEDED = "SUCCEEDED"
    PARTIAL = "PARTIAL"
    FAILED = "FAILED"
