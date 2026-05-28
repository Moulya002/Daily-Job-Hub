from datetime import datetime

from pydantic import BaseModel


class SavedJobItem(BaseModel):
    job_id: str
    created_at: datetime


class ApplicationItem(BaseModel):
    job_id: str
    status: str
    updated_at: datetime


class ActionResponse(BaseModel):
    success: bool
