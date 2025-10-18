"""Tests for provider registry."""

import pytest

from geoip_geocode.models import ProviderConfig
from geoip_geocode.registry import BaseProvider, ProviderRegistry, get_registry


class MockProvider(BaseProvider):
    """Mock provider for testing."""

    def lookup(self, ip_address: str):
        """Mock lookup."""
        from geoip_geocode.models import GeoData

        return GeoData(
            geoname_id=12345,
            ip_address=ip_address,
            city="Test City",
        )


def test_provider_registry_register():
    """Test registering a provider."""
    registry = ProviderRegistry()
    registry.register("mock", MockProvider)

    assert "mock" in registry.list_providers()


def test_provider_registry_get_provider():
    """Test getting a provider instance."""
    registry = ProviderRegistry()
    registry.register("mock", MockProvider)

    config = ProviderConfig(name="mock", enabled=True)
    provider = registry.get_provider("mock", config)

    assert provider is not None
    assert isinstance(provider, MockProvider)


def test_provider_registry_unregister():
    """Test unregistering a provider."""
    registry = ProviderRegistry()
    registry.register("mock", MockProvider)

    assert "mock" in registry.list_providers()

    registry.unregister("mock")

    assert "mock" not in registry.list_providers()


def test_provider_registry_list_providers():
    """Test listing providers."""
    registry = ProviderRegistry()
    registry.register("mock1", MockProvider)
    registry.register("mock2", MockProvider)

    providers = registry.list_providers()

    assert "mock1" in providers
    assert "mock2" in providers
    assert len(providers) == 2


def test_provider_lookup():
    """Test provider lookup method."""
    config = ProviderConfig(name="mock", enabled=True)
    provider = MockProvider(config)

    result = provider.lookup("8.8.8.8")

    assert result is not None
    assert result.geoname_id == 12345
    assert result.ip_address == "8.8.8.8"
    assert result.city == "Test City"


def test_provider_is_available():
    """Test provider availability check."""
    config = ProviderConfig(name="mock", enabled=True)
    provider = MockProvider(config)

    assert provider.is_available() is True

    config_disabled = ProviderConfig(name="mock", enabled=False)
    provider_disabled = MockProvider(config_disabled)

    assert provider_disabled.is_available() is False


def test_get_registry_singleton():
    """Test that get_registry returns the same instance."""
    registry1 = get_registry()
    registry2 = get_registry()

    assert registry1 is registry2


def test_provider_priority_sorting():
    """Test that providers are sorted by priority."""
    registry = ProviderRegistry()
    registry.register("mock", MockProvider)

    config1 = ProviderConfig(name="mock", enabled=True, priority=10)
    config2 = ProviderConfig(name="mock", enabled=True, priority=50)

    registry.get_provider("mock", config1)

    # Replace with higher priority
    registry.get_provider("mock", config2)

    available = registry.get_available_providers()

    # Should have the latest instance
    assert len(available) == 1
    assert available[0].config.priority == 50


def test_invalid_provider_registration():
    """Test that registering invalid provider raises error."""
    registry = ProviderRegistry()

    class NotAProvider:
        pass

    with pytest.raises(ValueError):
        registry.register("invalid", NotAProvider)
