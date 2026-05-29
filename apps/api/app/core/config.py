from functools import cached_property
from typing import Literal

from pydantic import computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=(".env", "../../.env"), extra="ignore")

    # --- App ---
    app_name: str = "Daily Job Hub API"
    environment: Literal["development", "staging", "production"] = "development"
    log_level: str = "INFO"
    log_json: bool = False

    # --- Database ---
    database_url: str = "postgresql://moulya.r.b@localhost:5432/daily_job_hub"
    db_pool_min_size: int = 1
    db_pool_max_size: int = 10
    db_pool_timeout: float = 10.0

    # --- Redis / queues ---
    redis_url: str = "redis://localhost:6379"

    # --- AI providers ---
    openai_api_key: str = ""
    gemini_api_key: str = ""
    embedding_model: str = "models/gemini-embedding-001"
    embedding_dimensions: int = 768
    gemini_text_model: str = "gemini-2.0-flash"
    embedding_requests_per_minute: int = 90
    groq_api_key: str = ""
    groq_text_model: str = "llama-3.3-70b-versatile"

    # --- Ingestion sources ---
    adzuna_app_id: str = ""
    adzuna_app_key: str = ""
    adzuna_country: str = "us"
    adzuna_max_pages_per_query: int = 2
    embedding_backfill_limit: int = 200
    greenhouse_companies: str = ""
    lever_companies: str = ""

    # --- API behavior ---
    rate_limit_per_minute: int = 120
    cors_origins: str = "http://localhost:3000"

    # --- Observability (optional) ---
    sentry_dsn: str = ""

    @computed_field  # type: ignore[prop-decorator]
    @cached_property
    def is_production(self) -> bool:
        return self.environment == "production"

    @computed_field  # type: ignore[prop-decorator]
    @cached_property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    @property
    def has_text_model(self) -> bool:
        return bool(self.groq_api_key or self.gemini_api_key)

    def missing_critical(self) -> list[str]:
        """Return human-readable warnings for config that limits functionality.

        Intentionally non-fatal: the API should still boot so health checks and
        non-AI endpoints work, but operators get a clear signal at startup.
        """
        warnings: list[str] = []
        if not self.gemini_api_key:
            warnings.append("GEMINI_API_KEY is empty - semantic search/embeddings disabled.")
        if not self.has_text_model:
            warnings.append("No GROQ_API_KEY or GEMINI_API_KEY - AI text generation disabled.")
        if not (self.adzuna_app_id and self.adzuna_app_key):
            warnings.append("ADZUNA_APP_ID/KEY empty - Adzuna ingestion disabled.")
        return warnings


settings = Settings()
