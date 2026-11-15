"""Centralized, typed application configuration loaded from environment variables."""
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    """Runtime settings; secrets are supplied by the deployment environment."""
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")
    app_name: str = "StockFlow ERP"
    environment: str = "development"
    debug: bool = False
    api_v1_prefix: str = "/api/v1"
    database_url: str = "sqlite:///./stockflow.db"
    jwt_secret_key: str = "development-only-change-this-secret-before-deployment"
    jwt_algorithm: str = "HS256"
    access_token_minutes: int = 20
    refresh_token_days: int = 14
    redis_url: str = "redis://localhost:6379/0"
    cors_origins: str = "http://localhost:5173"

    @property
    def cors_origin_list(self) -> list[str]:
        """Return configured browser origins as a clean list."""
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

@lru_cache
def get_settings() -> Settings:
    """Cache settings so all application components share one configuration."""
    return Settings()
