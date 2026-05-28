from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=(".env", "../../.env"), extra="ignore")

    app_name: str = "Daily Job Hub API"
    database_url: str = "postgresql://moulya.r.b@localhost:5432/daily_job_hub"
    redis_url: str = "redis://localhost:6379"
    openai_api_key: str = ""
    gemini_api_key: str = ""
    embedding_model: str = "models/gemini-embedding-001"
    embedding_dimensions: int = 768
    gemini_text_model: str = "gemini-2.0-flash"
    embedding_requests_per_minute: int = 90
    rate_limit_per_minute: int = 120
    cors_origins: str = "http://localhost:3000"
    adzuna_app_id: str = ""
    adzuna_app_key: str = ""
    adzuna_country: str = "us"
    adzuna_max_pages_per_query: int = 2
    embedding_backfill_limit: int = 200
    greenhouse_companies: str = ""
    lever_companies: str = ""
    groq_api_key: str = ""
    groq_text_model: str = "llama-3.3-70b-versatile"


settings = Settings()
