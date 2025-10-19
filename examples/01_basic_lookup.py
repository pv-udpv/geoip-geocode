#!/usr/bin/env python3
"""
Example usage of geoip-geocode package.

This script demonstrates various ways to use the package for IP geolocation.
"""

from pathlib import Path
from geoip_geocode.models import ProviderConfig, GeoData
from geoip_geocode.providers import GeoIP2Provider
from geoip_geocode.registry import get_registry
from geoip_geocode.config import load_config, AppConfig


def example_basic_lookup():
    """Example 1: Basic IP lookup with GeoIP2."""
    print("\n" + "="*60)
    print("Example 1: Basic IP Lookup")
    print("="*60)
    
    # Configure the provider
    config = ProviderConfig(
        name="geoip2",
        enabled=True,
        database_path="./GeoLite2-City.mmdb"  # Update with your path
    )
    
    # Create provider instance
    try:
        provider = GeoIP2Provider(config)
        
        # Look up an IP address
        ip = "8.8.8.8"
        result = provider.lookup(ip)
        
        if result:
            print(f"\nLookup results for {ip}:")
            print(f"  GeoName ID: {result.geoname_id}")
            print(f"  City: {result.city}")
            print(f"  Country: {result.country_name} ({result.country_code})")
            print(f"  Coordinates: {result.latitude}, {result.longitude}")
            print(f"  Time Zone: {result.time_zone}")
        else:
            print(f"No data found for {ip}")
            
    except FileNotFoundError as e:
        print(f"Error: {e}")
        print("Please download GeoLite2-City.mmdb first")


def example_using_registry():
    """Example 2: Using the provider registry."""
    print("\n" + "="*60)
    print("Example 2: Using Provider Registry")
    print("="*60)
    
    # Get the global registry
    registry = get_registry()
    
    # Register the GeoIP2 provider
    registry.register("geoip2", GeoIP2Provider)
    
    # Create provider configuration
    config = ProviderConfig(
        name="geoip2",
        enabled=True,
        database_path="./GeoLite2-City.mmdb",
        priority=100
    )
    
    try:
        # Get provider from registry
        provider = registry.get_provider("geoip2", config)
        
        if provider and provider.is_available():
            # Look up multiple IPs
            ips = ["8.8.8.8", "1.1.1.1", "208.67.222.222"]
            
            print("\nLooking up multiple IPs:")
            for ip in ips:
                result = provider.lookup(ip)
                if result:
                    print(f"  {ip}: {result.city}, {result.country_name}")
                else:
                    print(f"  {ip}: No data found")
        else:
            print("Provider not available")
            
    except FileNotFoundError as e:
        print(f"Error: {e}")


def example_with_config_file():
    """Example 3: Using a configuration file."""
    print("\n" + "="*60)
    print("Example 3: Using Configuration File")
    print("="*60)
    
    # Create a sample configuration
    config = AppConfig(
        default_provider="geoip2",
        cache_enabled=False,
    )
    
    # Add provider configuration
    provider_config = ProviderConfig(
        name="geoip2",
        enabled=True,
        database_path="./GeoLite2-City.mmdb",
        priority=100
    )
    config.add_provider_config(provider_config)
    
    # Save configuration (optional)
    # config.to_yaml("example_config.yaml")
    
    print("\nConfiguration:")
    print(f"  Default Provider: {config.default_provider}")
    print(f"  Cache Enabled: {config.cache_enabled}")
    print(f"  Number of Providers: {len(config.providers)}")
    
    # Get provider config
    geoip2_config = config.get_provider_config("geoip2")
    if geoip2_config:
        print(f"\nGeoIP2 Provider Config:")
        print(f"  Name: {geoip2_config.name}")
        print(f"  Enabled: {geoip2_config.enabled}")
        print(f"  Priority: {geoip2_config.priority}")
        print(f"  Database: {geoip2_config.database_path}")


def example_custom_geodata():
    """Example 4: Working with GeoData objects."""
    print("\n" + "="*60)
    print("Example 4: Working with GeoData Objects")
    print("="*60)
    
    # Create a GeoData object manually
    geo_data = GeoData(
        geoname_id=5375480,
        ip_address="8.8.8.8",
        country_code="US",
        country_name="United States",
        city="Mountain View",
        postal_code="94035",
        latitude=37.386,
        longitude=-122.0838,
        time_zone="America/Los_Angeles",
        continent_code="NA",
        continent_name="North America",
        subdivision="California",
        subdivision_code="CA",
        accuracy_radius=100,
        provider="geoip2"
    )
    
    print(f"\nGeoData Object:")
    print(f"  Primary Key (GeoName ID): {geo_data.geoname_id}")
    print(f"  Full Address: {geo_data.city}, {geo_data.subdivision}, {geo_data.country_name}")
    print(f"  Postal Code: {geo_data.postal_code}")
    print(f"  Location: ({geo_data.latitude}, {geo_data.longitude})")
    print(f"  Accuracy: ±{geo_data.accuracy_radius} km")
    
    # Convert to dict
    geo_dict = geo_data.model_dump()
    print(f"\nAs Dictionary (first 5 items):")
    for key, value in list(geo_dict.items())[:5]:
        print(f"  {key}: {value}")
    
    # Convert to JSON
    geo_json = geo_data.model_dump_json(indent=2)
    print(f"\nAs JSON (truncated):")
    print(geo_json[:200] + "...")


def example_error_handling():
    """Example 5: Error handling."""
    print("\n" + "="*60)
    print("Example 5: Error Handling")
    print("="*60)
    
    config = ProviderConfig(
        name="geoip2",
        database_path="./GeoLite2-City.mmdb"
    )
    
    try:
        provider = GeoIP2Provider(config)
        
        # Try various IPs
        test_ips = [
            "8.8.8.8",           # Valid public IP
            "192.168.1.1",       # Private IP (won't be in database)
            "invalid-ip",        # Invalid IP format
        ]
        
        print("\nTesting various IP addresses:")
        for ip in test_ips:
            try:
                result = provider.lookup(ip)
                if result:
                    print(f"  ✓ {ip}: {result.city}, {result.country_name}")
                else:
                    print(f"  ✗ {ip}: Not found in database")
            except Exception as e:
                print(f"  ✗ {ip}: Error - {type(e).__name__}")
                
    except FileNotFoundError:
        print("\nDatabase file not found!")
        print("Please download GeoLite2-City.mmdb from:")
        print("https://dev.maxmind.com/geoip/geolite2-free-geolocation-data")
    except Exception as e:
        print(f"Unexpected error: {e}")


def main():
    """Run all examples."""
    print("\n" + "="*60)
    print("GEOIP-GEOCODE USAGE EXAMPLES")
    print("="*60)
    print("\nThese examples demonstrate the geoip-geocode package features.")
    print("Note: Some examples require GeoLite2-City.mmdb to be present.")
    
    # Run examples
    example_basic_lookup()
    example_using_registry()
    example_with_config_file()
    example_custom_geodata()
    example_error_handling()
    
    print("\n" + "="*60)
    print("EXAMPLES COMPLETE")
    print("="*60)
    print("\nFor more information, see README.md or run:")
    print("  geoip-geocode --help")
    print()


if __name__ == "__main__":
    main()
