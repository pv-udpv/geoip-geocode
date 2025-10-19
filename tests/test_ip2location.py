"""Tests for IP2Location provider."""

import pytest
from unittest.mock import Mock, patch, MagicMock

from geoip_geocode.models import GeoData, ProviderConfig
from geoip_geocode.providers.ip2location import IP2LocationProvider


class TestIP2LocationProvider:
    """Test IP2Location provider implementation."""

    def test_init_missing_library(self):
        """Test initialization when IP2Location library is not available."""
        config = ProviderConfig(
            name="ip2location",
            database_path="/path/to/database.bin"
        )
        
        with patch('geoip_geocode.providers.ip2location.IP2Location', None):
            with pytest.raises(ImportError, match="IP2Location library is not installed"):
                IP2LocationProvider(config)

    def test_init_missing_database_path(self):
        """Test initialization without database path."""
        config = ProviderConfig(name="ip2location")
        
        with patch('geoip_geocode.providers.ip2location.IP2Location') as mock_ip2loc:
            with pytest.raises(ValueError, match="database_path is required"):
                IP2LocationProvider(config)

    def test_init_invalid_database_path(self):
        """Test initialization with invalid database path."""
        config = ProviderConfig(
            name="ip2location",
            database_path="/nonexistent/database.bin"
        )
        
        with patch('geoip_geocode.providers.ip2location.IP2Location') as mock_ip2loc:
            with pytest.raises(FileNotFoundError):
                IP2LocationProvider(config)

    @patch('geoip_geocode.providers.ip2location.IP2Location')
    @patch('pathlib.Path.exists', return_value=True)
    def test_init_success(self, mock_exists, mock_ip2loc_module):
        """Test successful initialization."""
        config = ProviderConfig(
            name="ip2location",
            database_path="/path/to/database.bin"
        )
        
        mock_db = Mock()
        mock_ip2loc_module.IP2Location.return_value = mock_db
        
        provider = IP2LocationProvider(config)
        
        assert provider.config == config
        assert provider.database == mock_db
        mock_ip2loc_module.IP2Location.assert_called_once_with("/path/to/database.bin")

    @patch('geoip_geocode.providers.ip2location.IP2Location')
    @patch('pathlib.Path.exists', return_value=True)
    def test_lookup_success(self, mock_exists, mock_ip2loc_module):
        """Test successful IP lookup."""
        config = ProviderConfig(
            name="ip2location",
            database_path="/path/to/database.bin"
        )
        
        # Mock IP2Location result
        mock_result = Mock()
        mock_result.country_short = "US"
        mock_result.country_long = "United States"
        mock_result.city = "Mountain View"
        mock_result.region = "California"
        mock_result.zipcode = "94043"
        mock_result.latitude = 37.386
        mock_result.longitude = -122.0838
        mock_result.timezone = "America/Los_Angeles"
        
        mock_db = Mock()
        mock_db.get_all.return_value = mock_result
        mock_ip2loc_module.IP2Location.return_value = mock_db
        
        provider = IP2LocationProvider(config)
        result = provider.lookup("8.8.8.8")
        
        assert result is not None
        assert isinstance(result, GeoData)
        assert result.ip_address == "8.8.8.8"
        assert result.country_code == "US"
        assert result.country_name == "United States"
        assert result.city == "Mountain View"
        assert result.subdivision == "California"
        assert result.postal_code == "94043"
        assert result.latitude == 37.386
        assert result.longitude == -122.0838
        assert result.time_zone == "America/Los_Angeles"
        assert result.continent_code == "NA"
        assert result.continent_name == "North America"
        assert result.provider == "ip2location"
        assert isinstance(result.geoname_id, int)
        assert result.geoname_id >= 900000000

    @patch('geoip_geocode.providers.ip2location.IP2Location')
    @patch('pathlib.Path.exists', return_value=True)
    def test_lookup_invalid_ip(self, mock_exists, mock_ip2loc_module):
        """Test lookup with invalid IP address."""
        config = ProviderConfig(
            name="ip2location",
            database_path="/path/to/database.bin"
        )
        
        mock_result = Mock()
        mock_result.country_short = "INVALID_IP_ADDRESS"
        
        mock_db = Mock()
        mock_db.get_all.return_value = mock_result
        mock_ip2loc_module.IP2Location.return_value = mock_db
        
        provider = IP2LocationProvider(config)
        result = provider.lookup("invalid.ip")
        
        assert result is None

    @patch('geoip_geocode.providers.ip2location.IP2Location')
    @patch('pathlib.Path.exists', return_value=True)
    def test_lookup_missing_coordinates(self, mock_exists, mock_ip2loc_module):
        """Test lookup with missing coordinates."""
        config = ProviderConfig(
            name="ip2location",
            database_path="/path/to/database.bin"
        )
        
        mock_result = Mock()
        mock_result.country_short = "US"
        mock_result.country_long = "United States"
        mock_result.city = "Unknown City"
        mock_result.region = "-"
        mock_result.zipcode = "-"
        mock_result.latitude = 0.0
        mock_result.longitude = 0.0
        mock_result.timezone = "-"
        
        mock_db = Mock()
        mock_db.get_all.return_value = mock_result
        mock_ip2loc_module.IP2Location.return_value = mock_db
        
        provider = IP2LocationProvider(config)
        result = provider.lookup("192.168.1.1")
        
        assert result is not None
        assert result.latitude is None
        assert result.longitude is None
        assert result.subdivision is None
        assert result.postal_code is None
        assert result.time_zone is None

    @patch('geoip_geocode.providers.ip2location.IP2Location')
    @patch('pathlib.Path.exists', return_value=True)
    def test_lookup_exception(self, mock_exists, mock_ip2loc_module):
        """Test lookup when database raises exception."""
        config = ProviderConfig(
            name="ip2location",
            database_path="/path/to/database.bin"
        )
        
        mock_db = Mock()
        mock_db.get_all.side_effect = Exception("Database error")
        mock_ip2loc_module.IP2Location.return_value = mock_db
        
        provider = IP2LocationProvider(config)
        
        # Should handle exception gracefully
        with patch('builtins.print') as mock_print:
            result = provider.lookup("8.8.8.8")
            assert result is None
            mock_print.assert_called_once()

    @patch('geoip_geocode.providers.ip2location.IP2Location')
    @patch('pathlib.Path.exists', return_value=True)
    def test_is_available_enabled(self, mock_exists, mock_ip2loc_module):
        """Test is_available when provider is enabled and working."""
        config = ProviderConfig(
            name="ip2location",
            enabled=True,
            database_path="/path/to/database.bin"
        )
        
        mock_db = Mock()
        mock_ip2loc_module.IP2Location.return_value = mock_db
        
        provider = IP2LocationProvider(config)
        assert provider.is_available() is True

    @patch('geoip_geocode.providers.ip2location.IP2Location')
    @patch('pathlib.Path.exists', return_value=True)
    def test_is_available_disabled(self, mock_exists, mock_ip2loc_module):
        """Test is_available when provider is disabled."""
        config = ProviderConfig(
            name="ip2location",
            enabled=False,
            database_path="/path/to/database.bin"
        )
        
        mock_db = Mock()
        mock_ip2loc_module.IP2Location.return_value = mock_db
        
        provider = IP2LocationProvider(config)
        assert provider.is_available() is False

    def test_is_available_no_library(self):
        """Test is_available when IP2Location library is not available."""
        config = ProviderConfig(
            name="ip2location",
            enabled=True,
            database_path="/path/to/database.bin"
        )
        
        with patch('geoip_geocode.providers.ip2location.IP2Location', None):
            # This will raise ImportError during init, but let's test the logic
            with patch('pathlib.Path.exists', return_value=True):
                try:
                    provider = IP2LocationProvider(config)
                    provider.database = None
                    assert provider.is_available() is False
                except ImportError:
                    # Expected when library is not available
                    pass

    @patch('geoip_geocode.providers.ip2location.IP2Location')
    @patch('pathlib.Path.exists', return_value=True)
    def test_close(self, mock_exists, mock_ip2loc_module):
        """Test closing database connection."""
        config = ProviderConfig(
            name="ip2location",
            database_path="/path/to/database.bin"
        )
        
        mock_db = Mock()
        mock_ip2loc_module.IP2Location.return_value = mock_db
        
        provider = IP2LocationProvider(config)
        assert provider.database is not None
        
        provider.close()
        assert provider.database is None

    def test_generate_synthetic_geoname_id(self):
        """Test synthetic geoname_id generation."""
        config = ProviderConfig(name="ip2location")
        
        with patch('geoip_geocode.providers.ip2location.IP2Location'):
            with patch('pathlib.Path.exists', return_value=True):
                provider = IP2LocationProvider.__new__(IP2LocationProvider)
                
                # Test consistent ID generation
                id1 = provider._generate_synthetic_geoname_id("US", "New York")
                id2 = provider._generate_synthetic_geoname_id("US", "New York")
                assert id1 == id2
                assert id1 >= 900000000
                
                # Test different locations generate different IDs
                id3 = provider._generate_synthetic_geoname_id("GB", "London")
                assert id1 != id3
                
                # Test handling of None/empty values
                id4 = provider._generate_synthetic_geoname_id(None, None)
                assert isinstance(id4, int)
                assert id4 >= 900000000

    def test_continent_mapping(self):
        """Test continent code and name mapping."""
        config = ProviderConfig(name="ip2location")
        
        with patch('geoip_geocode.providers.ip2location.IP2Location'):
            with patch('pathlib.Path.exists', return_value=True):
                provider = IP2LocationProvider.__new__(IP2LocationProvider)
                
                # Test known mappings
                assert provider._get_continent_code("US") == "NA"
                assert provider._get_continent_code("GB") == "EU"
                assert provider._get_continent_code("CN") == "AS"
                assert provider._get_continent_code("BR") == "SA"
                assert provider._get_continent_code("ZA") == "AF"
                assert provider._get_continent_code("AU") == "OC"
                
                # Test unknown country
                assert provider._get_continent_code("XX") is None
                
                # Test continent names
                assert provider._get_continent_name("US") == "North America"
                assert provider._get_continent_name("GB") == "Europe"
                assert provider._get_continent_name("CN") == "Asia"
                assert provider._get_continent_name("BR") == "South America"
                assert provider._get_continent_name("ZA") == "Africa"
                assert provider._get_continent_name("AU") == "Oceania"
                
                # Test unknown country name
                assert provider._get_continent_name("XX") is None

    @patch('geoip_geocode.providers.ip2location.IP2Location')
    @patch('pathlib.Path.exists', return_value=True)
    def test_context_manager(self, mock_exists, mock_ip2loc_module):
        """Test provider as context manager."""
        config = ProviderConfig(
            name="ip2location",
            database_path="/path/to/database.bin"
        )
        
        mock_db = Mock()
        mock_ip2loc_module.IP2Location.return_value = mock_db
        
        # Test context manager protocol
        with IP2LocationProvider(config) as provider:
            assert provider.database is not None
        
        # Database should be closed after context
        assert provider.database is None