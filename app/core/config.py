"""Core configuration management using Pydantic Settings."""

from functools import lru_cache
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings with environment variable support."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # OpenAI Configuration
    openai_api_key: str = Field(..., description="OpenAI API key")
    openai_api_base: str | None = Field(default=None, description="OpenAI API base URL (for proxies)")
    openai_model: str = Field(default="gpt-4o-mini", description="OpenAI model name")
    openai_max_tokens: int = Field(default=4096, description="Max tokens per request")

    # Agent Guardrails
    max_agent_steps: int = Field(default=20, description="Maximum agent execution steps")
    max_urls: int = Field(default=10, description="Maximum URLs to process")
    max_crawl_concurrency: int = Field(default=3, description="Max concurrent crawls")
    crawl_timeout_seconds: int = Field(default=30, description="Crawl timeout in seconds")
    max_retries: int = Field(default=3, description="Max retry attempts")

    # Database
    database_url: str = Field(
        default="sqlite+aiosqlite:///./research_agent.db",
        description="Database connection URL",
    )

    # Logging
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = Field(
        default="INFO", description="Logging level"
    )
    log_format: Literal["json", "console"] = Field(
        default="json", description="Log output format"
    )

    # Cache
    cache_enabled: bool = Field(default=True, description="Enable caching")
    cache_ttl_seconds: int = Field(default=3600, description="Cache TTL in seconds")

    # API
    api_host: str = Field(default="0.0.0.0", description="API host")
    api_port: int = Field(default=8000, description="API port")
    api_reload: bool = Field(default=True, description="Enable auto-reload")


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
