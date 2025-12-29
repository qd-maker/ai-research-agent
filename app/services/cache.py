"""Caching service (stub implementation with extensible interface)."""

import hashlib
import json
from typing import Any

from app.core.config import get_settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class CacheService:
    """In-memory cache service.
    
    Note: This is a simple in-memory implementation.
    In production, replace with Redis or similar distributed cache.
    """

    def __init__(self) -> None:
        """Initialize cache service."""
        self.settings = get_settings()
        self.enabled = self.settings.cache_enabled
        self.ttl = self.settings.cache_ttl_seconds
        self._cache: dict[str, Any] = {}

    def _generate_key(self, prefix: str, data: Any) -> str:
        """Generate cache key from data.
        
        Args:
            prefix: Key prefix
            data: Data to hash
            
        Returns:
            Cache key
        """
        data_str = json.dumps(data, sort_keys=True)
        hash_digest = hashlib.sha256(data_str.encode()).hexdigest()
        return f"{prefix}:{hash_digest[:16]}"

    async def get(self, key: str) -> Any | None:
        """Get value from cache.
        
        Args:
            key: Cache key
            
        Returns:
            Cached value or None
        """
        if not self.enabled:
            return None
        
        value = self._cache.get(key)
        if value is not None:
            logger.debug("cache_hit", key=key)
        else:
            logger.debug("cache_miss", key=key)
        return value

    async def set(self, key: str, value: Any) -> None:
        """Set value in cache.
        
        Args:
            key: Cache key
            value: Value to cache
        """
        if not self.enabled:
            return
        
        self._cache[key] = value
        logger.debug("cache_set", key=key)

    async def get_or_compute(
        self,
        key: str,
        compute_fn: Any,
        *args: Any,
        **kwargs: Any,
    ) -> Any:
        """Get from cache or compute and cache.
        
        Args:
            key: Cache key
            compute_fn: Function to compute value if not cached
            *args: Arguments for compute function
            **kwargs: Keyword arguments for compute function
            
        Returns:
            Cached or computed value
        """
        value = await self.get(key)
        if value is not None:
            return value
        
        # Compute value
        if callable(compute_fn):
            if hasattr(compute_fn, "__await__"):
                value = await compute_fn(*args, **kwargs)
            else:
                value = compute_fn(*args, **kwargs)
        
        await self.set(key, value)
        return value

    def clear(self) -> None:
        """Clear all cache entries."""
        self._cache.clear()
        logger.info("cache_cleared")


# Global cache service instance
_cache_service: CacheService | None = None


def get_cache_service() -> CacheService:
    """Get the global cache service instance.
    
    Returns:
        CacheService: Global cache service
    """
    global _cache_service
    if _cache_service is None:
        _cache_service = CacheService()
    return _cache_service
