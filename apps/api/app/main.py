import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes.admin import router as admin_router
from app.api.routes.ai import router as ai_router
from app.api.routes.health import router as health_router
from app.api.routes.ingest import router as ingest_router
from app.api.routes.jobs import router as jobs_router
from app.api.routes.recommendations import router as recommendations_router
from app.api.routes.search import router as search_router
from app.api.routes.user_activity import router as user_activity_router
from app.core.config import settings
from app.core.errors import register_exception_handlers
from app.core.logging import setup_logging
from app.core.middleware import RequestContextMiddleware
from app.db.postgres import close_pool, init_pool

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(_: FastAPI):
    setup_logging(level=settings.log_level, json_output=settings.log_json)
    for warning in settings.missing_critical():
        logger.warning("Config: %s", warning)
    try:
        init_pool()
    except Exception as exc:  # noqa: BLE001 - boot even if DB is down so health works
        logger.error("Failed to open DB pool at startup: %s", exc)
    logger.info("%s started in %s mode", settings.app_name, settings.environment)
    yield
    close_pool()


app = FastAPI(title=settings.app_name, lifespan=lifespan)

app.add_middleware(RequestContextMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

register_exception_handlers(app)

app.include_router(health_router)
app.include_router(jobs_router)
app.include_router(search_router)
app.include_router(ai_router)
app.include_router(recommendations_router)
app.include_router(admin_router)
app.include_router(user_activity_router)
app.include_router(ingest_router)
