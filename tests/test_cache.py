"""Tests for cache system."""

import time
from unittest.mock import Mock

import pytest

from geoip_geocode.cache import (
    CacheBackend,
    CacheFactory,
    CacheStats,
    LRUCacheBackend,
    NoOpCacheBackend,
)
from geoip_geocode.models import CacheConfig, GeoData


class TestCacheStats:
    """Tests for CacheStats dataclass."""

    def test_cache_stats_creation(self):
        """Test creating CacheStats object."""
        stats = CacheStats(hits=10, misses=5, size=8, max_size=100)

        assert stats.hits == 10
        assert stats.misses == 5
        assert stats.size == 8
        assert stats.max_size == 100

    def test_hit_rate_calculation(self):
        """Test hit rate percentage calculation."""
        stats = CacheStats(hits=90, misses=10)
        assert stats.hit_rate == 90.0

        stats = CacheStats(hits=1, misses=1)
        assert stats.hit_rate == 50.0

        stats = CacheStats(hits=100, misses=0)
        assert stats.hit_rate == 100.0

    def test_hit_rate_zero_total(self):
        """Test hit rate when no requests yet."""
        stats = CacheStats(hits=0, misses=0)
        assert stats.hit_rate == 0.0

    def test_default_values(self):
        """Test CacheStats default values."""
        stats = CacheStats()
        assert stats.hits == 0
        assert stats.misses == 0
        assert stats.size == 0
        assert stats.max_size == 0


class TestNoOpCacheBackend:
    """Tests for NoOpCacheBackend (disabled cache)."""

    def test_get_always_returns_none(self):
        """Test that get always returns None."""
        cache = NoOpCacheBackend()
        assert cache.get("any_key") is None
        assert cache.get("8.8.8.8") is None

    def test_set_does_nothing(self):
        """Test that set is a no-op."""
        cache = NoOpCacheBackend()
        geo_data = GeoData(geoname_id=123, city="Test")

        # Should not raise any errors
        cache.set("key", geo_data)
        cache.set("key", geo_data, ttl=100)

        # Still returns None
        assert cache.get("key") is None

    def test_delete_does_nothing(self):
        """Test that delete is a no-op."""
        cache = NoOpCacheBackend()

        # Should not raise any errors
        cache.delete("any_key")
        cache.delete("nonexistent")

    def test_clear_does_nothing(self):
        """Test that clear is a no-op."""
        cache = NoOpCacheBackend()

        # Should not raise any errors
        cache.clear()

    def test_get_stats_returns_empty(self):
        """Test that get_stats returns empty statistics."""
        cache = NoOpCacheBackend()
        stats = cache.get_stats()

        assert stats.hits == 0
        assert stats.misses == 0
        assert stats.size == 0
        assert stats.max_size == 0

    def test_is_enabled_returns_false(self):
        """Test that is_enabled returns False."""
        cache = NoOpCacheBackend()
        assert cache.is_enabled() is False


class TestLRUCacheBackend:
    """Tests for LRUCacheBackend (LRU cache implementation)."""

    @pytest.fixture
    def cache_config(self):
        """Create a cache configuration for testing."""
        return CacheConfig(enabled=True, max_size=100, ttl=60)

    @pytest.fixture
    def cache(self, cache_config):
        """Create an LRU cache for testing."""
        return LRUCacheBackend(cache_config)

    @pytest.fixture
    def geo_data(self):
        """Create sample GeoData for testing."""
        return GeoData(
            geoname_id=5375480,
            ip_address="8.8.8.8",
            country_code="US",
            city="Mountain View",
        )

    def test_initialization(self, cache_config):
        """Test cache initialization."""
        cache = LRUCacheBackend(cache_config)

        assert cache.config == cache_config
        assert cache._enabled is True
        assert cache.cache is not None
        assert cache._hits == 0
        assert cache._misses == 0

    def test_initialization_disabled(self):
        """Test cache initialization when disabled."""
        config = CacheConfig(enabled=False)
        cache = LRUCacheBackend(config)

        assert cache._enabled is False
        assert cache.cache is None

    def test_set_and_get(self, cache, geo_data):
        """Test basic set and get operations."""
        cache.set("8.8.8.8", geo_data)
        result = cache.get("8.8.8.8")

        assert result is not None
        assert result.geoname_id == 5375480
        assert result.city == "Mountain View"

    def test_get_nonexistent_key(self, cache):
        """Test getting a nonexistent key returns None."""
        result = cache.get("nonexistent")
        assert result is None

    def test_get_increments_stats(self, cache, geo_data):
        """Test that get increments hit/miss statistics."""
        # First get - should be a miss
        result = cache.get("8.8.8.8")
        assert result is None
        stats = cache.get_stats()
        assert stats.hits == 0
        assert stats.misses == 1

        # Add data
        cache.set("8.8.8.8", geo_data)

        # Second get - should be a hit
        result = cache.get("8.8.8.8")
        assert result is not None
        stats = cache.get_stats()
        assert stats.hits == 1
        assert stats.misses == 1

    def test_delete(self, cache, geo_data):
        """Test deleting a key."""
        cache.set("8.8.8.8", geo_data)
        assert cache.get("8.8.8.8") is not None

        cache.delete("8.8.8.8")
        result = cache.get("8.8.8.8")
        assert result is None

    def test_delete_nonexistent_key(self, cache):
        """Test deleting a nonexistent key doesn't raise error."""
        # Should not raise any errors
        cache.delete("nonexistent")

    def test_clear(self, cache, geo_data):
        """Test clearing all cache entries."""
        # Add multiple entries
        cache.set("8.8.8.8", geo_data)
        cache.set("1.1.1.1", geo_data)
        cache.get("8.8.8.8")  # Create some hits

        assert cache.get_stats().size == 2
        assert cache.get_stats().hits > 0

        # Clear cache
        cache.clear()

        # Verify cache is empty and stats reset
        assert cache.get("8.8.8.8") is None
        stats = cache.get_stats()
        assert stats.size == 0
        assert stats.hits == 0
        assert stats.misses == 1  # From the get above

    def test_max_size_eviction(self):
        """Test that cache evicts entries when max size is reached."""
        config = CacheConfig(enabled=True, max_size=3, ttl=60)
        cache = LRUCacheBackend(config)

        geo_data = GeoData(geoname_id=123)

        # Fill cache to capacity
        cache.set("key1", geo_data)
        cache.set("key2", geo_data)
        cache.set("key3", geo_data)

        assert cache.get_stats().size == 3

        # Add one more - should evict least recently used
        cache.set("key4", geo_data)

        stats = cache.get_stats()
        assert stats.size == 3  # Still at max size

        # key4 should be present
        assert cache.get("key4") is not None

    def test_ttl_expiration(self):
        """Test that entries expire after TTL."""
        config = CacheConfig(enabled=True, max_size=100, ttl=1)  # 1 second TTL
        cache = LRUCacheBackend(config)

        geo_data = GeoData(geoname_id=123)
        cache.set("test_key", geo_data)

        # Should be available immediately
        assert cache.get("test_key") is not None

        # Wait for expiration
        time.sleep(1.1)

        # Should be expired now
        result = cache.get("test_key")
        assert result is None

    def test_get_stats(self, cache, geo_data):
        """Test getting cache statistics."""
        cache.set("8.8.8.8", geo_data)
        cache.set("1.1.1.1", geo_data)

        cache.get("8.8.8.8")  # hit
        cache.get("1.1.1.1")  # hit
        cache.get("2.2.2.2")  # miss

        stats = cache.get_stats()

        assert stats.hits == 2
        assert stats.misses == 1
        assert stats.size == 2
        assert stats.max_size == 100
        assert stats.hit_rate == pytest.approx(66.67, rel=0.1)

    def test_is_enabled(self, cache):
        """Test that is_enabled returns True."""
        assert cache.is_enabled() is True

    def test_disabled_cache_returns_none(self):
        """Test that disabled cache always returns None."""
        config = CacheConfig(enabled=False)
        cache = LRUCacheBackend(config)

        geo_data = GeoData(geoname_id=123)

        cache.set("key", geo_data)
        result = cache.get("key")

        assert result is None
        assert cache.is_enabled() is False

    def test_multiple_sets_same_key(self, cache):
        """Test setting same key multiple times updates value."""
        geo_data1 = GeoData(geoname_id=123, city="City1")
        geo_data2 = GeoData(geoname_id=456, city="City2")

        cache.set("key", geo_data1)
        assert cache.get("key").city == "City1"

        cache.set("key", geo_data2)
        assert cache.get("key").city == "City2"

        # Size should still be 1
        assert cache.get_stats().size == 1


class TestCacheFactory:
    """Tests for CacheFactory."""

    def test_create_lru_cache(self):
        """Test creating LRU cache backend."""
        config = CacheConfig(enabled=True, backend="lru", max_size=100, ttl=60)
        cache = CacheFactory.create_cache(config)

        assert isinstance(cache, LRUCacheBackend)
        assert cache.is_enabled() is True

    def test_create_disabled_cache(self):
        """Test creating disabled cache returns NoOpCacheBackend."""
        config = CacheConfig(enabled=False)
        cache = CacheFactory.create_cache(config)

        assert isinstance(cache, NoOpCacheBackend)
        assert cache.is_enabled() is False

    def test_unsupported_backend_raises_error(self):
        """Test that unsupported backend raises ValueError."""
        config = CacheConfig(enabled=True, backend="redis")

        with pytest.raises(ValueError) as exc_info:
            CacheFactory.create_cache(config)

        assert "Unsupported cache backend: redis" in str(exc_info.value)
        assert "Supported backends: 'lru'" in str(exc_info.value)

    def test_case_insensitive_backend_name(self):
        """Test that backend name is case-insensitive."""
        config1 = CacheConfig(enabled=True, backend="LRU")
        cache1 = CacheFactory.create_cache(config1)
        assert isinstance(cache1, LRUCacheBackend)

        config2 = CacheConfig(enabled=True, backend="Lru")
        cache2 = CacheFactory.create_cache(config2)
        assert isinstance(cache2, LRUCacheBackend)


class TestCacheIntegration:
    """Integration tests for cache system."""

    def test_cache_workflow(self):
        """Test complete cache workflow."""
        config = CacheConfig(enabled=True, backend="lru", max_size=10, ttl=60)
        cache = CacheFactory.create_cache(config)

        geo_data = GeoData(
            geoname_id=5375480,
            ip_address="8.8.8.8",
            country_code="US",
            city="Mountain View",
        )

        # Initial state
        assert cache.get_stats().size == 0

        # Add entry
        cache.set("8.8.8.8", geo_data)
        assert cache.get_stats().size == 1

        # Retrieve entry (hit)
        result = cache.get("8.8.8.8")
        assert result is not None
        assert result.city == "Mountain View"

        # Try nonexistent entry (miss)
        result = cache.get("1.1.1.1")
        assert result is None

        # Check statistics
        stats = cache.get_stats()
        assert stats.hits == 1
        assert stats.misses == 1
        assert stats.hit_rate == 50.0

        # Delete entry
        cache.delete("8.8.8.8")
        assert cache.get("8.8.8.8") is None
        assert cache.get_stats().size == 0

    def test_high_hit_rate_scenario(self):
        """Test scenario with high cache hit rate."""
        config = CacheConfig(enabled=True, max_size=100, ttl=60)
        cache = CacheFactory.create_cache(config)

        # Add some data
        for i in range(10):
            geo_data = GeoData(geoname_id=i, city=f"City{i}")
            cache.set(f"ip{i}", geo_data)

        # Access same IPs multiple times (high hit rate)
        for _ in range(10):
            for i in range(10):
                cache.get(f"ip{i}")

        stats = cache.get_stats()
        assert stats.hits == 100  # All hits
        assert stats.misses == 0
        assert stats.hit_rate == 100.0
