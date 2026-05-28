from fastapi import APIRouter, Depends, Query
from psycopg import Connection

from app.api.deps.rate_limit import check_rate_limit
from app.db.postgres import get_db_connection
from app.repositories.jobs_repository import list_jobs
from app.repositories.user_activity_repository import mark_applied, save_job, unmark_applied, unsave_job
from app.schemas.jobs import JobOut
from app.schemas.user_activity import ActionResponse

router = APIRouter(prefix="/jobs", tags=["jobs"])


@router.get("", response_model=list[JobOut])
async def get_jobs(
    _rate_limit: None = Depends(check_rate_limit),
    connection: Connection = Depends(get_db_connection),
) -> list[JobOut]:
    return list_jobs(connection)


@router.post("/{job_id}/save", response_model=ActionResponse)
async def save_job_for_user(
    job_id: str,
    user_id: str = Query(..., min_length=2),
    _rate_limit: None = Depends(check_rate_limit),
    connection: Connection = Depends(get_db_connection),
) -> ActionResponse:
    save_job(connection, user_id=user_id, job_id=job_id)
    return ActionResponse(success=True)


@router.delete("/{job_id}/save", response_model=ActionResponse)
async def unsave_job_for_user(
    job_id: str,
    user_id: str = Query(..., min_length=2),
    _rate_limit: None = Depends(check_rate_limit),
    connection: Connection = Depends(get_db_connection),
) -> ActionResponse:
    unsave_job(connection, user_id=user_id, job_id=job_id)
    return ActionResponse(success=True)


@router.post("/{job_id}/apply", response_model=ActionResponse)
async def apply_job_for_user(
    job_id: str,
    user_id: str = Query(..., min_length=2),
    _rate_limit: None = Depends(check_rate_limit),
    connection: Connection = Depends(get_db_connection),
) -> ActionResponse:
    mark_applied(connection, user_id=user_id, job_id=job_id)
    return ActionResponse(success=True)


@router.delete("/{job_id}/apply", response_model=ActionResponse)
async def unapply_job_for_user(
    job_id: str,
    user_id: str = Query(..., min_length=2),
    _rate_limit: None = Depends(check_rate_limit),
    connection: Connection = Depends(get_db_connection),
) -> ActionResponse:
    unmark_applied(connection, user_id=user_id, job_id=job_id)
    return ActionResponse(success=True)
