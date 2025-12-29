"""Crawl node: Crawl URLs and extract content."""

from typing import Any

from app.agents.state import AgentState
from app.core.logging import get_logger
from app.tools.crawl import get_crawl_tool

logger = get_logger(__name__)


async def crawl_node(state: AgentState) -> dict[str, Any]:
    """Crawl filtered URLs.
    
    Args:
        state: Current agent state
        
    Returns:
        Updated state with crawled pages
    """
    job_id = state["job_id"]
    filtered_urls = state.get("filtered_urls", [])
    
    logger.info("crawl_node_started", job_id=job_id, url_count=len(filtered_urls))
    
    try:
        crawl_tool = get_crawl_tool()
        
        # Crawl all URLs with concurrency control
        crawl_results = await crawl_tool.crawl_urls(filtered_urls)
        
        # Convert to page dictionaries
        pages = []
        for result in crawl_results:
            page_data = {
                "url": result.url,
                "title": result.title,
                "content": result.content,
                "extra_metadata": result.extra_metadata,
                "success": result.success,
                "error": result.error,
            }
            pages.append(page_data)
        
        success_count = sum(1 for p in pages if p["success"])
        failed_count = len(pages) - success_count
        
        logger.info(
            "crawl_node_completed",
            job_id=job_id,
            total=len(pages),
            success=success_count,
            failed=failed_count,
        )
        
        # Track failures as errors but don't fail the entire node
        errors = state.get("errors", [])
        for page in pages:
            if not page["success"]:
                errors.append({
                    "node": "crawl",
                    "url": page["url"],
                    "error": page["error"],
                    "error_type": "CrawlError",
                })
        
        return {
            "pages": pages,
            "errors": errors,
            "step_count": state.get("step_count", 0) + 1,
            "progress": f"Crawled {success_count}/{len(pages)} pages successfully",
        }
        
    except Exception as e:
        logger.error("crawl_node_failed", job_id=job_id, error=str(e))
        errors = state.get("errors", [])
        errors.append({
            "node": "crawl",
            "error": str(e),
            "error_type": type(e).__name__,
        })
        return {
            "pages": [],
            "errors": errors,
            "step_count": state.get("step_count", 0) + 1,
            "progress": "Crawling failed",
        }
