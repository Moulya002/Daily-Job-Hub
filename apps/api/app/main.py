from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes.admin import router as admin_router
from app.api.routes.ai import router as ai_router
from app.api.routes.ingest import router as ingest_router
from app.api.routes.jobs import router as jobs_router
from app.api.routes.recommendations import router as recommendations_router
from app.api.routes.search import router as search_router
from app.api.routes.user_activity import router as user_activity_router
from app.core.config import settings

app = FastAPI(title=settings.app_name)

allowed_origins = [origin.strip() for origin in settings.cors_origins.split(",") if origin.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok", "service": "api"}


app.include_router(jobs_router)
app.include_router(search_router)
app.include_router(ai_router)
app.include_router(recommendations_router)
app.include_router(admin_router)
app.include_router(user_activity_router)
app.include_router(ingest_router)
