#!/usr/bin/env python3
"""
Examples for multi-database GeoIP lookups with caching.

This script demonstrates how to use the MultiDatabaseGeoIP2Provider
to perform enriched IP lookups using City + ASN databases with caching.
"""

from pathlib import Path
from geoip_geocode.models import ProviderConfig, CacheConfig
from geoip_geocode.providers import MultiDatabaseGeoIP2Provider

def example_basic_enriched_lookup():
    """Example 1: Basic enriched lookup with City + ASN databases."""
    print("\n" + "="*60)
    print("Example 1: Basic Enriched Lookup (City + ASN)")
    print("="*60)
    
    # Configure provider with both City and ASN databases
    config = ProviderConfig(
        name="geoip2-enriched",
        enabled=True,
        city_database_path="./GeoLite2-City.mmdb",
        asn_database_path="./GeoLite2-ASN.mmdb"
    )
    
    try:
        provider = MultiDatabaseGeoIP2Provider(config)
        
        # Look up an IP address
        ip = "8.8.8.8"
        result = provider.lookup(ip)
        
        if result:
            print(f"\nEnriched lookup results for {ip}:")
            print(f"  City: {result.city}")
            print(f"  Country: {result.country_name} ({result.country_code})")
            print(f"  Coordinates: {result.latitude}, {result.longitude}")
            print(f"  Time Zone: {result.time_zone}")
            print(f"\n  ASN: {result.asn}")
            print(f"  Organization: {result.asn_organization}")
            print(f"  Network: {result.network}")
        else:
            print(f"No data found for {ip}")
            
    except FileNotFoundError as e:
        print(f"Error: {e}")
        print("Please download both GeoLite2-City.mmdb and GeoLite2-ASN.mmdb")

def example_with_caching():
    """Example 2: Using cache to improve performance."""
    print("\n" + "="*60)
    print("Example 2: Enriched Lookup with LRU Caching")
    print("="*60)
    
    # Configure provider
    provider_config = ProviderConfig(
        name="geoip2-enriched",
        city_database_path="./GeoLite2-City.mmdb",
        asn_database_path="./GeoLite2-ASN.mmdb"
    )
    
    # Configure cache (10,000 entries, 1 hour TTL)
    cache_config = CacheConfig(
        enabled=True,
        backend="lru",
        max_size=10000,
        ttl=3600
    )
    
    try:
        provider = MultiDatabaseGeoIP2Provider(provider_config, cache_config)
        
        # Test IPs
        test_ips = ["8.8.8.8", "1.1.1.1", "8.8.8.8", "208.67.222.222", "8.8.8.8"]
        
        print("\nPerforming multiple lookups (notice cache hits):")
        for ip in test_ips:
            result = provider.lookup(ip)
            if result:
                print(f"  {ip}: {result.city}, {result.country_name} (ASN: {result.asn})")
        
        # Show cache statistics
        stats = provider.get_cache_stats()
        print(f"\nCache Statistics:")
        print(f"  Hits: {stats.hits}")
        print(f"  Misses: {stats.misses}")
        print(f"  Hit Rate: {stats.hit_rate:.2f}%")
        print(f"  Cache Size: {stats.size}/{stats.max_size}")
        
    except FileNotFoundError as e:
        print(f"Error: {e}")

def example_city_only():
    """Example 3: Using only City database (ASN optional)."""
    print("\n" + "="*60)
    print("Example 3: City Database Only (Graceful Degradation)")
    print("="*60)
    
    # Configure with only City database
    config = ProviderConfig(
        name="geoip2-city-only",
        city_database_path="./GeoLite2-City.mmdb"
        # No ASN database - will still work
    )
    
    cache_config = CacheConfig(enabled=True, max_size=5000, ttl=1800)
    
    try:
        provider = MultiDatabaseGeoIP2Provider(config, cache_config)
        
        ips = ["8.8.8.8", "1.1.1.1", "208.67.222.222"]
        
        print("\nLookups without ASN database:")
        for ip in ips:
            result = provider.lookup(ip)
            if result:
                print(f"  {ip}:")
                print(f"    Location: {result.city}, {result.country_name}")
                print(f"    ASN: {result.asn or 'N/A'}")
                print(f"    Organization: {result.asn_organization or 'N/A'}")
        
    except FileNotFoundError as e:
        print(f"Error: {e}")

def example_cache_management():
    """Example 4: Cache management operations."""
    print("\n" + "="*60)
    print("Example 4: Cache Management")
    print("="*60)
    
    provider_config = ProviderConfig(
        name="geoip2-enriched",
        city_database_path="./GeoLite2-City.mmdb",
        asn_database_path="./GeoLite2-ASN.mmdb"
    )
    
    cache_config = CacheConfig(
        enabled=True,
        max_size=100,  # Small cache for demonstration
        ttl=3600
    )
    
    try:
        provider = MultiDatabaseGeoIP2Provider(provider_config, cache_config)
        
        # Populate cache
        print("\nPopulating cache with multiple IPs:")
        ips = ["8.8.8.8", "1.1.1.1", "208.67.222.222", "9.9.9.9"]
        for ip in ips:
            result = provider.lookup(ip)
            if result:
                print(f"  Cached: {ip}")
        
        # Check stats
        stats = provider.get_cache_stats()
        print(f"\nCache after population:")
        print(f"  Size: {stats.size}")
        print(f"  Hits: {stats.hits}, Misses: {stats.misses}")
        
        # Do more lookups to see cache hits
        print("\nRepeating lookups (should be cached):")
        for ip in ips[:2]:
            result = provider.lookup(ip)
            if result:
                print(f"  {ip}: {result.city}")
        
        stats = provider.get_cache_stats()
        print(f"\nCache after repeats:")
        print(f"  Size: {stats.size}")
        print(f"  Hits: {stats.hits}, Misses: {stats.misses}")
        print(f"  Hit Rate: {stats.hit_rate:.2f}%")
        
        # Clear cache
        print("\nClearing cache...")
        provider.clear_cache()
        stats = provider.get_cache_stats()
        print(f"  Cache size after clear: {stats.size}")
        print(f"  Stats reset: Hits={stats.hits}, Misses={stats.misses}")
        
    except FileNotFoundError as e:
        print(f"Error: {e}")

def example_performance_comparison():
    """Example 5: Performance comparison with/without cache."""
    print("\n" + "="*60)
    print("Example 5: Performance Comparison")
    print("="*60)
    
    import time
    
    provider_config = ProviderConfig(
        name="geoip2-enriched",
        city_database_path="./GeoLite2-City.mmdb",
        asn_database_path="./GeoLite2-ASN.mmdb"
    )
    
    try:
        # Without cache
        print("\nWithout cache:")
        provider_no_cache = MultiDatabaseGeoIP2Provider(
            provider_config,
            CacheConfig(enabled=False)
        )
        
        test_ip = "8.8.8.8"
        iterations = 100
        
        start = time.time()
        for _ in range(iterations):
            provider_no_cache.lookup(test_ip)
        elapsed_no_cache = time.time() - start
        
        print(f"  {iterations} lookups took: {elapsed_no_cache:.3f}s")
        print(f"  Average: {elapsed_no_cache/iterations*1000:.2f}ms per lookup")
        
        # With cache
        print("\nWith cache:")
        provider_with_cache = MultiDatabaseGeoIP2Provider(
            provider_config,
            CacheConfig(enabled=True, max_size=1000, ttl=3600)
        )
        
        start = time.time()
        for _ in range(iterations):
            provider_with_cache.lookup(test_ip)
        elapsed_with_cache = time.time() - start
        
        print(f"  {iterations} lookups took: {elapsed_with_cache:.3f}s")
        print(f"  Average: {elapsed_with_cache/iterations*1000:.2f}ms per lookup")
        
        stats = provider_with_cache.get_cache_stats()
        print(f"\nCache performance:")
        print(f"  Hit rate: {stats.hit_rate:.2f}%")
        print(f"  Speedup: {elapsed_no_cache/elapsed_with_cache:.1f}x faster")
        
    except FileNotFoundError as e:
        print(f"Error: {e}")

def example_backward_compatibility():
    """Example 6: Backward compatibility with database_path."""
    print("\n" + "="*60)
    print("Example 6: Backward Compatibility")
    print("="*60)
    
    # Using old 'database_path' parameter (backward compatible)
    config = ProviderConfig(
        name="geoip2-compat",
        database_path="./GeoLite2-City.mmdb"  # Old parameter name
    )
    
    try:
        provider = MultiDatabaseGeoIP2Provider(config)
        
        result = provider.lookup("8.8.8.8")
        if result:
            print(f"\nBackward compatible configuration works!")
            print(f"  City: {result.city}")
            print(f"  Country: {result.country_name}")
            print(f"  Note: ASN fields will be None without ASN database")
        
    except FileNotFoundError as e:
        print(f"Error: {e}")

def example_bulk_enrichment():
    """Example 7: Bulk IP enrichment with caching."""
    print("\n" + "="*60)
    print("Example 7: Bulk IP Enrichment")
    print("="*60)
    
    provider_config = ProviderConfig(
        name="geoip2-bulk",
        city_database_path="./GeoLite2-City.mmdb",
        asn_database_path="./GeoLite2-ASN.mmdb"
    )
    
    cache_config = CacheConfig(enabled=True, max_size=10000, ttl=3600)
    
    try:
        provider = MultiDatabaseGeoIP2Provider(provider_config, cache_config)
        
        # Simulate bulk processing
        ip_list = [
            "8.8.8.8", "1.1.1.1", "208.67.222.222",
            "9.9.9.9", "8.8.4.4", "1.0.0.1"
        ]
        
        print("\nEnriching IP list:")
        enriched_results = []
        
        for ip in ip_list:
            result = provider.lookup(ip)
            if result:
                enriched_results.append(result)
                print(f"  ✓ {ip}: {result.city}, {result.country_code} (ASN: {result.asn})")
            else:
                print(f"  ✗ {ip}: Not found")
        
        # Show summary
        stats = provider.get_cache_stats()
        print(f"\nBulk enrichment summary:")
        print(f"  Total IPs processed: {len(ip_list)}")
        print(f"  Successful: {len(enriched_results)}")
        print(f"  Cache hits: {stats.hits}")
        print(f"  Cache misses: {stats.misses}")
        
        # Export to JSON
        print("\nSample JSON export (first result):")
        if enriched_results:
            import json
            print(json.dumps(enriched_results[0].model_dump(), indent=2))
        
    except FileNotFoundError as e:
        print(f"Error: {e}")

def main():
    """Run all examples."""
    print("\n" + "="*60)
    print("MULTI-DATABASE GEOIP WITH CACHING - EXAMPLES")
    print("="*60)
    print("\nThese examples demonstrate enriched IP lookups using:")
    print("  - City database for location information")
    print("  - ASN database for network/ISP information")
    print("  - LRU caching for improved performance")
    print("\nNote: Examples require GeoLite2-City.mmdb and GeoLite2-ASN.mmdb")
    
    # Run examples
    example_basic_enriched_lookup()
    example_with_caching()
    example_city_only()
    example_cache_management()
    example_performance_comparison()
    example_backward_compatibility()
    example_bulk_enrichment()
    
    print("\n" + "="*60)
    print("EXAMPLES COMPLETE")
    print("="*60)
    print("\nKey takeaways:")
    print("  1. Multi-database support enriches data with ASN info")
    print("  2. LRU caching dramatically improves performance")
    print("  3. Graceful degradation when ASN database is missing")
    print("  4. Cache statistics help monitor performance")
    print("  5. Backward compatible with existing configurations")
    print()

if __name__ == "__main__":
    main()
