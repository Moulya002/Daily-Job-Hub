from pydantic import BaseModel


class ResumeAnalysisRequest(BaseModel):
    user_id: str
    resume_id: str
    job_id: str | None = None
    job_description: str
    resume_text: str


class ResumeAnalysisResponse(BaseModel):
    ats_score: int
    match_percentage: int
    missing_skills: list[str]
    suggestions: list[str]


class ResumeUploadResponse(BaseModel):
    text: str
    extracted_skills: list[str]


class GenerateMessageRequest(BaseModel):
    message_type: str
    company_name: str
    role_title: str
    user_background: str


class GenerateMessageResponse(BaseModel):
    output: str
