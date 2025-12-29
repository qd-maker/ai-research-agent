"""Web crawling tool using httpx and BeautifulSoup (Windows compatible)."""

import asyncio
import random
from typing import Any

import httpx
from bs4 import BeautifulSoup
from pydantic import BaseModel, Field

from app.core.config import get_settings
from app.core.errors import CrawlError
from app.core.logging import get_logger
from app.core.retry import retry_on_crawl_error

logger = get_logger(__name__)


# Realistic User-Agent list for rotation
USER_AGENTS = [
    # Chrome on Windows
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    # Chrome on Mac
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    # Firefox on Windows
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0",
    # Safari on Mac
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15",
    # Edge on Windows
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0",
]


class CrawlResult(BaseModel):
    """Crawl result model."""

    url: str = Field(..., description="Crawled URL")
    title: str = Field(default="", description="Page title")
    content: str = Field(default="", description="Extracted text content")
    html: str = Field(default="", description="Raw HTML")
    extra_metadata: dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    success: bool = Field(default=True, description="Whether crawl succeeded")
    error: str | None = Field(default=None, description="Error message if failed")


class CrawlTool:
    """Web crawling tool using httpx + BeautifulSoup with anti-anti-crawl features."""

    def __init__(self) -> None:
        """Initialize crawl tool."""
        self.settings = get_settings()
        self.timeout = self.settings.crawl_timeout_seconds
        self.max_concurrency = self.settings.max_crawl_concurrency

    def _get_headers(self, url: str) -> dict[str, str]:
        """Generate random realistic headers for each request."""
        # Extract domain for Referer
        from urllib.parse import urlparse
        parsed = urlparse(url)
        domain = f"{parsed.scheme}://{parsed.netloc}"
        
        return {
            "User-Agent": random.choice(USER_AGENTS),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "Accept-Language": "en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-User": "?1",
            "Sec-Ch-Ua": '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
            "Sec-Ch-Ua-Mobile": "?0",
            "Sec-Ch-Ua-Platform": '"Windows"',
            "Cache-Control": "max-age=0",
            "Referer": domain,
            "DNT": "1",
        }

    def _extract_text(self, soup: BeautifulSoup) -> str:
        """Extract readable text from HTML."""
        # Remove script and style elements
        for element in soup(["script", "style", "nav", "footer", "header", "aside"]):
            element.decompose()
        
        # Get text
        text = soup.get_text(separator="\n", strip=True)
        
        # Clean up whitespace
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        return "\n".join(lines)

    @retry_on_crawl_error
    async def crawl_url(self, url: str) -> CrawlResult:
        """Crawl a single URL.
        
        Args:
            url: URL to crawl
            
        Returns:
            Crawl result
            
        Raises:
            CrawlError: If crawl fails after retries
        """
        logger.info("crawl_started", url=url)
        
        # Add random delay (0.5-2 seconds) to mimic human behavior
        await asyncio.sleep(random.uniform(0.5, 2.0))
        
        try:
            # Use dynamic headers for each request
            headers = self._get_headers(url)
            
            async with httpx.AsyncClient(
                timeout=httpx.Timeout(self.timeout),
                follow_redirects=True,
                headers=headers,
                http2=True,  # Enable HTTP/2 for better compatibility
            ) as client:
                response = await client.get(url)
                response.raise_for_status()
                
                html = response.text
                soup = BeautifulSoup(html, "lxml")
                
                # Extract title
                title_tag = soup.find("title")
                title = title_tag.get_text(strip=True) if title_tag else ""
                
                # Extract main content
                content = self._extract_text(soup)
                
                # Extract metadata
                extra_metadata = {
                    "status_code": response.status_code,
                    "content_type": response.headers.get("content-type", ""),
                    "content_length": len(content),
                }
                
                crawl_result = CrawlResult(
                    url=url,
                    title=title,
                    content=content[:50000],  # Limit content size
                    html=html[:100000],  # Limit HTML size
                    extra_metadata=extra_metadata,
                    success=True,
                )
                
                logger.info(
                    "crawl_completed",
                    url=url,
                    title=title[:50] if title else "",
                    content_length=len(content),
                )
                return crawl_result
                
        except httpx.TimeoutException as e:
            logger.error("crawl_timeout", url=url, timeout=self.timeout)
            raise CrawlError(f"Crawl timeout for {url}") from e
        except httpx.HTTPStatusError as e:
            logger.error("crawl_http_error", url=url, status=e.response.status_code)
            raise CrawlError(f"HTTP {e.response.status_code} for {url}") from e
        except Exception as e:
            logger.error("crawl_error", url=url, error=str(e))
            raise CrawlError(f"Crawl failed for {url}: {e}") from e

    async def crawl_urls(self, urls: list[str]) -> list[CrawlResult]:
        """Crawl multiple URLs with concurrency control.
        
        Args:
            urls: List of URLs to crawl
            
        Returns:
            List of crawl results
        """
        logger.info("batch_crawl_started", url_count=len(urls))
        
        # Create semaphore for concurrency control
        semaphore = asyncio.Semaphore(self.max_concurrency)
        
        async def crawl_with_semaphore(url: str) -> CrawlResult:
            async with semaphore:
                try:
                    return await self.crawl_url(url)
                except CrawlError as e:
                    # Return failed result instead of raising
                    return CrawlResult(
                        url=url,
                        success=False,
                        error=str(e),
                    )
        
        # Crawl all URLs concurrently with limit
        results = await asyncio.gather(
            *[crawl_with_semaphore(url) for url in urls],
            return_exceptions=False,
        )
        
        success_count = sum(1 for r in results if r.success)
        logger.info(
            "batch_crawl_completed",
            total=len(urls),
            success=success_count,
            failed=len(urls) - success_count,
        )
        
        return results


# Global crawl tool instance
_crawl_tool: CrawlTool | None = None


def get_crawl_tool() -> CrawlTool:
    """Get the global crawl tool instance.
    
    Returns:
        CrawlTool: Global crawl tool
    """
    global _crawl_tool
    if _crawl_tool is None:
        _crawl_tool = CrawlTool()
    return _crawl_tool
