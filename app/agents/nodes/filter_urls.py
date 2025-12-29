"""Filter URLs node: Deduplicate and limit URLs."""

from typing import Any

from app.agents.state import AgentState
from app.core.errors import URLLimitExceededError
from app.core.logging import get_logger

logger = get_logger(__name__)


async def filter_urls_node(state: AgentState) -> dict[str, Any]:
    """Filter and limit URLs.
    
    Args:
        state: Current agent state
        
    Returns:
        Updated state with filtered URLs
    """
    job_id = state["job_id"]
    urls = state.get("urls", [])
    max_urls = state.get("max_urls", 10)
    
    logger.info("filter_urls_node_started", job_id=job_id, url_count=len(urls))
    
    try:
        # Remove duplicates (already done in search, but double-check)
        unique_urls = list(dict.fromkeys(urls))
        
        # Apply URL limit
        if len(unique_urls) > max_urls:
            logger.warning(
                "url_limit_applied",
                job_id=job_id,
                original_count=len(unique_urls),
                max_urls=max_urls,
            )
            filtered_urls = unique_urls[:max_urls]
        else:
            filtered_urls = unique_urls
        
        # TODO: Add quality filtering based on:
        # - Domain reputation
        # - URL patterns
        # - Content type detection
        # For now, just use the first N URLs
        
        logger.info(
            "filter_urls_node_completed",
            job_id=job_id,
            filtered_count=len(filtered_urls),
        )
        
        return {
            "filtered_urls": filtered_urls,
            "step_count": state.get("step_count", 0) + 1,
            "progress": f"Filtered to {len(filtered_urls)} URLs",
        }
        
    except Exception as e:
        logger.error("filter_urls_node_failed", job_id=job_id, error=str(e))
        errors = state.get("errors", [])
        errors.append({
            "node": "filter_urls",
            "error": str(e),
            "error_type": type(e).__name__,
        })
        return {
            "filtered_urls": [],
            "errors": errors,
            "step_count": state.get("step_count", 0) + 1,
            "progress": "URL filtering failed",
        }
