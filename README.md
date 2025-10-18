# geoip-geocode

Geocoding and IP lookup tools with support for multiple providers.

## Features

- 🌍 **Multiple Provider Support**: Extensible provider registry system
- 🔌 **GeoIP2/MaxMind Integration**: Built-in support for MaxMind databases
- ⚙️ **Flexible Configuration**: Configure via Pydantic models, .env, or YAML files
- 🖥️ **CLI Interface**: Powerful command-line tool using Typer
- 📊 **Structured Data**: GeoData objects indexed by geoname_id
- 🧩 **Modular Design**: Easy to add new providers
- 📝 **Well Documented**: Comprehensive docstrings and examples

## Installation

```bash
pip install geoip-geocode
```

For development:

```bash
pip install -e ".[dev]"
```

## Quick Start

### Command Line Interface

Look up an IP address:

```bash
# Basic lookup (requires GeoLite2-City.mmdb in current directory)
geoip-geocode lookup 8.8.8.8

# Specify database path
geoip-geocode lookup 8.8.8.8 --database /path/to/GeoLite2-City.mmdb

# Use configuration file
geoip-geocode lookup 8.8.8.8 --config config.yaml
```

Initialize a configuration file:

```bash
geoip-geocode config-init --database /path/to/GeoLite2-City.mmdb
```

List available providers:

```bash
geoip-geocode list-providers
```

Download/update database (requires MaxMind license key):

```bash
geoip-geocode update-db --license-key YOUR_KEY
```

### Python API

```python
from geoip_geocode.models import ProviderConfig
from geoip_geocode.providers import GeoIP2Provider
from geoip_geocode.registry import get_registry

# Configure provider
config = ProviderConfig(
    name="geoip2",
    enabled=True,
    database_path="/path/to/GeoLite2-City.mmdb"
)

# Create provider
provider = GeoIP2Provider(config)

# Look up an IP address
result = provider.lookup("8.8.8.8")

if result:
    print(f"City: {result.city}")
    print(f"Country: {result.country_name}")
    print(f"Coordinates: {result.latitude}, {result.longitude}")
    print(f"GeoName ID: {result.geoname_id}")
```

### Using the Registry

```python
from geoip_geocode.registry import get_registry
from geoip_geocode.providers import GeoIP2Provider
from geoip_geocode.models import ProviderConfig

# Get global registry
registry = get_registry()

# Register providers
registry.register("geoip2", GeoIP2Provider)

# Create provider config
config = ProviderConfig(
    name="geoip2",
    database_path="/path/to/GeoLite2-City.mmdb",
    priority=100
)

# Get provider instance
provider = registry.get_provider("geoip2", config)

# Perform lookup
result = provider.lookup("8.8.8.8")
```

## Configuration

### YAML Configuration

Create a `config.yaml` file:

```yaml
default_provider: geoip2
cache_enabled: false
cache_ttl: 3600

providers:
  - name: geoip2
    enabled: true
    priority: 100
    database_path: ./GeoLite2-City.mmdb
    timeout: 30
    max_retries: 3
```

Load configuration:

```python
from geoip_geocode.config import load_config

config = load_config(yaml_path="config.yaml")
print(config.default_provider)
```

### Environment Variables

Create a `.env` file:

```env
GEOIP_DEFAULT_PROVIDER=geoip2
GEOIP_CACHE_ENABLED=false
GEOIP_CACHE_TTL=3600
MAXMIND_LICENSE_KEY=your_license_key_here
```

Configuration is automatically loaded from `.env` files.

## Data Model

All geographic data is returned as `GeoData` objects indexed by `geoname_id`:

```python
from geoip_geocode.models import GeoData

geo_data = GeoData(
    geoname_id=5375480,          # Primary key from GeoNames
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
```

## Adding Custom Providers

Create a new provider by inheriting from `BaseProvider`:

```python
from typing import Optional
from geoip_geocode.registry import BaseProvider
from geoip_geocode.models import GeoData, ProviderConfig

class MyProvider(BaseProvider):
    """Custom geocoding provider."""
    
    def __init__(self, config: ProviderConfig):
        super().__init__(config)
        # Initialize your provider here
    
    def lookup(self, ip_address: str) -> Optional[GeoData]:
        """Implement IP lookup logic."""
        # Your implementation here
        return GeoData(
            geoname_id=12345,
            ip_address=ip_address,
            # ... other fields
        )
    
    def is_available(self) -> bool:
        """Check if provider is ready."""
        return self.config.enabled

# Register your provider
from geoip_geocode.registry import get_registry

registry = get_registry()
registry.register("myprovider", MyProvider)
```

## GeoIP2 Database Setup

### Getting a Database

1. Sign up for a free account at [MaxMind](https://www.maxmind.com/en/geolite2/signup)
2. Get your license key
3. Download the GeoLite2-City database from the MaxMind website

### Database Locations

Common database locations:

- **Linux**: `/usr/share/GeoIP/GeoLite2-City.mmdb`
- **macOS**: `/usr/local/share/GeoIP/GeoLite2-City.mmdb`
- **Windows**: `C:\ProgramData\MaxMind\GeoLite2-City.mmdb`

Or place it anywhere and specify the path in your configuration.

## Development

### Running Tests

```bash
# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run tests with coverage
pytest --cov=geoip_geocode --cov-report=html
```

### Linting and Formatting

```bash
# Format code with black
black geoip_geocode tests

# Lint with ruff
ruff check geoip_geocode tests

# Type checking with mypy
mypy geoip_geocode
```

## Architecture

### Provider Registry System

The package uses a registry pattern to manage multiple providers:

1. **BaseProvider**: Abstract base class defining the provider interface
2. **ProviderRegistry**: Manages provider registration and instantiation
3. **Concrete Providers**: Implementations (e.g., GeoIP2Provider)

### Configuration Management

Configuration is handled through Pydantic models with support for:

- Environment variables (prefixed with `GEOIP_`)
- `.env` files
- YAML configuration files
- Programmatic configuration

### Data Models

- **GeoData**: Core geographic data model indexed by geoname_id
- **ProviderConfig**: Provider-specific configuration

## Examples

### Example 1: Simple Lookup

```python
from geoip_geocode.providers import GeoIP2Provider
from geoip_geocode.models import ProviderConfig

config = ProviderConfig(
    name="geoip2",
    database_path="GeoLite2-City.mmdb"
)

provider = GeoIP2Provider(config)
result = provider.lookup("8.8.8.8")

if result:
    print(f"Location: {result.city}, {result.country_name}")
```

### Example 2: Using Configuration File

```python
from geoip_geocode.config import load_config
from geoip_geocode.registry import get_registry
from geoip_geocode.providers import GeoIP2Provider

# Load configuration
config = load_config(yaml_path="config.yaml")

# Setup registry
registry = get_registry()
registry.register("geoip2", GeoIP2Provider)

# Get provider
provider_config = config.get_provider_config("geoip2")
provider = registry.get_provider("geoip2", provider_config)

# Perform lookup
result = provider.lookup("8.8.8.8")
```

### Example 3: Multiple Providers with Priority

```python
from geoip_geocode.registry import get_registry
from geoip_geocode.providers import GeoIP2Provider
from geoip_geocode.models import ProviderConfig

registry = get_registry()
registry.register("geoip2", GeoIP2Provider)

# Configure multiple providers with different priorities
config1 = ProviderConfig(name="geoip2", database_path="db1.mmdb", priority=100)
config2 = ProviderConfig(name="geoip2", database_path="db2.mmdb", priority=50)

provider1 = registry.get_provider("geoip2", config1)

# Get available providers sorted by priority
providers = registry.get_available_providers()

# Try providers in order until one succeeds
for provider in providers:
    result = provider.lookup("8.8.8.8")
    if result:
        print(f"Found with provider priority {provider.config.priority}")
        break
```

## License

MIT License

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Links

- [MaxMind GeoLite2](https://dev.maxmind.com/geoip/geolite2-free-geolocation-data)
- [GeoNames](https://www.geonames.org/)
- [Pydantic Documentation](https://docs.pydantic.dev/)
- [Typer Documentation](https://typer.tiangolo.com/)
