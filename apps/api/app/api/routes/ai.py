from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from psycopg import Connection

from app.api.deps.rate_limit import check_rate_limit
from app.db.postgres import get_db_connection
from app.schemas.ai import (
    GenerateMessageRequest,
    GenerateMessageResponse,
    ResumeAnalysisRequest,
    ResumeAnalysisResponse,
    ResumeUploadResponse,
)
from app.services.pdf_service import extract_skills_from_text, extract_text_from_pdf_bytes
from app.services.ai_service import generate_text
from app.services.resume_service import analyze_resume_against_job

router = APIRouter(prefix="/ai", tags=["ai"])


@router.post("/resume/analyze", response_model=ResumeAnalysisResponse)
async def analyze_resume(
    payload: ResumeAnalysisRequest,
    _rate_limit: None = Depends(check_rate_limit),
    connection: Connection = Depends(get_db_connection),
) -> ResumeAnalysisResponse:
    return analyze_resume_against_job(
        connection,
        user_id=payload.user_id,
        resume_id=payload.resume_id,
        job_id=payload.job_id,
        job_description=payload.job_description,
        resume_text=payload.resume_text,
    )


@router.post("/resume/upload", response_model=ResumeUploadResponse)
async def upload_resume(
    file: UploadFile = File(...),
    _rate_limit: None = Depends(check_rate_limit),
) -> ResumeUploadResponse:
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Only PDF files are supported.")

    raw = await file.read()
    if len(raw) > 5 * 1024 * 1024:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="File too large (max 5MB).")

    text = extract_text_from_pdf_bytes(raw)
    return ResumeUploadResponse(text=text, extracted_skills=extract_skills_from_text(text))


@router.post("/messages/generate", response_model=GenerateMessageResponse)
async def generate_message(
    payload: GenerateMessageRequest,
    _rate_limit: None = Depends(check_rate_limit),
) -> GenerateMessageResponse:
    prompt = f"""
Write a concise {payload.message_type} message for:
Company: {payload.company_name}
Role: {payload.role_title}
Background: {payload.user_background}
"""
    return GenerateMessageResponse(output=generate_text(prompt))
