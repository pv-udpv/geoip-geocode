---
runme:
  document:
    relativePath: README.md
  session:
    id: 01K7Y780YWYNDQ18DSA4YKW9SF
    updated: 2025-10-19 17:31:03+03:00
---

# geoip-geocode

Geocoding and IP lookup tools with support for multiple providers.

> 🚀 **Quick Start**: See [QUICKSTART.md](QUICKSTART.md) for a rapid introduction to the library!

## Features

- 🌍 **Multiple Provider Support**: Extensible provider registry system
- 🔌 **GeoIP2/MaxMind Integration**: Built-in support for MaxMind databases
- 🗺️ **IP*******on Support**: Alternative provider with IP*******on databases
- ⚙️ **Flexible Configuration**: Configure via Pydantic models, .env, or YAML files
- 🖥️ **CLI Interface**: Powerful command-line tool using Typer
- 📊 __Structured Data__: GeoData objects indexed by geoname_id
- 🧩 **Modular Design**: Easy to add new providers
- 📝 **Well Documented**: Comprehensive docstrings and examples

## Installation

```bash
pip install geoip-geocode

```

For development with `uv` (recommended):

```bash
uv sync --all-extras

```

Or with pip in a virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
pip install -e ".[dev]"

```

### Health Check

Run the health check script to verify everything is set up correctly:

```bash
./scripts/health_check.sh

```

## Quick Start

### Command Line Interface

Look up an IP address:

```bash
# Basic lookup (requires Ge**************db in current directory)
geoip-geocode lookup 8.***.8

# Specify database path
geoip-geocode lookup 8.***.8 --database /path/to/Ge**************db

# Use configuration file
geoip-geocode lookup 8.***.8 --config config.yaml

```

Initialize a configuration file:

```bash
geoip-geocode config-init --database /path/to/Ge**************db

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

 Using GeoIP2 Provider

```python
from geoip_geocode.models import ProviderConfig
from geoip_geocode.providers import Ge**********er

# Configure provider
config = ProviderConfig(
    name="ge**p2",
    enabled=True,
    da*********th="/path/to/Ge**************db"
)

# Create provider
provider = Ge*****************ig)

# Look up an IP address
result = pr***********up("8.***.8")

if result:
    print(f"City: {result.city}")
    print(f"Country: {result.country_name}")
    print(f"Coordinates: {result.latitude}, {result.longitude}")
    print(f"GeoName ID: {result.geoname_id}")

```

 Using IP2Location Provider

```python
from geoip_geocode.models import ProviderConfig
from geoip_geocode.providers import IP***************er

# Configure IP*******on provider
config = ProviderConfig(
    name="ip*******on",
    enabled=True,
    da*********th="/path/to/IP*********************IN"
)

# Create provider
provider = IP**********************ig)

# Look up an IP address
result = pr***********up("8.***.8")

if result:
    print(f"City: {result.city}")
    print(f"Country: {result.country_name}")

```

### Using the Registry

```python
from geoip_geocode.registry import get_registry
from geoip_geocode.providers import Ge**********er, IP***************er
from geoip_geocode.models import ProviderConfig

# Get global registry
registry = get_registry()

# Register providers
re*************er("ge**p2", Ge**********er)
re*************er("ip*******on", IP***************er)

# Create provider config
config = ProviderConfig(
    name="ge**p2",
    da*********th="/path/to/Ge**************db",
    pr********00
)

# Get provider instance
provider = re*****************er("ge**p2", config)

# Perform lookup
result = pr***********up("8.***.8")

```

## Configuration

### YAML Configuration

Create a `config.yaml` file:

```yaml
default_provider: ge**p2
cache_enabled: false
cache_ttl: 3600

providers:
  - name: ge**p2
    enabled: true
    priority: 100
    database_path: ./Ge**************db
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
GE*************************p2
GEOIP_CACHE_ENABLED=false
GE****************00
MAXMIND_LICENSE_KEY=your_license_key_here

```

Configuration is automatically loaded from `.env` files.

## Data Model

All geographic data is returned as `GeoData` objects indexed by `geoname_id`:

```python
from geoip_geocode.models import GeoData

geo_data = GeoData(
    ge**************80,          # Primary key from GeoNames
    ip******ss="8.***.8",
    country_code="US",
    country_name="United States",
    city="Mountain View",
    po*******de="94035",
    la***********86,
    lo***************38,
    time_zone="America/Los_Angeles",
    continent_code="NA",
    continent_name="North America",
    subdivision="California",
    subdivision_code="CA",
    ac***************00,
    pr****er="ge**p2"
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
            ge************45,
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

## Ge**P2 Database Setup

### Getting a Database

1. Sign up for a free account at [MaxMind](ht**************************************up)
2. Get your license key
3. Download the Ge*********ty database from the MaxMind website

### Database Locations

Common database locations:

- **Linux**: `/usr/share/GeoIP/Ge**************db`
- **macOS**: `/usr/local/share/GeoIP/Ge**************db`
- **Windows**: `C:\Pr*******ta\Ma***nd\Ge**************db`

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
3. **Concrete Providers**: Implementations (e.g., Ge**********er)

### Configuration Management

Configuration is handled through Pydantic models with support for:

- Environment variables (prefixed with `GEOIP_`)
- `.env` files
- YAML configuration files
- Programmatic configuration

### Data Models

- __GeoData__: Core geographic data model indexed by geoname_id
- **ProviderConfig**: Provider-specific configuration

## Examples

### Example 1: Simple Lookup

```python
from geoip_geocode.providers import Ge**********er
from geoip_geocode.models import ProviderConfig

config = ProviderConfig(
    name="ge**p2",
    da*********th="Ge**************db"
)

provider = Ge*****************ig)
result = pr***********up("8.***.8")

if result:
    print(f"Location: {result.city}, {result.country_name}")

```

### Example 2: Using Configuration File

```python
from geoip_geocode.config import load_config
from geoip_geocode.registry import get_registry
from geoip_geocode.providers import Ge**********er

# Load configuration
config = load_config(yaml_path="config.yaml")

# Setup registry
registry = get_registry()
re*************er("ge**p2", Ge**********er)

# Get provider
provider_config = co**********************ig("ge**p2")
provider = re*****************er("ge**p2", provider_config)

# Perform lookup
result = pr***********up("8.***.8")

```

### Example 3: Multiple Providers with Priority

```python
from geoip_geocode.registry import get_registry
from geoip_geocode.providers import Ge**********er
from geoip_geocode.models import ProviderConfig

registry = get_registry()
re*************er("ge**p2", Ge**********er)

# Configure multiple providers with different priorities
co***g1 = Pr***************me="ge**p2", da*********th="db****db", pr********00)
co***g2 = Pr***************me="ge**p2", da*********th="db****db", pr*******50)

pr*****r1 = re*****************er("ge**p2", co***g1)

# Get available providers sorted by priority
providers = registry.get_available_providers()

# Try providers in order until one succeeds
for provider in providers:
    result = pr***********up("8.***.8")
    if result:
        print(f"Found with provider priority {provider.config.priority}")
        break

```

## License

MIT License

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Links

- [MaxMind Ge****e2](ht********************************************************ta)
- [GeoNames](ht********************rg/)
- [Pydantic Documentation](ht*********************ev/)
- [Typer Documentation](ht**********************om/)
