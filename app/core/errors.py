"""Custom error classes and error handling utilities."""

from typing import Any


class ResearchAgentError(Exception):
    """Base exception for all research agent errors."""

    def __init__(self, message: str, details: dict[str, Any] | None = None) -> None:
        super().__init__(message)
        self.message = message
        self.details = details or {}


class ConfigurationError(ResearchAgentError):
    """Raised when configuration is invalid or missing."""

    pass


class AgentExecutionError(ResearchAgentError):
    """Raised when agent execution fails."""

    pass


class StepLimitExceededError(AgentExecutionError):
    """Raised when agent exceeds maximum step limit."""

    pass


class URLLimitExceededError(AgentExecutionError):
    """Raised when URL limit is exceeded."""

    pass


class CrawlError(ResearchAgentError):
    """Raised when web crawling fails."""

    pass


class ExtractionError(ResearchAgentError):
    """Raised when data extraction fails."""

    pass


class LLMError(ResearchAgentError):
    """Raised when LLM API call fails."""

    pass


class DatabaseError(ResearchAgentError):
    """Raised when database operation fails."""

    pass


class JobNotFoundError(ResearchAgentError):
    """Raised when job is not found."""

    pass


def classify_error(error: Exception) -> str:
    """Classify error into categories for better handling.
    
    Args:
        error: Exception to classify
        
    Returns:
        Error category string
    """
    if isinstance(error, StepLimitExceededError):
        return "step_limit_exceeded"
    elif isinstance(error, URLLimitExceededError):
        return "url_limit_exceeded"
    elif isinstance(error, CrawlError):
        return "crawl_failed"
    elif isinstance(error, ExtractionError):
        return "extraction_failed"
    elif isinstance(error, LLMError):
        return "llm_failed"
    elif isinstance(error, DatabaseError):
        return "database_error"
    elif isinstance(error, TimeoutError):
        return "timeout"
    else:
        return "unknown_error"
