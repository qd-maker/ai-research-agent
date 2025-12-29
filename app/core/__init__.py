"""Core package initialization."""

from app.core.config import Settings, get_settings
from app.core.errors import (
    AgentExecutionError,
    ConfigurationError,
    CrawlError,
    DatabaseError,
    ExtractionError,
    JobNotFoundError,
    LLMError,
    ResearchAgentError,
    StepLimitExceededError,
    URLLimitExceededError,
    classify_error,
)
from app.core.logging import configure_logging, get_logger
from app.core.retry import (
    create_retry_decorator,
    retry_on_crawl_error,
    retry_on_llm_error,
    retry_on_network_error,
)

__all__ = [
    # Config
    "Settings",
    "get_settings",
    # Logging
    "configure_logging",
    "get_logger",
    # Errors
    "ResearchAgentError",
    "ConfigurationError",
    "AgentExecutionError",
    "StepLimitExceededError",
    "URLLimitExceededError",
    "CrawlError",
    "ExtractionError",
    "LLMError",
    "DatabaseError",
    "JobNotFoundError",
    "classify_error",
    # Retry
    "create_retry_decorator",
    "retry_on_llm_error",
    "retry_on_crawl_error",
    "retry_on_network_error",
]
