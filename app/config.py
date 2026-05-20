from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")

    app_env: str = "development"
    database_url: str
    jwt_secret: str
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 30
    sendgrid_api_key: str = ""
    email_from: str = "noreply@mangawatch.app"
    poll_interval_mangadex: int = 1800  # seconds — 30 min per ADR-0001
    poll_interval_scrape: int = 7200    # seconds — 2 hr for scrape sources


settings = Settings()
