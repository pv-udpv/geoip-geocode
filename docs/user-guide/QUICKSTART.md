# Quick Reference Guide

## Installation

```bash
pip install geoip-geocode
```

## CLI Quick Reference

```bash
# Look up an IP address
geoip-geocode lookup 8.8.8.8

# With custom database path
geoip-geocode lookup 8.8.8.8 --database /path/to/GeoLite2-City.mmdb

# Using config file
geoip-geocode lookup 8.8.8.8 --config config.yaml

# Initialize configuration
geoip-geocode config-init

# List providers
geoip-geocode list-providers

# Show version
geoip-geocode version
```

## Python API Quick Reference

### Basic Lookup

```python
from geoip_geocode.providers import GeoIP2Provider
from geoip_geocode.models import ProviderConfig

config = ProviderConfig(
    name="geoip2",
    database_path="GeoLite2-City.mmdb"
)
provider = GeoIP2Provider(config)
result = provider.lookup("8.8.8.8")

print(f"City: {result.city}")
print(f"Country: {result.country_name}")
print(f"Coordinates: {result.latitude}, {result.longitude}")
```

### Using Registry

```python
from geoip_geocode.registry import get_registry
from geoip_geocode.providers import GeoIP2Provider

registry = get_registry()
registry.register("geoip2", GeoIP2Provider)

config = ProviderConfig(name="geoip2", database_path="db.mmdb")
provider = registry.get_provider("geoip2", config)
```

### Configuration

```python
from geoip_geocode.config import load_config

# From YAML
config = load_config(yaml_path="config.yaml")

# From .env
config = load_config()

# Get provider config
provider_config = config.get_provider_config("geoip2")
```

## Configuration Files

### YAML (config.yaml)

```yaml
default_provider: geoip2
cache_enabled: false
cache_ttl: 3600

providers:
  - name: geoip2
    enabled: true
    priority: 100
    database_path: ./GeoLite2-City.mmdb
```

### Environment (.env)

```env
GEOIP_DEFAULT_PROVIDER=geoip2
GEOIP_CACHE_ENABLED=false
GEOIP_CACHE_TTL=3600
```

## Data Models

### GeoData

```python
from geoip_geocode.models import GeoData

geo = GeoData(
    geoname_id=5375480,      # Required: primary key
    ip_address="8.8.8.8",
    country_code="US",
    country_name="United States",
    city="Mountain View",
    latitude=37.386,
    longitude=-122.0838,
    time_zone="America/Los_Angeles",
)
```

### ProviderConfig

```python
from geoip_geocode.models import ProviderConfig

config = ProviderConfig(
    name="geoip2",
    enabled=True,
    priority=100,
    database_path="./GeoLite2-City.mmdb",
    timeout=30,
)
```

## Common Tasks

### Multiple IP Lookups

```python
ips = ["8.8.8.8", "1.1.1.1", "208.67.222.222"]

for ip in ips:
    result = provider.lookup(ip)
    if result:
        print(f"{ip}: {result.city}, {result.country_name}")
```

### Error Handling

```python
try:
    provider = GeoIP2Provider(config)
    result = provider.lookup("8.8.8.8")
    
    if result:
        print(f"Found: {result.city}")
    else:
        print("IP not found in database")
        
except FileNotFoundError:
    print("Database file not found")
except Exception as e:
    print(f"Error: {e}")
```

### Custom Provider

```python
from geoip_geocode.registry import BaseProvider
from geoip_geocode.models import GeoData

class MyProvider(BaseProvider):
    def lookup(self, ip_address: str):
        # Your implementation
        return GeoData(
            geoname_id=12345,
            ip_address=ip_address,
            city="Custom City",
        )

# Register and use
registry = get_registry()
registry.register("myprovider", MyProvider)
```

## Database Setup

1. Sign up at https://www.maxmind.com/en/geolite2/signup
2. Download GeoLite2-City.mmdb
3. Place in project directory or specify path

## Development

```bash
# Install for development
pip install -e ".[dev]"

# Run tests
pytest

# Format code
black geoip_geocode tests

# Lint code
ruff check geoip_geocode tests

# Type check
mypy geoip_geocode
```

## Troubleshooting

**Database not found:**
```bash
geoip-geocode lookup 8.8.8.8 --database /path/to/GeoLite2-City.mmdb
```

**No data for IP:**
- Private IPs (192.168.x.x, 10.x.x.x) won't be in database
- Some IPs may not have location data

**Import errors:**
```bash
pip install -e ".[dev]"  # Reinstall with dependencies
```

## Resources

- Documentation: README.md
- Examples: examples.py
- Contributing: CONTRIBUTING.md
- Architecture: IMPLEMENTATION.md
- MaxMind: https://dev.maxmind.com/geoip/geolite2-free-geolocation-data
