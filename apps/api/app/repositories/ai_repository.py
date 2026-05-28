from psycopg import Connection

from app.schemas.ai import ResumeAnalysisResponse


def create_resume_analysis(
    connection: Connection,
    *,
    user_id: str,
    resume_id: str,
    job_id: str | None,
    analysis: ResumeAnalysisResponse,
    model_name: str = "gpt-4.1-mini",
) -> None:
    with connection.cursor() as cursor:
        cursor.execute(
            """
            INSERT INTO "ResumeAnalysis" (
              id, "atsScore", "matchPercentage", "missingSkills", suggestions, strengths,
              "modelName", "userId", "resumeId", "jobId", "createdAt"
            )
            VALUES (
              gen_random_uuid()::text, %s, %s, %s, %s, %s,
              %s, %s, %s, %s, NOW()
            )
            """,
            (
                analysis.ats_score,
                analysis.match_percentage,
                analysis.missing_skills,
                analysis.suggestions,
                [],
                model_name,
                user_id,
                resume_id,
                job_id,
            ),
        )
    connection.commit()


def upsert_job_embedding(
    connection: Connection,
    *,
    job_id: str,
    model_name: str,
    vector_literal: str,
    dimensions: int = 1536,
) -> None:
    with connection.cursor() as cursor:
        cursor.execute(
            """
            DELETE FROM "Embedding"
            WHERE "jobId" = %s AND "entityType" = 'JOB' AND "modelName" = %s
            """,
            (job_id, model_name),
        )
        cursor.execute(
            """
            INSERT INTO "Embedding" (
              id, "entityType", "modelName", dimensions, vector, metadata, "createdAt", "updatedAt", "jobId"
            )
            VALUES (
              gen_random_uuid()::text, 'JOB', %s, %s, %s::vector, '{}'::jsonb, NOW(), NOW(), %s
            )
            """,
            (model_name, dimensions, vector_literal, job_id),
        )
    connection.commit()
