"""Test crawl tool."""

import pytest

from app.tools.crawl import CrawlTool


@pytest.mark.asyncio
async def test_crawl_tool_initialization() -> None:
    """Test crawl tool can be initialized."""
    crawl_tool = CrawlTool()
    assert crawl_tool is not None
    assert crawl_tool.timeout > 0
    assert crawl_tool.max_concurrency > 0


@pytest.mark.asyncio
async def test_crawl_urls_empty() -> None:
    """Test crawling empty URL list."""
    crawl_tool = CrawlTool()
    results = await crawl_tool.crawl_urls([])
    assert results == []


# Note: Real crawl tests would require network access
# In production, add integration tests with real URLs
