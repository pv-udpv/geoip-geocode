"""Integration test demonstrating complete workflow."""

import tempfile
from pathlib import Path

from geoip_geocode.config import AppConfig, load_config
from geoip_geocode.models import GeoData, ProviderConfig
from geoip_geocode.registry import BaseProvider, ProviderRegistry, get_registry


class MockProvider(BaseProvider):
    """Mock provider that returns test data."""

    def lookup(self, ip_address: str):
        """Return mock GeoData."""
        if ip_address == "8.8.8.8":
            return GeoData(
                geoname_id=5375480,
                ip_address=ip_address,
                country_code="US",
                country_name="United States",
                city="Mountain View",
                latitude=37.386,
                longitude=-122.0838,
                time_zone="America/Los_Angeles",
                provider="mock",
            )
        return None


def test_complete_workflow():
    """Test complete workflow from config to lookup."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Step 1: Create configuration
        config = AppConfig(default_provider="mock")

        # Step 2: Add provider configuration
        provider_config = ProviderConfig(
            name="mock", enabled=True, priority=100, database_path="/mock/path"
        )
        config.add_provider_config(provider_config)

        # Step 3: Save configuration to YAML
        yaml_path = Path(tmpdir) / "config.yaml"
        config.to_yaml(str(yaml_path))

        # Step 4: Load configuration back
        loaded_config = load_config(yaml_path=str(yaml_path))

        assert loaded_config.default_provider == "mock"
        assert len(loaded_config.providers) == 1

        # Step 5: Initialize registry
        registry = ProviderRegistry()
        registry.register("mock", MockProvider)

        # Step 6: Get provider from registry
        mock_config = loaded_config.get_provider_config("mock")
        assert mock_config is not None

        provider = registry.get_provider("mock", mock_config)
        assert provider is not None
        assert provider.is_available()

        # Step 7: Perform lookup
        result = provider.lookup("8.8.8.8")

        assert result is not None
        assert result.geoname_id == 5375480
        assert result.city == "Mountain View"
        assert result.country_name == "United States"
        assert result.provider == "mock"

        # Step 8: Test non-existent IP
        no_result = provider.lookup("1.2.3.4")
        assert no_result is None


def test_multiple_providers_priority():
    """Test provider priority system."""
    registry = ProviderRegistry()
    registry.register("mock", MockProvider)

    # Create two providers with different priorities
    low_priority = ProviderConfig(name="mock", enabled=True, priority=10)
    high_priority = ProviderConfig(name="mock", enabled=True, priority=100)

    # Add to registry
    registry.get_provider("mock", low_priority)

    # Replace with higher priority
    registry.get_provider("mock", high_priority)

    # Get available providers (should be sorted by priority)
    providers = registry.get_available_providers()

    assert len(providers) == 1
    assert providers[0].config.priority == 100


def test_config_roundtrip():
    """Test configuration save and load roundtrip."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yaml_path = Path(tmpdir) / "config.yaml"

        # Create config
        original = AppConfig(
            default_provider="geoip2", cache_enabled=True, cache_ttl=7200
        )

        provider_config = ProviderConfig(
            name="geoip2",
            enabled=True,
            priority=100,
            database_path="/path/to/db.mmdb",
            timeout=60,
            max_retries=5,
        )
        original.add_provider_config(provider_config)

        # Save
        original.to_yaml(str(yaml_path))

        # Load
        loaded = AppConfig.from_yaml(str(yaml_path))

        # Verify
        assert loaded.default_provider == "geoip2"
        assert loaded.cache_enabled is True
        assert loaded.cache_ttl == 7200
        assert len(loaded.providers) == 1

        loaded_provider = loaded.providers[0]
        assert loaded_provider.name == "geoip2"
        assert loaded_provider.priority == 100
        assert loaded_provider.database_path == "/path/to/db.mmdb"
        assert loaded_provider.timeout == 60
        assert loaded_provider.max_retries == 5


def test_geodata_serialization():
    """Test GeoData serialization."""
    geo = GeoData(
        geoname_id=5375480,
        ip_address="8.8.8.8",
        country_code="US",
        city="Mountain View",
        latitude=37.386,
        longitude=-122.0838,
    )

    # Test dict conversion
    geo_dict = geo.model_dump()
    assert geo_dict["geoname_id"] == 5375480
    assert geo_dict["city"] == "Mountain View"

    # Test JSON conversion
    geo_json = geo.model_dump_json()
    assert isinstance(geo_json, str)
    assert "5375480" in geo_json
    assert "Mountain View" in geo_json

    # Test recreation from dict
    recreated = GeoData(**geo_dict)
    assert recreated.geoname_id == geo.geoname_id
    assert recreated.city == geo.city
