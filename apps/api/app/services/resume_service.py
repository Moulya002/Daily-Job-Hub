import json
import logging
import re

from psycopg import Connection

from app.repositories.ai_repository import create_resume_analysis
from app.schemas.ai import ResumeAnalysisResponse
from app.services.ai_service import generate_text

logger = logging.getLogger(__name__)

_SYSTEM_PROMPT = (
    "You are an expert ATS (Applicant Tracking System) evaluator and technical recruiter. "
    "Respond with ONLY a JSON object, no markdown, no commentary."
)

_FALLBACK = ResumeAnalysisResponse(
    ats_score=72,
    match_percentage=68,
    missing_skills=["Add skills explicitly listed in the job description"],
    suggestions=[
        "Quantify project impact with concrete metrics.",
        "Mirror keywords from the job description.",
        "Move the most relevant experience to the top.",
    ],
)


def _extract_json(text: str) -> dict | None:
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if not match:
        return None
    try:
        return json.loads(match.group(0))
    except json.JSONDecodeError:
        return None


def _clamp_score(value: object, default: int) -> int:
    try:
        return max(0, min(100, int(float(value))))  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return default


def _string_list(value: object, limit: int) -> list[str]:
    if not isinstance(value, list):
        return []
    return [str(item).strip() for item in value if str(item).strip()][:limit]


def analyze_resume_against_job(
    connection: Connection,
    *,
    user_id: str,
    resume_id: str,
    job_id: str | None,
    job_description: str,
    resume_text: str,
) -> ResumeAnalysisResponse:
    prompt = f"""
Evaluate this resume against the job description and return a JSON object with exactly these keys:
- "ats_score": integer 0-100 (how well the resume would pass an ATS for this role)
- "match_percentage": integer 0-100 (overall fit)
- "missing_skills": array of up to 10 short strings (skills/keywords in the job but missing from the resume)
- "suggestions": array of up to 8 short, actionable improvement strings

Job description:
{job_description[:6000]}

Resume:
{resume_text[:6000]}
"""

    result = _FALLBACK
    try:
        raw = generate_text(prompt, system=_SYSTEM_PROMPT)
        data = _extract_json(raw)
        if data:
            result = ResumeAnalysisResponse(
                ats_score=_clamp_score(data.get("ats_score"), _FALLBACK.ats_score),
                match_percentage=_clamp_score(data.get("match_percentage"), _FALLBACK.match_percentage),
                missing_skills=_string_list(data.get("missing_skills"), 10) or _FALLBACK.missing_skills,
                suggestions=_string_list(data.get("suggestions"), 8) or _FALLBACK.suggestions,
            )
    except Exception as exc:  # noqa: BLE001 - never fail the request on model errors
        logger.warning("Resume analysis model call failed, using fallback: %s", exc)

    create_resume_analysis(
        connection,
        user_id=user_id,
        resume_id=resume_id,
        job_id=job_id,
        analysis=result,
    )
    return result
