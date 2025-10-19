# Examples

This directory contains usage examples demonstrating various features of the geoip-geocode package.

## Structure

- `01_basic_lookup.py` - Basic IP lookup functionality
- `02_improved_usage.py` - Improved usage patterns with best practices
- `03_enriched_data.py` - Working with enriched geolocation data (City + ASN databases)
- `04_ip2location_usage.py` - IP2Location provider usage and comparison
- `05_base_provider_demo.py` - Abstract base provider features demonstration
- `06_locales_usage.py` - Using locales for localized geographic data (Russian, German, etc.)
- `07_database_update.py` - Automatic database downloads and updates
- `08_matching_rules.py` - Provider selection rules based on IP characteristics
- `ip2location/` - IP2Location provider specific examples
- `visualization/` - Data visualization examples

## Running Examples

To run any example:

```bash
python examples/01_basic_lookup.py
```

## Requirements

Some examples may require additional setup:

- Download GeoIP2 databases from MaxMind
- Download IP2Location databases
- Configure environment variables (see `config/.env.example`)
