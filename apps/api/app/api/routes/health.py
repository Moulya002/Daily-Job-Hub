from fastapi import APIRouter, Response, status

from app.core.config import settings
from app.db.postgres import check_db

router = APIRouter(tags=["health"])


@router.get("/health")
async def health() -> dict[str, str]:
    """Liveness: the process is up and serving."""
    return {"status": "ok", "service": "api", "environment": settings.environment}


@router.get("/health/ready")
async def readiness(response: Response) -> dict[str, object]:
    """Readiness: dependencies (DB) are reachable. 503 if not ready."""
    db_ok = check_db()
    ready = db_ok
    if not ready:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    return {
        "ready": ready,
        "checks": {"database": "ok" if db_ok else "unavailable"},
    }
