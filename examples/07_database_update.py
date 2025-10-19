"""
Example 07: Database Auto-Update

This example demonstrates how to use the auto-update functionality
to download and update GeoIP databases from remote sources.

Environment variables required:
    - For MaxMind:
        MAXMIND_LICENSE_KEY: Your MaxMind license key
        MAXMIND_ACCOUNT_ID: (optional) Your MaxMind account ID
        MAXMIND_EDITION_ID: (optional) Database edition (default: GeoLite2-City)

    - For IP2Location:
        IP2LOCATION_TOKEN: Your IP2Location download token
        IP2LOCATION_PRODUCT_CODE: (optional) Product code (default: DB11LITE)
"""

import os
from pathlib import Path

from geoip_geocode.config import AppConfig
from geoip_geocode.models import ProviderConfig
from geoip_geocode.providers.geoip2 import GeoIP2Provider
from geoip_geocode.providers.ip2location import IP2LocationProvider


def example_maxmind_update():
    """Update MaxMind GeoLite2 database."""
    print("=" * 60)
    print("MaxMind Database Update Example")
    print("=" * 60)

    # Check for license key
    license_key = os.getenv("MAXMIND_LICENSE_KEY")
    if not license_key:
        print("\n⚠️  MAXMIND_LICENSE_KEY not set")
        print("Set it in .env file or environment:")
        print("  export MAXMIND_LICENSE_KEY='your_license_key'")
        print("\nGet a free license key at: https://www.maxmind.com/en/geolite2/signup")
        return

    # Create provider config with auto_update enabled
    config = ProviderConfig(
        name="geoip2",
        database_path="./data/databases/GeoLite2-City.mmdb",
        enabled=True,
        auto_update=True,
        license_key=license_key,
    )

    # Create provider
    provider = GeoIP2Provider(config)

    print("\n📦 Configuration:")
    print(f"  Database: {config.database_path}")
    print(f"  Auto-update: {config.auto_update}")
    print(f"  License key: {'*' * 20}")

    # Check if database exists
    db_exists = Path(config.database_path).exists()
    print(f"\n📁 Database exists: {db_exists}")

    # Update database
    print("\n🔄 Updating database...")
    success = provider.update()

    if success:
        print("✅ Database updated successfully!")

        # Test lookup
        print("\n🔍 Testing database with lookup:")
        result = provider.lookup("8.8.8.8")
        if result:
            print(f"  IP: {result.ip_address}")
            print(f"  City: {result.city}")
            print(f"  Country: {result.country_name}")
            print(f"  Location: {result.latitude}, {result.longitude}")
    else:
        print("❌ Database update failed")

    # Clean up
    provider.close()


def example_ip2location_update():
    """Update IP2Location database."""
    print("\n" + "=" * 60)
    print("IP2Location Database Update Example")
    print("=" * 60)

    # Check for token
    token = os.getenv("IP2LOCATION_TOKEN")
    if not token:
        print("\n⚠️  IP2LOCATION_TOKEN not set")
        print("Set it in .env file or environment:")
        print("  export IP2LOCATION_TOKEN='your_token'")
        print("\nGet a free token at: https://lite.ip2location.com/sign-up")
        return

    # Create provider config with auto_update enabled
    config = ProviderConfig(
        name="ip2location",
        database_path="./data/databases/IP2LOCATION-LITE-DB11.BIN",
        enabled=True,
        auto_update=True,
        license_key=token,  # IP2Location uses token as license_key
    )

    # Create provider
    provider = IP2LocationProvider(config)

    print("\n📦 Configuration:")
    print(f"  Database: {config.database_path}")
    print(f"  Auto-update: {config.auto_update}")
    print(f"  Token: {'*' * 20}")

    # Check if database exists
    db_exists = Path(config.database_path).exists()
    print(f"\n📁 Database exists: {db_exists}")

    # Update database
    print("\n🔄 Updating database...")
    success = provider.update()

    if success:
        print("✅ Database updated successfully!")

        # Test lookup
        print("\n🔍 Testing database with lookup:")
        result = provider.lookup("8.8.8.8")
        if result:
            print(f"  IP: {result.ip_address}")
            print(f"  City: {result.city}")
            print(f"  Country: {result.country_name}")
            print(f"  Location: {result.latitude}, {result.longitude}")
    else:
        print("❌ Database update failed")

    # Clean up
    provider.close()


def example_config_based_update():
    """Update databases using configuration file."""
    print("\n" + "=" * 60)
    print("Config-Based Update Example")
    print("=" * 60)

    # Load config from file (assumes config.yaml exists)
    config_path = Path("./config/config.yaml")
    if not config_path.exists():
        print(f"\n⚠️  Config file not found: {config_path}")
        print("Create config.yaml with auto_update settings")
        return

    config = AppConfig.from_yaml(str(config_path))

    print(f"\n📦 Loaded configuration from: {config_path}")
    print(f"  Providers: {len(config.providers)}")

    # Update all providers with auto_update enabled
    for provider_config in config.providers:
        if not provider_config.auto_update:
            print(f"\n⏭️  Skipping {provider_config.name} (auto_update disabled)")
            continue

        print(f"\n🔄 Updating {provider_config.name}...")

        # Create provider based on name
        if provider_config.name == "geoip2":
            provider = GeoIP2Provider(provider_config)
        elif provider_config.name == "ip2location":
            provider = IP2LocationProvider(provider_config)
        else:
            print(f"  ⚠️  Unknown provider: {provider_config.name}")
            continue

        # Update
        success = provider.update()
        if success:
            print(f"  ✅ {provider_config.name} updated successfully")
        else:
            print(f"  ❌ {provider_config.name} update failed")

        provider.close()


def example_direct_updater():
    """Use updater classes directly for batch updates."""
    print("\n" + "=" * 60)
    print("Direct Updater Example")
    print("=" * 60)

    from geoip_geocode.updater import IP2LocationUpdater, MaxMindUpdater

    # MaxMind update
    license_key = os.getenv("MAXMIND_LICENSE_KEY")
    if license_key:
        print("\n🔄 Updating MaxMind databases...")
        updater = MaxMindUpdater(license_key=license_key, output_dir="./data/databases")

        # Update all common editions
        results = updater.update_all()

        for edition, path in results.items():
            if path:
                print(f"  ✅ {edition}: {path}")
            else:
                print(f"  ❌ {edition}: Failed")
    else:
        print("\n⏭️  Skipping MaxMind (no license key)")

    # IP2Location update
    token = os.getenv("IP2LOCATION_TOKEN")
    if token:
        print("\n🔄 Updating IP2Location database...")
        updater = IP2LocationUpdater(token=token, output_dir="./data/databases")

        # Update default database
        path = updater.download_database()
        if path:
            print(f"  ✅ Database updated: {path}")
        else:
            print("  ❌ Update failed")
    else:
        print("\n⏭️  Skipping IP2Location (no token)")


if __name__ == "__main__":
    print("\n🌍 GeoIP Database Auto-Update Examples\n")

    # Example 1: Update MaxMind database
    example_maxmind_update()

    # Example 2: Update IP2Location database
    example_ip2location_update()

    # Example 3: Update using config file
    # example_config_based_update()

    # Example 4: Direct updater usage
    example_direct_updater()

    print("\n" + "=" * 60)
    print("✨ All examples completed!")
    print("=" * 60)
