from fastapi import APIRouter, Depends, Query
from psycopg import Connection

from app.api.deps.rate_limit import check_rate_limit
from app.db.postgres import get_db_connection
from app.repositories.user_activity_repository import list_applications, list_saved_jobs
from app.schemas.user_activity import ApplicationItem, SavedJobItem

router = APIRouter(prefix="/users", tags=["user-activity"])


@router.get("/{user_id}/saved-jobs", response_model=list[SavedJobItem])
async def get_saved_jobs(
    user_id: str,
    _rate_limit: None = Depends(check_rate_limit),
    connection: Connection = Depends(get_db_connection),
) -> list[SavedJobItem]:
    return list_saved_jobs(connection, user_id=user_id)


@router.get("/{user_id}/applications", response_model=list[ApplicationItem])
async def get_user_applications(
    user_id: str,
    status: str | None = Query(None),
    _rate_limit: None = Depends(check_rate_limit),
    connection: Connection = Depends(get_db_connection),
) -> list[ApplicationItem]:
    applications = list_applications(connection, user_id=user_id)
    if status:
        return [app for app in applications if app.status == status]
    return applications
