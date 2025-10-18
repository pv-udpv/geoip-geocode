"""Tests for MultiDatabaseGeoIP2Provider."""

import pytest
from unittest.mock import Mock, MagicMock, patch
from pathlib import Path

from geoip_geocode.providers.multi_database import MultiDatabaseGeoIP2Provider
from geoip_geocode.models import ProviderConfig, CacheConfig, EnrichedGeoData
from geoip_geocode.cache import CacheStats


class TestMultiDatabaseProviderInitialization:
    """Tests for provider initialization."""

    @patch('geoip_geocode.providers.multi_database.geoip2.database.Reader')
    @patch('geoip_geocode.providers.multi_database.Path')
    def test_init_with_city_database(self, mock_path, mock_reader):
        """Test initialization with City database only."""
        # Setup mocks
        mock_path_instance = MagicMock()
        mock_path_instance.exists.return_value = True
        mock_path.return_value = mock_path_instance

        config = ProviderConfig(
            name="test",
            city_database_path="/fake/city.mmdb"
        )

        provider = MultiDatabaseGeoIP2Provider(config)

        assert provider.city_reader is not None
        assert provider.asn_reader is None
        assert provider.cache is not None

    @patch('geoip_geocode.providers.multi_database.geoip2.database.Reader')
    @patch('geoip_geocode.providers.multi_database.Path')
    def test_init_with_city_and_asn_databases(self, mock_path, mock_reader):
        """Test initialization with both City and ASN databases."""
        # Setup mocks
        mock_path_instance = MagicMock()
        mock_path_instance.exists.return_value = True
        mock_path.return_value = mock_path_instance

        config = ProviderConfig(
            name="test",
            city_database_path="/fake/city.mmdb",
            asn_database_path="/fake/asn.mmdb"
        )

        provider = MultiDatabaseGeoIP2Provider(config)

        assert provider.city_reader is not None
        assert provider.asn_reader is not None

    @patch('geoip_geocode.providers.multi_database.geoip2.database.Reader')
    @patch('geoip_geocode.providers.multi_database.Path')
    def test_init_with_backward_compatible_database_path(self, mock_path, mock_reader):
        """Test backward compatibility with database_path parameter."""
        # Setup mocks
        mock_path_instance = MagicMock()
        mock_path_instance.exists.return_value = True
        mock_path.return_value = mock_path_instance

        config = ProviderConfig(
            name="test",
            database_path="/fake/city.mmdb"  # Old parameter name
        )

        provider = MultiDatabaseGeoIP2Provider(config)

        assert provider.city_reader is not None

    def test_init_without_database_path_raises_error(self):
        """Test that initialization without database path raises ValueError."""
        config = ProviderConfig(name="test")

        with pytest.raises(ValueError) as exc_info:
            MultiDatabaseGeoIP2Provider(config)

        assert "Either 'city_database_path' or 'database_path' must be provided" in str(exc_info.value)

    @patch('geoip_geocode.providers.multi_database.Path')
    def test_init_with_missing_city_database_raises_error(self, mock_path):
        """Test that missing City database raises FileNotFoundError."""
        mock_path_instance = MagicMock()
        mock_path_instance.exists.return_value = False
        mock_path.return_value = mock_path_instance

        config = ProviderConfig(
            name="test",
            city_database_path="/fake/nonexistent.mmdb"
        )

        with pytest.raises(FileNotFoundError) as exc_info:
            MultiDatabaseGeoIP2Provider(config)

        assert "City database not found" in str(exc_info.value)

    @patch('geoip_geocode.providers.multi_database.geoip2.database.Reader')
    @patch('geoip_geocode.providers.multi_database.Path')
    def test_init_with_missing_asn_database_raises_error(self, mock_path, mock_reader):
        """Test that missing ASN database raises FileNotFoundError."""
        def path_exists_side_effect(path_str):
            mock_instance = MagicMock()
            # City exists, ASN doesn't
            mock_instance.exists.return_value = "/city.mmdb" in path_str
            return mock_instance

        mock_path.side_effect = path_exists_side_effect

        config = ProviderConfig(
            name="test",
            city_database_path="/fake/city.mmdb",
            asn_database_path="/fake/nonexistent-asn.mmdb"
        )

        with pytest.raises(FileNotFoundError) as exc_info:
            MultiDatabaseGeoIP2Provider(config)

        assert "ASN database not found" in str(exc_info.value)

    @patch('geoip_geocode.providers.multi_database.geoip2.database.Reader')
    @patch('geoip_geocode.providers.multi_database.Path')
    def test_init_with_cache_config(self, mock_path, mock_reader):
        """Test initialization with custom cache configuration."""
        mock_path_instance = MagicMock()
        mock_path_instance.exists.return_value = True
        mock_path.return_value = mock_path_instance

        config = ProviderConfig(name="test", city_database_path="/fake/city.mmdb")
        cache_config = CacheConfig(enabled=True, max_size=5000, ttl=1800)

        provider = MultiDatabaseGeoIP2Provider(config, cache_config)

        assert provider.cache is not None
        assert provider.cache.is_enabled() is True


class TestMultiDatabaseProviderLookup:
    """Tests for lookup operations."""

    @pytest.fixture
    def mock_city_response(self):
        """Create a mock City database response."""
        response = Mock()
        response.city.geoname_id = 5375480
        response.city.name = "Mountain View"
        response.country.geoname_id = None
        response.country.iso_code = "US"
        response.country.name = "United States"
        response.postal.code = "94043"
        response.location.latitude = 37.386
        response.location.longitude = -122.0838
        response.location.time_zone = "America/Los_Angeles"
        response.location.accuracy_radius = 1000
        response.continent.code = "NA"
        response.continent.name = "North America"
        response.subdivisions = []
        return response

    @pytest.fixture
    def mock_asn_response(self):
        """Create a mock ASN database response."""
        response = Mock()
        response.autonomous_system_number = 15169
        response.autonomous_system_organization = "Google LLC"
        response.network = "8.8.8.0/24"
        return response

    @patch('geoip_geocode.providers.multi_database.geoip2.database.Reader')
    @patch('geoip_geocode.providers.multi_database.Path')
    def test_lookup_with_city_only(self, mock_path, mock_reader, mock_city_response):
        """Test lookup with City database only."""
        # Setup mocks
        mock_path_instance = MagicMock()
        mock_path_instance.exists.return_value = True
        mock_path.return_value = mock_path_instance

        mock_reader_instance = MagicMock()
        mock_reader_instance.city.return_value = mock_city_response
        mock_reader.return_value = mock_reader_instance

        config = ProviderConfig(name="test", city_database_path="/fake/city.mmdb")
        provider = MultiDatabaseGeoIP2Provider(config)

        result = provider.lookup("8.8.8.8")

        assert result is not None
        assert isinstance(result, EnrichedGeoData)
        assert result.city == "Mountain View"
        assert result.country_code == "US"
        assert result.asn is None  # No ASN database
        assert result.asn_organization is None

    @patch('geoip_geocode.providers.multi_database.geoip2.database.Reader')
    @patch('geoip_geocode.providers.multi_database.Path')
    def test_lookup_with_city_and_asn(self, mock_path, mock_reader, mock_city_response, mock_asn_response):
        """Test lookup with both City and ASN databases."""
        # Setup mocks
        mock_path_instance = MagicMock()
        mock_path_instance.exists.return_value = True
        mock_path.return_value = mock_path_instance

        mock_city_reader = MagicMock()
        mock_city_reader.city.return_value = mock_city_response

        mock_asn_reader = MagicMock()
        mock_asn_reader.asn.return_value = mock_asn_response

        mock_reader.side_effect = [mock_city_reader, mock_asn_reader]

        config = ProviderConfig(
            name="test",
            city_database_path="/fake/city.mmdb",
            asn_database_path="/fake/asn.mmdb"
        )
        provider = MultiDatabaseGeoIP2Provider(config)

        result = provider.lookup("8.8.8.8")

        assert result is not None
        assert isinstance(result, EnrichedGeoData)
        assert result.city == "Mountain View"
        assert result.country_code == "US"
        assert result.asn == 15169
        assert result.asn_organization == "Google LLC"
        assert result.network == "8.8.8.0/24"

    @patch('geoip_geocode.providers.multi_database.geoip2.database.Reader')
    @patch('geoip_geocode.providers.multi_database.Path')
    def test_lookup_with_cache_hit(self, mock_path, mock_reader, mock_city_response):
        """Test lookup with cache hit."""
        # Setup mocks
        mock_path_instance = MagicMock()
        mock_path_instance.exists.return_value = True
        mock_path.return_value = mock_path_instance

        mock_reader_instance = MagicMock()
        mock_reader_instance.city.return_value = mock_city_response
        mock_reader.return_value = mock_reader_instance

        config = ProviderConfig(name="test", city_database_path="/fake/city.mmdb")
        cache_config = CacheConfig(enabled=True, max_size=100, ttl=60)
        provider = MultiDatabaseGeoIP2Provider(config, cache_config)

        # First lookup - cache miss
        result1 = provider.lookup("8.8.8.8")
        assert result1 is not None

        # Second lookup - should hit cache
        result2 = provider.lookup("8.8.8.8")
        assert result2 is not None
        assert result2.city == result1.city

        # Verify cache statistics
        stats = provider.get_cache_stats()
        assert stats.hits == 1
        assert stats.misses == 1

    @patch('geoip_geocode.providers.multi_database.geoip2.database.Reader')
    @patch('geoip_geocode.providers.multi_database.Path')
    def test_lookup_ip_not_found(self, mock_path, mock_reader):
        """Test lookup when IP is not found in database."""
        # Setup mocks
        mock_path_instance = MagicMock()
        mock_path_instance.exists.return_value = True
        mock_path.return_value = mock_path_instance

        import geoip2.errors
        mock_reader_instance = MagicMock()
        mock_reader_instance.city.side_effect = geoip2.errors.AddressNotFoundError("IP not found")
        mock_reader.return_value = mock_reader_instance

        config = ProviderConfig(name="test", city_database_path="/fake/city.mmdb")
        provider = MultiDatabaseGeoIP2Provider(config)

        result = provider.lookup("192.168.1.1")

        assert result is None

    @patch('geoip_geocode.providers.multi_database.geoip2.database.Reader')
    @patch('geoip_geocode.providers.multi_database.Path')
    def test_lookup_with_no_geoname_id(self, mock_path, mock_reader):
        """Test lookup when response has no geoname_id."""
        # Setup mocks
        mock_path_instance = MagicMock()
        mock_path_instance.exists.return_value = True
        mock_path.return_value = mock_path_instance

        mock_response = Mock()
        mock_response.city.geoname_id = None
        mock_response.country.geoname_id = None  # Both None

        mock_reader_instance = MagicMock()
        mock_reader_instance.city.return_value = mock_response
        mock_reader.return_value = mock_reader_instance

        config = ProviderConfig(name="test", city_database_path="/fake/city.mmdb")
        provider = MultiDatabaseGeoIP2Provider(config)

        result = provider.lookup("8.8.8.8")

        assert result is None


class TestMultiDatabaseProviderCacheManagement:
    """Tests for cache management operations."""

    @patch('geoip_geocode.providers.multi_database.geoip2.database.Reader')
    @patch('geoip_geocode.providers.multi_database.Path')
    def test_get_cache_stats(self, mock_path, mock_reader):
        """Test getting cache statistics."""
        mock_path_instance = MagicMock()
        mock_path_instance.exists.return_value = True
        mock_path.return_value = mock_path_instance
        mock_reader.return_value = MagicMock()

        config = ProviderConfig(name="test", city_database_path="/fake/city.mmdb")
        cache_config = CacheConfig(enabled=True, max_size=100, ttl=60)
        provider = MultiDatabaseGeoIP2Provider(config, cache_config)

        stats = provider.get_cache_stats()

        assert isinstance(stats, CacheStats)
        assert stats.hits == 0
        assert stats.misses == 0
        assert stats.max_size == 100

    @patch('geoip_geocode.providers.multi_database.geoip2.database.Reader')
    @patch('geoip_geocode.providers.multi_database.Path')
    def test_clear_cache(self, mock_path, mock_reader):
        """Test clearing cache."""
        mock_path_instance = MagicMock()
        mock_path_instance.exists.return_value = True
        mock_path.return_value = mock_path_instance

        mock_city_response = Mock()
        mock_city_response.city.geoname_id = 123
        mock_city_response.city.name = "Test"
        mock_city_response.country.geoname_id = None
        mock_city_response.country.iso_code = "US"
        mock_city_response.country.name = "United States"
        mock_city_response.postal.code = None
        mock_city_response.location.latitude = 0.0
        mock_city_response.location.longitude = 0.0
        mock_city_response.location.time_zone = "UTC"
        mock_city_response.location.accuracy_radius = 100
        mock_city_response.continent.code = "NA"
        mock_city_response.continent.name = "North America"
        mock_city_response.subdivisions = []

        mock_reader_instance = MagicMock()
        mock_reader_instance.city.return_value = mock_city_response
        mock_reader.return_value = mock_reader_instance

        config = ProviderConfig(name="test", city_database_path="/fake/city.mmdb")
        cache_config = CacheConfig(enabled=True, max_size=100, ttl=60)
        provider = MultiDatabaseGeoIP2Provider(config, cache_config)

        # Add some data to cache
        provider.lookup("8.8.8.8")
        assert provider.get_cache_stats().size > 0

        # Clear cache
        provider.clear_cache()

        stats = provider.get_cache_stats()
        assert stats.size == 0
        assert stats.hits == 0
        assert stats.misses == 0


class TestMultiDatabaseProviderAvailability:
    """Tests for provider availability checks."""

    @patch('geoip_geocode.providers.multi_database.geoip2.database.Reader')
    @patch('geoip_geocode.providers.multi_database.Path')
    def test_is_available_when_enabled(self, mock_path, mock_reader):
        """Test is_available returns True when enabled."""
        mock_path_instance = MagicMock()
        mock_path_instance.exists.return_value = True
        mock_path.return_value = mock_path_instance
        mock_reader.return_value = MagicMock()

        config = ProviderConfig(
            name="test",
            enabled=True,
            city_database_path="/fake/city.mmdb"
        )
        provider = MultiDatabaseGeoIP2Provider(config)

        assert provider.is_available() is True

    @patch('geoip_geocode.providers.multi_database.geoip2.database.Reader')
    @patch('geoip_geocode.providers.multi_database.Path')
    def test_is_available_when_disabled(self, mock_path, mock_reader):
        """Test is_available returns False when disabled."""
        mock_path_instance = MagicMock()
        mock_path_instance.exists.return_value = True
        mock_path.return_value = mock_path_instance
        mock_reader.return_value = MagicMock()

        config = ProviderConfig(
            name="test",
            enabled=False,
            city_database_path="/fake/city.mmdb"
        )
        provider = MultiDatabaseGeoIP2Provider(config)

        assert provider.is_available() is False


class TestMultiDatabaseProviderClose:
    """Tests for provider cleanup."""

    @patch('geoip_geocode.providers.multi_database.geoip2.database.Reader')
    @patch('geoip_geocode.providers.multi_database.Path')
    def test_close_closes_readers(self, mock_path, mock_reader):
        """Test that close() closes all database readers."""
        mock_path_instance = MagicMock()
        mock_path_instance.exists.return_value = True
        mock_path.return_value = mock_path_instance

        mock_city_reader = MagicMock()
        mock_asn_reader = MagicMock()
        mock_reader.side_effect = [mock_city_reader, mock_asn_reader]

        config = ProviderConfig(
            name="test",
            city_database_path="/fake/city.mmdb",
            asn_database_path="/fake/asn.mmdb"
        )
        provider = MultiDatabaseGeoIP2Provider(config)

        provider.close()

        mock_city_reader.close.assert_called_once()
        mock_asn_reader.close.assert_called_once()
        assert provider.city_reader is None
        assert provider.asn_reader is None
