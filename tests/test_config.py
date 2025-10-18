"""Tests for configuration management."""

import tempfile
from pathlib import Path

import pytest

from geoip_geocode.config import AppConfig, load_config
from geoip_geocode.models import ProviderConfig


def test_app_config_defaults():
    """Test AppConfig with default values."""
    config = AppConfig()

    assert config.default_provider == "geoip2"
    assert config.cache_enabled is False
    assert config.cache_ttl == 3600
    assert len(config.providers) == 0


def test_app_config_with_providers():
    """Test AppConfig with provider configurations."""
    provider_config = ProviderConfig(name="geoip2", database_path="/path/to/db")
    config = AppConfig(providers=[provider_config])

    assert len(config.providers) == 1
    assert config.providers[0].name == "geoip2"


def test_app_config_get_provider_config():
    """Test getting a specific provider config."""
    provider_config = ProviderConfig(name="geoip2", database_path="/path/to/db")
    config = AppConfig(providers=[provider_config])

    found = config.get_provider_config("geoip2")

    assert found is not None
    assert found.name == "geoip2"
    assert found.database_path == "/path/to/db"


def test_app_config_get_nonexistent_provider():
    """Test getting a non-existent provider config."""
    config = AppConfig()

    found = config.get_provider_config("nonexistent")

    assert found is None


def test_app_config_add_provider_config():
    """Test adding a provider config."""
    config = AppConfig()
    provider_config = ProviderConfig(name="geoip2", database_path="/path/to/db")

    config.add_provider_config(provider_config)

    assert len(config.providers) == 1
    assert config.providers[0].name == "geoip2"


def test_app_config_update_provider_config():
    """Test updating an existing provider config."""
    config = AppConfig()

    provider1 = ProviderConfig(name="geoip2", database_path="/old/path")
    config.add_provider_config(provider1)

    provider2 = ProviderConfig(name="geoip2", database_path="/new/path")
    config.add_provider_config(provider2)

    assert len(config.providers) == 1
    assert config.providers[0].database_path == "/new/path"


def test_app_config_to_yaml():
    """Test saving config to YAML."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yaml_path = Path(tmpdir) / "test_config.yaml"

        provider_config = ProviderConfig(name="geoip2", database_path="/path/to/db")
        config = AppConfig(default_provider="geoip2", providers=[provider_config])

        config.to_yaml(str(yaml_path))

        assert yaml_path.exists()


def test_app_config_from_yaml():
    """Test loading config from YAML."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yaml_path = Path(tmpdir) / "test_config.yaml"

        # Create and save config
        provider_config = ProviderConfig(
            name="geoip2", database_path="/path/to/db", priority=100
        )
        config = AppConfig(
            default_provider="geoip2", cache_enabled=True, providers=[provider_config]
        )
        config.to_yaml(str(yaml_path))

        # Load it back
        loaded_config = AppConfig.from_yaml(str(yaml_path))

        assert loaded_config.default_provider == "geoip2"
        assert loaded_config.cache_enabled is True
        assert len(loaded_config.providers) == 1
        assert loaded_config.providers[0].name == "geoip2"
        assert loaded_config.providers[0].database_path == "/path/to/db"
        assert loaded_config.providers[0].priority == 100


def test_app_config_from_nonexistent_yaml():
    """Test loading from non-existent YAML raises error."""
    with pytest.raises(FileNotFoundError):
        AppConfig.from_yaml("/nonexistent/path.yaml")


def test_load_config_defaults():
    """Test load_config with defaults."""
    config = load_config()

    assert config.default_provider == "geoip2"
    assert config.cache_enabled is False


def test_load_config_from_yaml():
    """Test load_config from YAML file."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yaml_path = Path(tmpdir) / "test_config.yaml"

        # Create config file
        provider_config = ProviderConfig(name="geoip2", database_path="/path/to/db")
        config = AppConfig(providers=[provider_config])
        config.to_yaml(str(yaml_path))

        # Load it
        loaded_config = load_config(yaml_path=str(yaml_path))

        assert len(loaded_config.providers) == 1
        assert loaded_config.providers[0].name == "geoip2"
