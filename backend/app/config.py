"""Application configuration using Pydantic Settings."""

from functools import lru_cache
from typing import Literal

from pydantic import Field, PostgresDsn, RedisDsn, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Application
    app_name: str = "LavenderSentinel"
    app_version: str = "0.1.0"
    debug: bool = False
    environment: Literal["development", "staging", "production"] = "development"

    # API
    api_prefix: str = "/api/v1"
    cors_origins: list[str] = Field(default=["http://localhost:5173", "http://localhost:3000"])

    # Security
    secret_key: SecretStr = Field(default=SecretStr("change-this-in-production"))
    access_token_expire_minutes: int = 60 * 24 * 7  # 7 days
    algorithm: str = "HS256"

    # Database
    database_url: PostgresDsn = Field(
        default="postgresql+asyncpg://postgres:postgres@localhost:5432/lavender_sentinel"
    )
    database_pool_size: int = 10
    database_max_overflow: int = 20

    # Redis
    redis_url: RedisDsn = Field(default="redis://localhost:6379/0")

    # Vector Database (Qdrant)
    qdrant_host: str = "localhost"
    qdrant_port: int = 6333
    qdrant_collection: str = "paper_embeddings"

    # LLM Settings
    llm_provider: Literal["openai", "anthropic", "ollama"] = "openai"
    llm_model: str = "gpt-4o-mini"
    llm_api_key: SecretStr = Field(default=SecretStr(""))
    llm_base_url: str | None = None

    # Embedding Settings
    embedding_model: str = "BAAI/bge-base-en-v1.5"
    embedding_dimension: int = 768

    # Paper Collection Settings
    arxiv_max_results: int = 100
    paper_collection_interval_hours: int = 24

    # CocoIndex Settings
    cocoindex_database_url: str = Field(
        default="postgresql://postgres:postgres@localhost:5432/lavender_sentinel"
    )

    @property
    def sync_database_url(self) -> str:
        """Get synchronous database URL for CocoIndex."""
        return str(self.database_url).replace("+asyncpg", "")


class DevelopmentSettings(Settings):
    """Development-specific settings."""

    debug: bool = True
    environment: Literal["development", "staging", "production"] = "development"


class ProductionSettings(Settings):
    """Production-specific settings."""

    debug: bool = False
    environment: Literal["development", "staging", "production"] = "production"


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance based on environment."""
    import os

    env = os.getenv("ENVIRONMENT", "development")
    if env == "production":
        return ProductionSettings()
    return DevelopmentSettings()


# Global settings instance
settings = get_settings()

