"""
Application configuration using Pydantic settings.
"""
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List


class Settings(BaseSettings):
    """Application settings."""

    # App Configuration
    APP_NAME: str = "Floatplane Zero Agent"
    DEBUG: bool = True

    # Database
    DATABASE_URL: str = "postgresql://postgres:postgres@db:5432/floatplane"

    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:5173"]

    # LLM API Keys (optional for Feature 1)
    OPENAI_API_KEY: str = ""
    ANTHROPIC_API_KEY: str = ""
    GOOGLE_API_KEY: str = ""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True
    )


# Create settings instance
settings = Settings()
