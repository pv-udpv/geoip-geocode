# Configuration Guide

This guide describes the comprehensive configuration system for geoip-geocode.

## Overview

The configuration system supports:

- **YAML configuration files** with full schema validation
- **Environment variables** for sensitive data and overrides
- **Multiple providers** with priority-based selection
- **Matching rules** for intelligent provider selection
- **Cache configuration** for performance optimization
- **Advanced settings** for logging, error handling, output, and security

## Configuration Sources

Configuration is loaded with the following priority (highest to lowest):

1. YAML configuration file (if provided)
2. Environment variables (prefixed with `GEOIP_`)
3. `.env` file
4. Default values

## Configuration File Structure

### Basic Settings

```yaml
# Default provider to use when none is specified
default_provider: geoip2

# Default locales for localized data (country names, city names, etc.)
# First locale in the list is preferred, fallback to next if not available
locales:
  - en  # English (recommended as primary)
  - ru  # Russian
```

### Cache Configuration

```yaml
cache:
  enabled: true          # Enable/disable caching
  backend: lru           # Cache backend: 'lru' or 'memory'
  max_size: 100000       # Maximum cache entries (1-1000000)
  ttl: 3600              # Cache TTL in seconds (60-86400)
```

**Validation:**
- `max_size`: Must be between 1 and 1,000,000
- `ttl`: Must be between 60 and 86,400 seconds (1 minute to 24 hours)

### Provider Configuration

Providers are configured with a priority system where **lower numbers = higher priority**.

```yaml
providers:
  - name: geoip2
    enabled: true
    priority: 100        # Lower = higher priority (1-999)
    description: "MaxMind GeoIP2 / GeoLite2 database provider"
    
    # Locales override (optional, uses global if not specified)
    locales:
      - en
      - ru
    
    # Database configuration
    database:
      dir: ./data/databases/maxmind
      editions:
        city: GeoLite2-City.mmdb
        asn: GeoLite2-ASN.mmdb
        country: GeoLite2-Country.mmdb
    
    # Connection settings
    timeout: 30          # Timeout in seconds (1-300)
    max_retries: 3       # Max retry attempts (0-10)
    
    # Auto-update configuration (optional)
    auto_update:
      enabled: false
      schedule: "0 3 * * 2"  # Cron expression
```

**Validation:**
- `priority`: Must be between 1 and 999
- `timeout`: Must be between 1 and 300 seconds
- `max_retries`: Must be between 0 and 10

### Matching Rules

Matching rules enable intelligent provider selection based on IP characteristics:

```yaml
matching_rules:
  - name: private_networks
    description: "Private and local IP addresses"
    enabled: true
    priority: 10         # Lower = higher priority
    match_all: false     # OR logic: match any condition
    conditions:
      - type: ip_range
        values:
          - "10.0.0.0/8"
          - "172.16.0.0/12"
          - "192.168.0.0/16"
    provider: geoip2
    fallback_provider: ip2location  # Optional fallback
```

**Condition Types:**
- `ip_range`: Match CIDR ranges
- `ip_version`: Match IPv4 (4) or IPv6 (6)
- `country`: Match country codes (e.g., "US", "RU")
- `continent`: Match continent codes (e.g., "EU", "AS")
- `asn`: Match Autonomous System Numbers
- `regex`: Match IP addresses with regex patterns

**Match Logic:**
- `match_all: true` - ALL conditions must match (AND logic)
- `match_all: false` - ANY condition can match (OR logic)

### Logging Configuration

```yaml
logging:
  level: INFO          # DEBUG, INFO, WARNING, ERROR, CRITICAL
  format: json         # 'json' or 'text'
  file: ./logs/geoip-geocode.log  # Optional log file path
```

### Performance Tuning (Advanced)

```yaml
performance:
  connection_pool:
    enabled: true
    max_connections: 10
    min_connections: 2
  
  parallel_lookups:
    enabled: false
    max_workers: 4
  
  memory:
    max_database_size: 512  # MB
```

### Error Handling

```yaml
error_handling:
  retry_policy:
    max_attempts: 3
    backoff_factor: 1.5
    retry_on:
      - timeout
      - connection_error
  
  fallback:
    enabled: true
    use_next_priority: true
```

### Output Configuration

```yaml
output:
  format: json         # 'json', 'yaml', 'csv', or 'text'
  pretty_print: true
  include_metadata: false
  fields:              # Optional field filtering
    - country
    - city
    - latitude
    - longitude
```

### Security Settings

```yaml
security:
  allowed_ranges:      # Restrict lookups to specific ranges
    - 10.0.0.0/8
    - 172.16.0.0/12
  
  blocked_ranges:      # Block specific ranges
    - 169.254.0.0/16
  
  api_key: ""          # API key for access control
```

## Environment Variables

All sensitive data should be configured via environment variables:

```bash
# Provider Configuration
GEOIP_DEFAULT_PROVIDER=geoip2
GEOIP_CACHE_ENABLED=true
GEOIP_CACHE_TTL=3600

# MaxMind Configuration
MAXMIND_ACCOUNT_ID=your_account_id
MAXMIND_ACCOUNT_NAME=your_email@example.com
MAXMIND_LICENSE_KEY=your_license_key
MAXMIND_EDITION_ID=GeoLite2-City

# IP2Location Configuration
IP2LOCATION_TOKEN=your_token
IP2LOCATION_PRODUCT_CODE=DB11LITE
```

## Configuration Templates

Three configuration templates are provided:

1. **config.minimal.yaml** - Minimal configuration for quick start
2. **config.standard.yaml** - Standard configuration with common settings
3. **config.full.yaml** - Full configuration with all available options

## CLI Commands

### Initialize Configuration

```bash
# Create default configuration
geoip-geocode config init

# Create with custom template
geoip-geocode config init --template full

# Specify database path
geoip-geocode config init --database /path/to/GeoLite2-City.mmdb
```

### Validate Configuration

```bash
# Validate configuration file
geoip-geocode config validate

# Validate specific file
geoip-geocode config validate --config config/config.yaml
```

Output includes:
- Validation status (valid/invalid)
- Number of enabled providers
- Number of matching rules
- Issues (errors that must be fixed)
- Warnings (potential problems)

### Show Configuration

```bash
# Show configuration overview
geoip-geocode config show

# Show specific sections
geoip-geocode config show --section providers
geoip-geocode config show --section cache
geoip-geocode config show --section rules
```

### Check Provider Status

```bash
# Check provider availability and database files
geoip-geocode config check

# Check specific configuration
geoip-geocode config check --config config/config.yaml
```

## Python API

### Loading Configuration

```python
from geoip_geocode.config import load_config, create_default_config

# Load from YAML file
config = load_config(yaml_path="config.yaml")

# Load from environment variables
config = load_config()

# Create default configuration
config = create_default_config()
```

### Accessing Configuration

```python
# Basic settings
print(config.default_provider)
print(config.locales)

# Cache configuration
print(config.cache.enabled)
print(config.cache.max_size)

# Get provider configuration
provider = config.get_provider_config("geoip2")
print(provider.priority)
print(provider.timeout)

# Get enabled providers (sorted by priority)
enabled = config.get_enabled_providers()
for p in enabled:
    print(f"{p.priority} - {p.name}")
```

### Validating Configuration

```python
# Validate configuration
results = config.validate_config()

if results["valid"]:
    print("✓ Configuration is valid")
else:
    print("✗ Configuration has issues:")
    for issue in results["issues"]:
        print(f"  - {issue}")

# Check warnings
for warning in results["warnings"]:
    print(f"  ⚠ {warning}")
```

### Saving Configuration

```python
# Modify configuration
config.cache.enabled = True
config.cache.max_size = 50000

# Save to file
config.to_yaml("config/my-config.yaml")
```

## Configuration Models

All configuration uses Pydantic models with validation:

- **AppConfig** - Main configuration container
- **CacheConfig** - Cache settings
- **ProviderConfig** - Provider configuration
- **DatabaseConfig** - Database settings
- **AutoUpdateConfig** - Auto-update settings
- **LoggingConfig** - Logging settings
- **PerformanceConfig** - Performance tuning
- **ErrorHandlingConfig** - Error handling
- **OutputConfig** - Output formatting
- **SecurityConfig** - Security settings

## Best Practices

1. **Use environment variables** for all sensitive data (API keys, credentials)
2. **Enable caching** in production environments for better performance
3. **Keep 'en' locale** as fallback for maximum compatibility
4. **Set appropriate timeouts** based on your use case and network conditions
5. **Use matching rules** to optimize provider selection
6. **Validate configuration** after making changes
7. **Monitor database updates** to ensure data freshness
8. **Configure proper logging** for troubleshooting
9. **Test configuration** before deploying to production
10. **Document custom rules** for future reference

## Validation Rules

The configuration system enforces the following validation rules:

1. **At least one enabled provider** must be configured
2. **Default provider** must exist and be enabled
3. **Matching rules** must reference existing providers
4. **Cache settings** must be within valid ranges
5. **Provider priorities** should be unique (warning if duplicates)
6. **Timeout values** must be reasonable (1-300 seconds)
7. **Retry counts** must be within limits (0-10)

## Examples

See `examples/09_config_usage.py` for comprehensive examples:

- Creating default configuration
- Loading from YAML files
- Validating configuration
- Getting enabled providers
- Accessing advanced settings
- Working with provider details

## Troubleshooting

### Configuration file not found

```bash
geoip-geocode config init --output config/config.yaml
```

### Provider not available

Check provider status:
```bash
geoip-geocode config check
```

Ensure database files exist in configured paths.

### Validation errors

Run validation to see specific issues:
```bash
geoip-geocode config validate
```

Fix issues reported in the output.

### Cache not working

1. Ensure `cache.enabled: true` in configuration
2. Check cache size limits
3. Verify TTL is appropriate for your use case

## See Also

- [CONFIG_TEMPLATES.md](CONFIG_TEMPLATES.md) - Configuration template guide
- [MATCHING_RULES.md](MATCHING_RULES.md) - Matching rules documentation
- [DATABASE_UPDATE.md](DATABASE_UPDATE.md) - Database update guide
