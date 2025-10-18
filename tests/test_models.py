"""Tests for core data models."""

from geoip_geocode.models import GeoData, ProviderConfig


def test_geodata_creation():
    """Test creating a GeoData object with required fields."""
    geo_data = GeoData(
        geoname_id=5375480,
        country_code="US",
        country_name="United States",
        city="Mountain View",
        latitude=37.386,
        longitude=-122.0838,
    )

    assert geo_data.geoname_id == 5375480
    assert geo_data.country_code == "US"
    assert geo_data.city == "Mountain View"
    assert geo_data.latitude == 37.386
    assert geo_data.longitude == -122.0838


def test_geodata_with_ip():
    """Test GeoData with IP address."""
    geo_data = GeoData(
        geoname_id=5375480,
        ip_address="8.8.8.8",
        country_code="US",
    )

    assert geo_data.geoname_id == 5375480
    assert geo_data.ip_address == "8.8.8.8"


def test_geodata_optional_fields():
    """Test that optional fields default to None."""
    geo_data = GeoData(geoname_id=12345)

    assert geo_data.geoname_id == 12345
    assert geo_data.ip_address is None
    assert geo_data.city is None
    assert geo_data.postal_code is None


def test_provider_config_creation():
    """Test creating a ProviderConfig."""
    config = ProviderConfig(
        name="geoip2",
        enabled=True,
        database_path="/path/to/db.mmdb",
    )

    assert config.name == "geoip2"
    assert config.enabled is True
    assert config.database_path == "/path/to/db.mmdb"


def test_provider_config_defaults():
    """Test ProviderConfig default values."""
    config = ProviderConfig(name="test")

    assert config.name == "test"
    assert config.enabled is True
    assert config.priority == 0
    assert config.timeout == 30
    assert config.max_retries == 3


def test_provider_config_priority():
    """Test setting priority in ProviderConfig."""
    config = ProviderConfig(name="test", priority=100)

    assert config.priority == 100
