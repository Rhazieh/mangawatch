from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")

    app_env: str = "development"
    app_base_url: str = "http://localhost:8000"
    database_url: str
    jwt_secret: str
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 30
    sendgrid_api_key: str = ""
    email_from: str = "noreply@mangawatch.app"
    discord_webhook_url: str = ""
    poll_interval_mangadex: int = 1800  # seconds — 30 min per ADR-0001
    poll_interval_scrape: int = 7200    # seconds — 2 hr for scrape sources

    @field_validator("database_url")
    @classmethod
    def fix_postgres_scheme(cls, v: str) -> str:
        # Fly.io (and Heroku) set postgres:// but SQLAlchemy 2.0 requires postgresql://
        if v.startswith("postgres://"):
            return v.replace("postgres://", "postgresql://", 1)
        return v

    @field_validator("jwt_secret")
    @classmethod
    def jwt_secret_not_empty(cls, v: str) -> str:
        if not v:
            raise ValueError("JWT_SECRET must not be empty")
        return v


settings = Settings()
