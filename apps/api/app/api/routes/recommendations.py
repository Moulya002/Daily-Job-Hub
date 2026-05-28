from fastapi import APIRouter, Depends, Query
from psycopg import Connection

from app.api.deps.rate_limit import check_rate_limit
from app.db.postgres import get_db_connection
from app.schemas.jobs import JobOut
from app.services.recommendation_service import get_recommendations_for_user

router = APIRouter(prefix="/recommendations", tags=["recommendations"])


@router.get("", response_model=list[JobOut])
async def recommendations(
    user_id: str = Query(...),
    _rate_limit: None = Depends(check_rate_limit),
    connection: Connection = Depends(get_db_connection),
) -> list[JobOut]:
    return get_recommendations_for_user(connection, user_id)
