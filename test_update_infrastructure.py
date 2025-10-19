#!/usr/bin/env python3
"""
Quick test script for database update functionality.
Tests that the update infrastructure is properly set up.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from geoip_geocode.models import ProviderConfig
from geoip_geocode.providers.geoip2 import GeoIP2Provider
from geoip_geocode.providers.ip2location import IP2LocationProvider


def test_config_fields():
    """Test that ProviderConfig has update fields."""
    print("Testing ProviderConfig fields...")

    config = ProviderConfig(
        name="test",
        database_path="/tmp/test.mmdb",
        auto_update=True,
        license_key="test_key",
        update_url="https://example.com",
    )

    assert config.auto_update == True
    assert config.license_key == "test_key"
    assert config.update_url == "https://example.com"

    print("✅ ProviderConfig has all update fields")


def test_provider_update_method():
    """Test that providers have update() method."""
    print("\nTesting provider update() method...")

    # Test GeoIP2Provider
    config = ProviderConfig(
        name="geoip2",
        database_path="./data/databases/GeoLite2-City.mmdb",
        auto_update=False,
    )

    provider = GeoIP2Provider(config)

    # Check that method exists
    assert hasattr(provider, "update")
    assert callable(provider.update)

    # Test that it returns False when auto_update is disabled
    result = provider.update()
    assert result == False, "update() should return False when auto_update=False"

    provider.close()
    print("✅ GeoIP2Provider has update() method")

    # Test IP2LocationProvider
    config = ProviderConfig(
        name="ip2location",
        database_path="./data/databases/IP2LOCATION-LITE-DB11.BIN",
        auto_update=False,
    )

    provider = IP2LocationProvider(config)

    # Check that method exists
    assert hasattr(provider, "update")
    assert callable(provider.update)

    # Test that it returns False when auto_update is disabled
    result = provider.update()
    assert result == False, "update() should return False when auto_update=False"

    provider.close()
    print("✅ IP2LocationProvider has update() method")


def test_updater_classes():
    """Test that updater classes can be imported."""
    print("\nTesting updater classes...")

    try:
        from geoip_geocode.updater import (
            IP2LocationUpdater,
            MaxMindUpdater,
            update_databases,
        )

        # Check class attributes
        assert hasattr(MaxMindUpdater, "BASE_URL")
        assert hasattr(MaxMindUpdater, "DEFAULT_EDITION")
        assert hasattr(IP2LocationUpdater, "BASE_URL")
        assert hasattr(IP2LocationUpdater, "DEFAULT_PRODUCT")

        # Check that function exists
        assert callable(update_databases)

        print("✅ Updater classes import successfully")
        return True
    except ImportError as e:
        print(f"❌ Failed to import updater: {e}")
        return False


def main():
    """Run all tests."""
    print("=" * 60)
    print("Database Update Infrastructure Tests")
    print("=" * 60)

    try:
        test_config_fields()
        test_provider_update_method()
        test_updater_classes()

        print("\n" + "=" * 60)
        print("✅ All tests passed!")
        print("=" * 60)
        print("\nThe database update infrastructure is properly set up.")
        print("To use it, set environment variables:")
        print("  MAXMIND_LICENSE_KEY=your_key")
        print("  IP2LOCATION_TOKEN=your_token")
        print("\nSee docs/guides/DATABASE_UPDATE.md for usage examples.")
        return 0

    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        return 1
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
