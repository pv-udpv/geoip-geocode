#!/usr/bin/env python3
"""
Example: Using the IP2Location provider for IP geolocation.

This example demonstrates how to use the IP2Location provider
to perform IP geolocation lookups.
"""

from geoip_geocode.models import ProviderConfig
from geoip_geocode.providers import IP2LocationProvider


def ip2location_example():
    """Example of using IP2Location provider."""
    print("=== IP2Location Provider Example ===\n")

    # Note: You need to download an IP2Location database file
    # from https://www.ip2location.com/developers/python
    # This example assumes you have the database file

    try:
        # Configure the IP2Location provider
        config = ProviderConfig(
            name="ip2location",
            enabled=True,
            database_path="./data/databases/IP2LOCATION-LITE-DB11.BIN",  # Update this path
        )

        # Create provider instance
        provider = IP2LocationProvider(config)

        if not provider.is_available():
            print("❌ IP2Location provider is not available.")
            print("   Make sure you have:")
            print("   1. Installed IP2Location library: pip install IP2Location")
            print("   2. Downloaded a database file from ip2location.com")
            print("   3. Updated the database_path in the configuration")
            return

        # Test IP addresses
        test_ips = [
            "8.8.8.8",  # Google DNS
            "1.1.1.1",  # Cloudflare DNS
            "208.67.222.222",  # OpenDNS
            "134.195.196.26",  # Sample IP
        ]

        print("Performing IP lookups...\n")

        for ip in test_ips:
            print(f"Looking up: {ip}")
            try:
                result = provider.lookup(ip)

                if result:
                    print(f"  ✓ Found location data:")
                    print(f"    Country: {result.country_name} ({result.country_code})")
                    print(f"    City: {result.city or 'Unknown'}")
                    print(f"    Region: {result.subdivision or 'Unknown'}")
                    print(f"    Coordinates: {result.latitude}, {result.longitude}")
                    print(f"    Timezone: {result.time_zone or 'Unknown'}")
                    print(f"    Continent: {result.continent_name or 'Unknown'}")
                    print(f"    Postal Code: {result.postal_code or 'Unknown'}")
                    print(f"    Provider: {result.provider}")
                    print(f"    Geoname ID: {result.geoname_id}")
                else:
                    print(f"  ❌ No location data found for {ip}")

            except Exception as e:
                print(f"  ❌ Error looking up {ip}: {e}")

            print()

        # Demonstrate context manager usage
        print("=== Using as Context Manager ===")
        with IP2LocationProvider(config) as provider:
            result = provider.lookup("8.8.8.8")
            if result:
                print(
                    f"✓ Context manager lookup successful: {result.city}, {result.country_name}"
                )
        # Provider is automatically closed here

    except ImportError:
        print("❌ IP2Location library not installed.")
        print("   Install it with: pip install IP2Location")
    except FileNotFoundError:
        print("❌ Database file not found.")
        print(
            "   Download a database file from https://www.ip2location.com/developers/python"
        )
        print("   and update the database_path in the configuration.")
    except Exception as e:
        print(f"❌ Error: {e}")


def compare_providers_example():
    """Example comparing multiple providers."""
    print("\n=== Comparing Providers ===\n")

    # This example assumes you have both GeoIP2 and IP2Location databases
    providers = []

    # Try to create GeoIP2 provider
    try:
        from geoip_geocode.providers import GeoIP2Provider

        geoip2_config = ProviderConfig(
            name="geoip2",
            enabled=True,
            database_path="./data/databases/GeoLite2-City.mmdb",
        )
        geoip2_provider = GeoIP2Provider(geoip2_config)
        if geoip2_provider.is_available():
            providers.append(("GeoIP2", geoip2_provider))
    except Exception as e:
        print(f"GeoIP2 provider not available: {e}")

    # Try to create IP2Location provider
    try:
        ip2loc_config = ProviderConfig(
            name="ip2location",
            enabled=True,
            database_path="./data/databases/IP2LOCATION-LITE-DB11.BIN",
        )
        ip2loc_provider = IP2LocationProvider(ip2loc_config)
        if ip2loc_provider.is_available():
            providers.append(("IP2Location", ip2loc_provider))
    except Exception as e:
        print(f"IP2Location provider not available: {e}")

    if not providers:
        print("❌ No providers available for comparison.")
        return

    test_ip = "8.8.8.8"
    print(f"Comparing results for IP: {test_ip}\n")

    for provider_name, provider in providers:
        print(f"--- {provider_name} ---")
        try:
            result = provider.lookup(test_ip)
            if result:
                print(f"Country: {result.country_name}")
                print(f"City: {result.city}")
                print(f"Coordinates: {result.latitude}, {result.longitude}")
                print(f"Geoname ID: {result.geoname_id}")
            else:
                print("No result found")
        except Exception as e:
            print(f"Error: {e}")
        print()


if __name__ == "__main__":
    ip2location_example()
    compare_providers_example()
