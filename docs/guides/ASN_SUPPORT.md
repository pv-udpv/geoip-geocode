# ASN Support in geoip-geocode

This guide explains how to use ASN (Autonomous System Number) databases with geoip-geocode.

## Overview

ASN data provides information about the network infrastructure:
- **ASN Number**: Unique identifier for an autonomous system
- **Organization**: The organization managing the network
- **Network Range**: IP address range of the network

## Supported Providers

### 1. MultiDatabaseGeoIP2Provider (Recommended)

The `MultiDatabaseGeoIP2Provider` supports both City and ASN databases from MaxMind.

#### Features:
- ✅ City geolocation data (lat/lon, city, country)
- ✅ ASN network information
- ✅ Built-in caching support
- ✅ Locale support
- ✅ Returns `EnrichedGeoData` with ASN fields

#### Setup:

```python
from geoip_geocode.models import ProviderConfig, CacheConfig
from geoip_geocode.providers import MultiDatabaseGeoIP2Provider

# Configuration with City + ASN databases
config = ProviderConfig(
    name="geoip2-multi",
    enabled=True,
    city_database_path="./GeoLite2-City.mmdb",
    asn_database_path="./GeoLite2-ASN.mmdb"
)

# Optional: Enable caching
cache_config = CacheConfig(
    enabled=True,
    max_size=10000,
    ttl=3600
)

provider = MultiDatabaseGeoIP2Provider(config, cache_config)
```

#### Usage:

```python
# Perform enriched lookup
result = provider.lookup("8.8.8.8")

if result:
    # City data
    print(f"City: {result.city}")
    print(f"Country: {result.country_name}")
    print(f"Coordinates: {result.latitude}, {result.longitude}")
    
    # ASN data
    print(f"ASN: {result.asn}")
    print(f"Organization: {result.asn_organization}")
    print(f"Network: {result.network}")
```

#### CLI Usage:

```bash
# List providers (geoip2-multi will be shown)
uv run geoip-geocode list-providers

# Use with config file
uv run geoip-geocode lookup 8.8.8.8 --provider geoip2-multi --config config.yaml
```

### 2. IP2Location Provider

IP2Location databases include ASN data in their DB files (DB11 and higher).

#### Features:
- ✅ City geolocation data
- ⚠️ ASN data available only in DB11+ versions
- ✅ Single database file
- ✅ No separate ASN database needed

#### Setup:

```python
from geoip_geocode.models import ProviderConfig
from geoip_geocode.providers import IP2LocationProvider

config = ProviderConfig(
    name="ip2location",
    enabled=True,
    database_path="./IP2LOCATION-LITE-DB11.BIN"  # DB11 includes ASN
)

provider = IP2LocationProvider(config)
```

**Note**: IP2Location's free LITE databases (DB1-DB11) include varying levels of data. For ASN information, you need at least DB11.

## Database Downloads

### MaxMind GeoLite2

1. Sign up at [MaxMind](https://www.maxmind.com/en/geolite2/signup)
2. Get your license key
3. Download both databases:
   - **GeoLite2-City.mmdb** - For location data
   - **GeoLite2-ASN.mmdb** - For ASN data

### IP2Location

Download from [IP2Location](https://www.ip2location.com/database/ip2location):
- **IP2LOCATION-LITE-DB11.BIN** - Includes ASN data (free)
- Higher DB versions for more detailed information

## Configuration File Example

### config.yaml with ASN Support

```yaml
default_provider: geoip2-multi
cache_enabled: true
cache_ttl: 3600

providers:
  # GeoIP2 with ASN support
  - name: geoip2-multi
    enabled: true
    priority: 100
    city_database_path: ./data/databases/GeoLite2-City.mmdb
    asn_database_path: ./data/databases/GeoLite2-ASN.mmdb
    timeout: 30
    max_retries: 3

  # IP2Location with built-in ASN
  - name: ip2location
    enabled: true
    priority: 50
    database_path: ./data/databases/IP2LOCATION-LITE-DB11.BIN
```

## Complete Example

```python
from geoip_geocode.registry import get_registry
from geoip_geocode.providers import MultiDatabaseGeoIP2Provider
from geoip_geocode.models import ProviderConfig, CacheConfig

# Initialize registry
registry = get_registry()
registry.register("geoip2-multi", MultiDatabaseGeoIP2Provider)

# Configure provider with ASN support
config = ProviderConfig(
    name="geoip2-multi",
    enabled=True,
    city_database_path="./GeoLite2-City.mmdb",
    asn_database_path="./GeoLite2-ASN.mmdb"
)

cache_config = CacheConfig(enabled=True, max_size=10000, ttl=3600)

# Get provider
provider = registry.get_provider("geoip2-multi", config, cache_config)

# Lookup with ASN data
ip_addresses = ["8.8.8.8", "1.1.1.1", "208.67.222.222"]

for ip in ip_addresses:
    result = provider.lookup(ip)
    if result:
        print(f"\n{'='*50}")
        print(f"IP: {ip}")
        print(f"Location: {result.city}, {result.country_name}")
        print(f"ASN: AS{result.asn}")
        print(f"Organization: {result.asn_organization}")
        print(f"Network: {result.network}")
        print(f"{'='*50}")

# Cache statistics
stats = provider.get_cache_stats()
print(f"\nCache Stats:")
print(f"  Hits: {stats.hits}")
print(f"  Misses: {stats.misses}")
print(f"  Hit Rate: {stats.hit_rate:.2f}%")
print(f"  Size: {stats.size}/{stats.max_size}")
```

## Data Model: EnrichedGeoData

When using `MultiDatabaseGeoIP2Provider`, results are returned as `EnrichedGeoData`:

```python
from geoip_geocode.models import EnrichedGeoData

# EnrichedGeoData extends GeoData with ASN fields:
enriched_data = EnrichedGeoData(
    geoname_id=5375480,
    ip_address="8.8.8.8",
    country_code="US",
    country_name="United States",
    city="Mountain View",
    latitude=37.386,
    longitude=-122.0838,
    # ASN fields:
    asn=15169,                           # AS number
    asn_organization="GOOGLE",           # Organization name
    network="8.8.8.0/24",               # Network range
    provider="geoip2-multi"
)
```

## Use Cases

### 1. Network Analysis
```python
# Identify which networks are accessing your service
result = provider.lookup(client_ip)
print(f"Request from AS{result.asn} ({result.asn_organization})")
```

### 2. Traffic Routing
```python
# Route traffic based on ASN
if result.asn == 15169:  # Google
    # Special handling for Google traffic
    pass
```

### 3. Security
```python
# Block or flag suspicious ASNs
BLOCKED_ASNS = [12345, 67890]
if result.asn in BLOCKED_ASNS:
    print(f"Blocked: AS{result.asn}")
```

### 4. Analytics
```python
# Track geographic and network distribution
analytics = {
    'country': result.country_code,
    'asn': result.asn,
    'org': result.asn_organization
}
```

## Best Practices

1. **Use Caching**: Enable caching for better performance
2. **Keep Databases Updated**: Download new versions monthly
3. **Handle Missing Data**: Not all IPs have ASN information
4. **Error Handling**: Always check if result is not None
5. **Choose Right Provider**: Use `MultiDatabaseGeoIP2Provider` for most accurate ASN data

## Troubleshooting

### ASN Data Not Available
- Ensure you're using `MultiDatabaseGeoIP2Provider` (not basic `GeoIP2Provider`)
- Check that `asn_database_path` is configured
- Verify the ASN database file exists
- Private/local IPs typically don't have ASN data

### Performance Issues
- Enable caching: `CacheConfig(enabled=True, max_size=10000)`
- Check cache hit rate: `provider.get_cache_stats()`
- Clear cache if needed: `provider.clear_cache()`

### Database Errors
- Verify database files are not corrupted
- Ensure you have read permissions
- Check database file paths are correct

## References

- [MaxMind GeoLite2 ASN](https://dev.maxmind.com/geoip/geolite2-free-geolocation-data)
- [IP2Location Database Comparison](https://www.ip2location.com/database/db11-ip-country-region-city-latitude-longitude-zipcode-timezone-isp-domain-netspeed-areacode-weather-mobile-elevation-usagetype)
- [ASN Information](https://www.iana.org/assignments/as-numbers/as-numbers.xhtml)
