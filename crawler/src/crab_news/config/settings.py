"""Configuration settings for Crab News Crawler."""

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    supabase_url: str = Field(default="", alias="SUPABASE_URL")
    supabase_service_role_key: str = Field(default="", alias="SUPABASE_SERVICE_ROLE_KEY")

    log_level: str = Field(default="INFO", alias="LOG_LEVEL")
    user_agent: str = Field(
        default="Mozilla/5.0 (compatible; CrabNewsCrawler/1.0; +https://github.com/Qosam217/Crab-News)",
        alias="USER_AGENT"
    )
    request_timeout_seconds: int = Field(default=15, alias="REQUEST_TIMEOUT_SECONDS")
    rate_limit_delay_seconds: float = Field(default=1.0, alias="RATE_LIMIT_DELAY_SECONDS")
    max_articles_per_source: int = Field(default=30, alias="MAX_ARTICLES_PER_SOURCE")


settings = Settings()
