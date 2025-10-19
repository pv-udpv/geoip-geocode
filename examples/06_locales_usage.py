#!/usr/bin/env python3
"""
Example: Using locales for localized geographic data.

This example demonstrates how to configure and use locales
to get country and city names in different languages.
"""

from geoip_geocode.models import ProviderConfig, CacheConfig
from geoip_geocode.providers import GeoIP2Provider, MultiDatabaseGeoIP2Provider


def basic_locale_example():
    """Example of using locales with basic GeoIP2 provider."""
    print("=== Basic Locale Example ===\n")

    # Configure provider with Russian locale
    config_ru = ProviderConfig(
        name="geoip2-ru",
        enabled=True,
        locales=["ru", "en"],  # Russian preferred, English fallback
        database_path="./data/databases/GeoLite2-City.mmdb",
    )

    # Configure provider with English locale
    config_en = ProviderConfig(
        name="geoip2-en",
        enabled=True,
        locales=["en"],  # English only
        database_path="./data/databases/GeoLite2-City.mmdb",
    )

    test_ip = "8.8.8.8"

    try:
        # Lookup with Russian locale
        print("Russian locale (ru, en):")
        with GeoIP2Provider(config_ru) as provider_ru:
            result_ru = provider_ru.lookup(test_ip)
            if result_ru:
                print(f"  Country: {result_ru.country_name}")
                print(f"  City: {result_ru.city}")
                print(f"  Subdivision: {result_ru.subdivision}")

        print()

        # Lookup with English locale
        print("English locale (en):")
        with GeoIP2Provider(config_en) as provider_en:
            result_en = provider_en.lookup(test_ip)
            if result_en:
                print(f"  Country: {result_en.country_name}")
                print(f"  City: {result_en.city}")
                print(f"  Subdivision: {result_en.subdivision}")

    except FileNotFoundError:
        print("❌ Database file not found.")
        print("   Download GeoLite2-City.mmdb and place it in ./data/databases/")
    except Exception as e:
        print(f"❌ Error: {e}")


def enriched_locale_example():
    """Example of using locales with multi-database provider."""
    print("\n=== Enriched Data with Locales ===\n")

    # Configure multi-database provider with multiple locales
    config = ProviderConfig(
        name="geoip2-enriched",
        enabled=True,
        locales=["ru", "en", "de"],  # Russian, English, German
        city_database_path="./data/databases/GeoLite2-City.mmdb",
        asn_database_path="./data/databases/GeoLite2-ASN.mmdb",
    )

    cache_config = CacheConfig(enabled=True, backend="lru", max_size=10000, ttl=3600)

    test_ips = [
        ("8.8.8.8", "Google DNS"),
        ("77.88.8.8", "Yandex DNS"),
        ("1.1.1.1", "Cloudflare DNS"),
    ]

    try:
        with MultiDatabaseGeoIP2Provider(config, cache_config) as provider:
            for ip, description in test_ips:
                print(f"{description} ({ip}):")
                result = provider.lookup(ip)

                if result:
                    print(f"  Country: {result.country_name} ({result.country_code})")
                    print(f"  City: {result.city or 'Unknown'}")
                    print(f"  Subdivision: {result.subdivision or 'Unknown'}")
                    if result.asn:
                        print(f"  ASN: {result.asn}")
                        print(f"  ISP: {result.asn_organization}")
                else:
                    print(f"  ❌ No data found")
                print()

            # Show cache statistics
            stats = provider.get_cache_stats()
            total = stats.hits + stats.misses
            if total > 0:
                print(
                    f"Cache stats: {stats.hits} hits, {stats.misses} misses, "
                    f"{stats.hit_rate:.1%} hit rate"
                )

    except FileNotFoundError as e:
        print(f"❌ Database file not found: {e}")
        print("   Download GeoLite2 databases and place them in ./data/databases/")
    except Exception as e:
        print(f"❌ Error: {e}")


def compare_locales_example():
    """Compare results from different locales."""
    print("\n=== Comparing Different Locales ===\n")

    locales_to_test = [
        (["en"], "English"),
        (["ru", "en"], "Russian with English fallback"),
        (["de", "en"], "German with English fallback"),
        (["fr", "en"], "French with English fallback"),
    ]

    test_ip = "77.88.8.8"  # Russian IP for better demonstration

    try:
        for locales, description in locales_to_test:
            config = ProviderConfig(
                name=f"geoip2-{locales[0]}",
                enabled=True,
                locales=locales,
                database_path="./data/databases/GeoLite2-City.mmdb",
            )

            print(f"{description} ({locales}):")
            with GeoIP2Provider(config) as provider:
                result = provider.lookup(test_ip)
                if result:
                    print(f"  Country: {result.country_name}")
                    print(f"  City: {result.city or 'Unknown'}")
                else:
                    print(f"  ❌ No data found")
            print()

    except FileNotFoundError:
        print("❌ Database file not found.")
        print("   Download GeoLite2-City.mmdb and place it in ./data/databases/")
    except Exception as e:
        print(f"❌ Error: {e}")


def config_file_locale_example():
    """Example of loading locales from configuration file."""
    print("\n=== Loading Locales from Config File ===\n")

    from geoip_geocode.config import load_config

    try:
        # Load config from YAML (if exists)
        config = load_config(yaml_path="config.yaml")

        print(f"Global locales: {config.locales}")
        print(f"Providers configured: {len(config.providers)}")

        for provider_config in config.providers:
            print(f"\nProvider: {provider_config.name}")
            print(f"  Locales: {provider_config.locales}")
            print(f"  Priority: {provider_config.priority}")

    except FileNotFoundError:
        print("❌ config.yaml not found")
        print("   Copy config/config.yaml.example to config.yaml")
        print("\nExample configuration:")
        print(
            """
# config.yaml
locales:
  - ru  # Russian preferred
  - en  # English fallback

providers:
  - name: geoip2
    enabled: true
    locales:
      - ru
      - en
    database_path: ./data/databases/GeoLite2-City.mmdb
        """
        )
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    basic_locale_example()
    enriched_locale_example()
    compare_locales_example()
    config_file_locale_example()

    print("\n=== Summary ===")
    print(
        "✓ Locales allow you to get country and city names in your preferred language"
    )
    print("✓ Specify multiple locales for fallback (e.g., ['ru', 'en'])")
    print("✓ Locales can be configured globally and per-provider")
    print("✓ Supported locales depend on your GeoIP2 database")
    print("\nCommon locales: en, ru, de, fr, es, pt, ja, zh-CN")
