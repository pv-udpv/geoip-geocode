# geoip-geocode

Geocoding and IP lookup tools with support for multiple providers.

## Features

- **Multiple Provider Support**: GeoIP2, IP2Location, and more
- **Unified API**: Consistent interface across all providers
- **Caching**: Built-in caching for improved performance
- **Configuration**: Flexible YAML and environment-based configuration
- **CLI Tool**: Command-line interface for common operations
- **Type Safety**: Full type hints with Pydantic models

## Quick Start

Install the package:

```bash
pip install geoip-geocode
```

Basic usage:

```python
from geoip_geocode.models import ProviderConfig
from geoip_geocode.providers import GeoIP2Provider

config = ProviderConfig(
    name="geoip2",
    enabled=True,
    database_path="./GeoLite2-City.mmdb"
)

provider = GeoIP2Provider(config)
result = provider.lookup("8.8.8.8")

if result:
    print(f"Location: {result.city}, {result.country_name}")
```

## Documentation Sections

- **[User Guide](user-guide/QUICKSTART.md)**: Get started with geoip-geocode
- **[Providers](providers/overview.md)**: Learn about supported providers
- **[How-to Guides](guides/MULTI_DATABASE_CACHING.md)**: Advanced usage patterns
- **[API Reference](api-reference/models.md)**: Detailed API documentation
- **[Development](development/CONTRIBUTING.md)**: Contributing guidelines

## Project Structure

```
geoip-geocode/
├── src/geoip_geocode/     # Source code
├── examples/              # Usage examples
├── notebooks/             # Jupyter notebooks
├── tests/                 # Test suite
├── docs/                  # Documentation
├── data/                  # Data files
│   ├── databases/         # GeoIP databases
│   ├── samples/           # Sample data
│   └── outputs/           # Output files
├── config/                # Configuration files
└── scripts/               # Utility scripts
```

## License

MIT License - see LICENSE file for details.
