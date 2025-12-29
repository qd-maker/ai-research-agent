"""Retry utilities using tenacity."""

from typing import Any, Callable, TypeVar

from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from app.core.config import get_settings
from app.core.errors import CrawlError, LLMError

T = TypeVar("T")


def create_retry_decorator(
    max_attempts: int | None = None,
    exceptions: tuple[type[Exception], ...] = (Exception,),
    min_wait: float = 1.0,
    max_wait: float = 10.0,
) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """Create a retry decorator with exponential backoff.
    
    Args:
        max_attempts: Maximum retry attempts (defaults to settings.max_retries)
        exceptions: Tuple of exception types to retry on
        min_wait: Minimum wait time in seconds
        max_wait: Maximum wait time in seconds
        
    Returns:
        Configured retry decorator
    """
    settings = get_settings()
    attempts = max_attempts or settings.max_retries

    return retry(
        stop=stop_after_attempt(attempts),
        wait=wait_exponential(multiplier=1, min=min_wait, max=max_wait),
        retry=retry_if_exception_type(exceptions),
        reraise=True,
    )


# Pre-configured retry decorators for common use cases
retry_on_llm_error = create_retry_decorator(
    exceptions=(LLMError, TimeoutError),
    min_wait=2.0,
    max_wait=30.0,
)

retry_on_crawl_error = create_retry_decorator(
    exceptions=(CrawlError, TimeoutError),
    min_wait=1.0,
    max_wait=10.0,
)

retry_on_network_error = create_retry_decorator(
    exceptions=(ConnectionError, TimeoutError),
    min_wait=1.0,
    max_wait=15.0,
)
