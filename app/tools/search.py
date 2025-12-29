"""Web search tool using DuckDuckGo with region support."""

import asyncio
from functools import partial

from duckduckgo_search import DDGS

from pydantic import BaseModel, Field

from app.core.logging import get_logger

logger = get_logger(__name__)


class SearchResult(BaseModel):
    """Search result model."""

    title: str = Field(..., description="Page title")
    url: str = Field(..., description="Page URL")
    snippet: str = Field(..., description="Page snippet/description")
    rank: int = Field(..., description="Search result rank")


# Sites that commonly block scraping
BLOCKED_DOMAINS = {
    "zhihu.com", 
    "weixin.qq.com", 
    "weibo.com",
    "douyin.com",
    "xiaohongshu.com",
    "bilibili.com",
    "weforum.org",      # World Economic Forum - strict anti-bot
    "bloomberg.com",    # Bloomberg - paywall + anti-bot
    "wsj.com",          # Wall Street Journal - paywall
    "nytimes.com",      # NYTimes - paywall
    "ft.com",           # Financial Times - paywall
    "linkedin.com",     # LinkedIn - login required
    "facebook.com",     # Facebook - login required
    "twitter.com",      # Twitter/X - login required
    "x.com",            # X - login required
    "instagram.com",    # Instagram - login required
    "reddit.com",       # Reddit - strict anti-bot (403)
    "segmentfault.com", # SegmentFault - timeout issues
    "ones.cn",          # Ones - timeout issues
    "worktile.com",     # Worktile - timeout issues
    "movieboxpro.app",  # MovieBoxPro - strict anti-bot (403)
}


def is_accessible_url(url: str) -> bool:
    """Check if URL is likely accessible (not from blocked domains)."""
    for domain in BLOCKED_DOMAINS:
        if domain in url:
            return False
    return True


class SearchTool:
    """Web search tool using DuckDuckGo."""

    async def search(
        self,
        query: str,
        max_results: int = 10,
    ) -> list[SearchResult]:
        """Search the web for a query using DuckDuckGo.
        
        Searches both Chinese and English results to get diverse sources.
        
        Args:
            query: Search query
            max_results: Maximum number of results
            
        Returns:
            List of search results
        """
        logger.info("search_started", query=query, max_results=max_results)
        
        results = []
        seen_urls = set()
        
        try:
            # Create a fresh DDGS instance for each search to avoid state issues
            loop = asyncio.get_event_loop()
            
            def _do_search(q: str, **kwargs) -> list:
                """Helper function to perform search in executor."""
                try:
                    ddgs = DDGS()
                    raw = list(ddgs.text(q, **kwargs))
                    logger.info("ddgs_raw_results", query=q, count=len(raw))
                    return raw
                except Exception as e:
                    logger.error("ddgs_search_error", query=q, error=str(e), error_type=type(e).__name__)
                    return []
            
            # 1. Default search
            raw_results = await loop.run_in_executor(
                None,
                partial(_do_search, query, max_results=max_results * 2)
            )
            
            for item in raw_results:
                url = item.get("href", item.get("link", ""))
                if url and url not in seen_urls and is_accessible_url(url):
                    seen_urls.add(url)
                    results.append(SearchResult(
                        title=item.get("title", ""),
                        url=url,
                        snippet=item.get("body", item.get("snippet", "")),
                        rank=len(results) + 1,
                    ))
                    if len(results) >= max_results:
                        break
            
            # 2. If not enough results, try English search
            if len(results) < max_results // 2:
                en_query = f"{query} review comparison analysis"
                en_results = await loop.run_in_executor(
                    None,
                    partial(_do_search, en_query, region="wt-wt", max_results=max_results)
                )
                
                for item in en_results:
                    url = item.get("href", item.get("link", ""))
                    if url and url not in seen_urls and is_accessible_url(url):
                        seen_urls.add(url)
                        results.append(SearchResult(
                            title=item.get("title", ""),
                            url=url,
                            snippet=item.get("body", item.get("snippet", "")),
                            rank=len(results) + 1,
                        ))
                        if len(results) >= max_results:
                            break
            
            logger.info(
                "search_completed", 
                query=query, 
                result_count=len(results),
                filtered_blocked=len(seen_urls) - len(results),
            )
            return results
            
        except Exception as e:
            logger.error("search_failed", query=query, error=str(e), error_type=type(e).__name__)
            return []


# Global search tool instance
_search_tool: SearchTool | None = None


def get_search_tool() -> SearchTool:
    """Get the global search tool instance.
    
    Returns:
        SearchTool: Global search tool
    """
    global _search_tool
    if _search_tool is None:
        _search_tool = SearchTool()
    return _search_tool
