"""
Cache system for GeoIP lookups.

This module provides an abstract cache interface and implementations for
caching IP geolocation lookup results to improve performance.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Optional

from geoip_geocode.models import GeoData


@dataclass
class CacheStats:
    """
    Cache statistics.

    Attributes:
        hits: Number of cache hits
        misses: Number of cache misses
        size: Current number of cached entries
        max_size: Maximum cache capacity
    """

    hits: int = 0
    misses: int = 0
    size: int = 0
    max_size: int = 0

    @property
    def hit_rate(self) -> float:
        """Calculate cache hit rate as percentage."""
        total = self.hits + self.misses
        return (self.hits / total * 100) if total > 0 else 0.0


class CacheBackend(ABC):
    """
    Abstract base class for cache implementations.

    All cache backends must implement this interface to ensure consistent
    behavior across different caching strategies.

    Examples:
        >>> class MyCache(CacheBackend):
        ...     def get(self, key: str) -> Optional[Any]:
        ...         # Implementation here
        ...         pass
    """

    @abstractmethod
    def get(self, key: str) -> Optional[GeoData]:
        """
        Get value from cache.

        Args:
            key: Cache key (typically IP address)

        Returns:
            Cached GeoData object if found, None otherwise
        """
        raise NotImplementedError

    @abstractmethod
    def set(self, key: str, value: GeoData, ttl: Optional[int] = None) -> None:
        """
        Set value in cache with optional TTL.

        Args:
            key: Cache key (typically IP address)
            value: GeoData object to cache
            ttl: Optional time-to-live in seconds (None uses default)
        """
        raise NotImplementedError

    @abstractmethod
    def delete(self, key: str) -> None:
        """
        Delete key from cache.

        Args:
            key: Cache key to delete
        """
        raise NotImplementedError

    @abstractmethod
    def clear(self) -> None:
        """Clear all cache entries and reset statistics."""
        raise NotImplementedError

    @abstractmethod
    def get_stats(self) -> CacheStats:
        """
        Get cache statistics.

        Returns:
            CacheStats object with current statistics
        """
        raise NotImplementedError

    @abstractmethod
    def is_enabled(self) -> bool:
        """
        Check if cache is enabled.

        Returns:
            True if cache is enabled and operational
        """
        raise NotImplementedError


class NoOpCacheBackend(CacheBackend):
    """
    No-operation cache backend (caching disabled).

    This backend is used when caching is disabled. All operations are no-ops
    and always return None or default values.

    Examples:
        >>> cache = NoOpCacheBackend()
        >>> cache.set("key", data)  # Does nothing
        >>> cache.get("key")  # Always returns None
        None
    """

    def get(self, key: str) -> Optional[GeoData]:
        """Always returns None (cache disabled)."""
        return None

    def set(self, key: str, value: GeoData, ttl: Optional[int] = None) -> None:
        """No-op (cache disabled)."""
        pass

    def delete(self, key: str) -> None:
        """No-op (cache disabled)."""
        pass

    def clear(self) -> None:
        """No-op (cache disabled)."""
        pass

    def get_stats(self) -> CacheStats:
        """Returns empty statistics."""
        return CacheStats()

    def is_enabled(self) -> bool:
        """Always returns False."""
        return False


class LRUCacheBackend(CacheBackend):
    """
    LRU (Least Recently Used) cache implementation using cachetools.

    This cache automatically evicts the least recently used entries when the
    maximum size is reached. Entries also expire after the specified TTL.

    Attributes:
        config: Cache configuration
        cache: Underlying TTLCache instance
        _hits: Number of cache hits
        _misses: Number of cache misses

    Examples:
        >>> from geoip_geocode.models import CacheConfig
        >>> config = CacheConfig(enabled=True, max_size=1000, ttl=3600)
        >>> cache = LRUCacheBackend(config)
        >>> cache.set("8.8.8.8", geo_data)
        >>> result = cache.get("8.8.8.8")
    """

    def __init__(self, config: "CacheConfig"):
        """
        Initialize LRU cache backend.

        Args:
            config: Cache configuration with max_size and ttl settings
        """
        from cachetools import TTLCache

        self.config = config
        self._enabled = config.enabled

        if self._enabled:
            self.cache = TTLCache(maxsize=config.max_size, ttl=config.ttl)
        else:
            self.cache = None

        self._hits = 0
        self._misses = 0

    def get(self, key: str) -> Optional[GeoData]:
        """
        Get value from LRU cache.

        Args:
            key: Cache key (IP address)

        Returns:
            Cached GeoData if found, None otherwise
        """
        if not self._enabled or self.cache is None:
            return None

        value = self.cache.get(key)
        if value is not None:
            self._hits += 1
        else:
            self._misses += 1

        return value

    def set(self, key: str, value: GeoData, ttl: Optional[int] = None) -> None:
        """
        Set value in LRU cache.

        Note: TTL is set at cache level in TTLCache, not per-key.
        The ttl parameter is accepted for interface compatibility but ignored.

        Args:
            key: Cache key (IP address)
            value: GeoData object to cache
            ttl: Ignored (TTL is set at cache initialization)
        """
        if self._enabled and self.cache is not None:
            self.cache[key] = value

    def delete(self, key: str) -> None:
        """
        Delete key from cache.

        Args:
            key: Cache key to delete
        """
        if self._enabled and self.cache is not None:
            self.cache.pop(key, None)

    def clear(self) -> None:
        """Clear all cache entries and reset statistics."""
        if self._enabled and self.cache is not None:
            self.cache.clear()
            self._hits = 0
            self._misses = 0

    def get_stats(self) -> CacheStats:
        """
        Get cache statistics.

        Returns:
            CacheStats with hits, misses, size, and max_size
        """
        size = len(self.cache) if self.cache is not None else 0
        max_size = self.config.max_size if self._enabled else 0

        return CacheStats(
            hits=self._hits, misses=self._misses, size=size, max_size=max_size
        )

    def is_enabled(self) -> bool:
        """Check if cache is enabled."""
        return self._enabled


class CacheFactory:
    """
    Factory for creating cache backends.

    This factory creates the appropriate cache backend based on configuration.
    Currently supports LRU cache, with the ability to add more backends later.

    Examples:
        >>> config = CacheConfig(enabled=True, backend="lru")
        >>> cache = CacheFactory.create_cache(config)
        >>> isinstance(cache, LRUCacheBackend)
        True
    """

    @staticmethod
    def create_cache(config: "CacheConfig") -> CacheBackend:
        """
        Create appropriate cache backend based on configuration.

        Args:
            config: Cache configuration

        Returns:
            Cache backend instance (NoOp if disabled, LRU if enabled)

        Raises:
            ValueError: If backend type is not supported

        Examples:
            >>> # Disabled cache
            >>> config = CacheConfig(enabled=False)
            >>> cache = CacheFactory.create_cache(config)
            >>> isinstance(cache, NoOpCacheBackend)
            True

            >>> # LRU cache
            >>> config = CacheConfig(enabled=True, backend="lru")
            >>> cache = CacheFactory.create_cache(config)
            >>> isinstance(cache, LRUCacheBackend)
            True
        """
        if not config.enabled:
            return NoOpCacheBackend()

        backend = config.backend.lower()

        if backend == "lru":
            return LRUCacheBackend(config)
        else:
            raise ValueError(
                f"Unsupported cache backend: {backend}. "
                f"Supported backends: 'lru'"
            )
