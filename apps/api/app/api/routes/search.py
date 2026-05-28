from fastapi import APIRouter, Depends, Query
from psycopg import Connection

from app.api.deps.rate_limit import check_rate_limit
from app.db.postgres import get_db_connection
from app.schemas.jobs import SemanticSearchResult
from app.services.search_service import semantic_search_jobs

router = APIRouter(prefix="/search", tags=["search"])


@router.get("", response_model=list[SemanticSearchResult])
async def search_jobs(
    query: str = Query(..., min_length=2),
    _rate_limit: None = Depends(check_rate_limit),
    connection: Connection = Depends(get_db_connection),
) -> list[SemanticSearchResult]:
    return semantic_search_jobs(connection, query)
