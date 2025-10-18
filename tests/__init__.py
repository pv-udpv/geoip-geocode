"""Test package initialization."""


def test_package_imports():
    """Test that core package imports work."""
    from geoip_geocode import GeoData, ProviderConfig, ProviderRegistry, get_registry

    assert GeoData is not None
    assert ProviderConfig is not None
    assert ProviderRegistry is not None
    assert get_registry is not None


def test_version():
    """Test that version is accessible."""
    from geoip_geocode import __version__

    assert __version__ is not None
    assert isinstance(__version__, str)
