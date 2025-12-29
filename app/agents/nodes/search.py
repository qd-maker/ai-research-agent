"""Search node: Search for relevant URLs."""

from typing import Any

from app.agents.state import AgentState
from app.core.logging import get_logger
from app.tools.search import get_search_tool

logger = get_logger(__name__)


async def search_node(state: AgentState) -> dict[str, Any]:
    """Search for URLs based on research plan.
    
    Args:
        state: Current agent state
        
    Returns:
        Updated state with URLs
    """
    job_id = state["job_id"]
    query = state["query"]
    plan = state.get("plan", {})
    max_urls = state.get("max_urls", 10)
    
    logger.info("search_node_started", job_id=job_id)
    
    try:
        search_tool = get_search_tool()
        
        # Use search keywords from plan if available, otherwise use original query
        search_keywords = plan.get("search_keywords", [query])
        
        # Search using the first few keywords
        all_urls = []
        for keyword in search_keywords[:3]:  # Limit to first 3 keywords
            results = await search_tool.search(
                query=keyword,
                max_results=max_urls,
            )
            all_urls.extend([r.url for r in results])
        
        # Remove duplicates while preserving order
        seen = set()
        unique_urls = []
        for url in all_urls:
            if url not in seen:
                seen.add(url)
                unique_urls.append(url)
        
        logger.info(
            "search_node_completed",
            job_id=job_id,
            url_count=len(unique_urls),
        )
        
        return {
            "urls": unique_urls,
            "step_count": state.get("step_count", 0) + 1,
            "progress": f"Found {len(unique_urls)} candidate URLs",
        }
        
    except Exception as e:
        logger.error("search_node_failed", job_id=job_id, error=str(e))
        errors = state.get("errors", [])
        errors.append({
            "node": "search",
            "error": str(e),
            "error_type": type(e).__name__,
        })
        return {
            "urls": [],
            "errors": errors,
            "step_count": state.get("step_count", 0) + 1,
            "progress": "Search failed",
        }
