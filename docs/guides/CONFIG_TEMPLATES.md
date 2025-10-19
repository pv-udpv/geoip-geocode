# Configuration Templates Guide

This guide explains the three configuration templates available for geoip-geocode and helps you choose the right one for your use case.

## Overview

The library provides three configuration templates with different levels of complexity:

| Template | Lines | Use Case | Complexity |
|----------|-------|----------|------------|
| `config.minimal.yaml` | ~40 | Quick start, simple deployments | ⭐ Low |
| `config.standard.yaml` | ~110 | Production use, multiple providers | ⭐⭐ Medium |
| `config.full.yaml` | ~250 | Advanced features, full customization | ⭐⭐⭐ High |

## Template Comparison

### config.minimal.yaml

**Best for:**
- Getting started quickly
- Simple single-provider setups
- Development and testing
- Small projects with basic GeoIP needs

**Includes:**
- Single GeoIP2 provider
- Basic cache configuration
- Essential settings only
- Minimal comments

**Example:**
```yaml
default_provider: geoip2
locales: [en, ru]

cache:
  enabled: true
  max_size: 100000
  ttl: 3600

providers:
  - name: geoip2
    enabled: true
    priority: 100
    database:
      dir: ./data/databases/maxmind
      editions:
        city: GeoLite2-City.mmdb
        asn: GeoLite2-ASN.mmdb
```

### config.standard.yaml

**Best for:**
- Production deployments
- Multiple provider setups
- Projects requiring fallback strategies
- Standard business use cases

**Includes:**
- Two providers (GeoIP2 + IP2Location)
- Matching rules for intelligent routing
- Localization support
- Auto-update configuration
- Provider priority system

**Key Features:**
- Private network detection
- IPv6 support
- Provider fallback
- Environment variable integration

### config.full.yaml

**Best for:**
- Enterprise deployments
- Complex routing requirements
- Custom provider implementations
- Advanced performance tuning

**Includes:**
- All available features
- Advanced matching rules (ASN, regex, continent)
- Multi-database provider
- Performance tuning options
- Commented examples for all features
- HTTP API provider templates

**Additional Features:**
- Connection pooling
- Parallel lookups
- Custom error handling
- Output formatting
- Security restrictions

## Choosing a Template

### Decision Tree

```
START: What's your use case?
│
├─ Just need basic IP lookup?
│  └─ Use: config.minimal.yaml
│
├─ Need multiple providers + fallback?
│  └─ Use: config.standard.yaml
│
└─ Need advanced features or custom setup?
   └─ Use: config.full.yaml
```

### By Experience Level

**Beginners:**
- Start with `config.minimal.yaml`
- Upgrade to `config.standard.yaml` when needed

**Intermediate Users:**
- Start with `config.standard.yaml`
- Reference `config.full.yaml` for specific features

**Advanced Users:**
- Use `config.full.yaml` as reference
- Customize based on specific requirements

## Setup Instructions

### 1. Copy Template

```bash
# For minimal setup
cp config/config.minimal.yaml config.yaml

# For standard setup
cp config/config.standard.yaml config.yaml

# For full setup
cp config/config.full.yaml config.yaml
```

### 2. Configure Environment Variables

Create a `.env` file (use `.env.example` as template):

```bash
cp .env.example .env
```

**Required for all templates:**
- Database paths (if different from defaults)

**Required for auto-updates:**
- `MAXMIND_ACCOUNT_ID`
- `MAXMIND_LICENSE_KEY`
- `IP2LOCATION_TOKEN` (if using IP2Location)

### 3. Download Databases

```bash
# MaxMind GeoLite2 (free account required)
# https://www.maxmind.com/en/geolite2/signup

# Place databases in:
# - ./data/databases/maxmind/GeoLite2-City.mmdb
# - ./data/databases/maxmind/GeoLite2-ASN.mmdb
```

### 4. Validate Configuration

```bash
# Check if configuration is valid
geoip-geocode config validate

# View effective configuration
geoip-geocode config show

# Test with sample lookup
geoip-geocode lookup 8.8.8.8 --config config.yaml
```

## Migration Between Templates

### From Minimal to Standard

Add these sections to your config:

```yaml
# Add matching rules
matching_rules:
  - name: private_networks
    enabled: true
    priority: 10
    # ... (see config.standard.yaml)

# Add second provider
providers:
  - name: ip2location
    enabled: true
    priority: 200
    # ... (see config.standard.yaml)
```

### From Standard to Full

Add advanced features as needed:

```yaml
# Performance tuning
performance:
  connection_pool:
    enabled: true
    max_connections: 10

# Advanced matching rules
matching_rules:
  - name: cdn_traffic
    conditions:
      - type: asn
        values: ["13335", "16509"]
```

## Common Patterns

### Pattern 1: Single Provider, No Cache

```yaml
default_provider: geoip2
cache:
  enabled: false

providers:
  - name: geoip2
    enabled: true
    database:
      dir: ./data/databases/maxmind
```

### Pattern 2: Multiple Providers with Fallback

```yaml
default_provider: geoip2

providers:
  - name: geoip2
    priority: 100  # Try first
  - name: ip2location
    priority: 200  # Fallback
```

### Pattern 3: Geographic Routing

```yaml
matching_rules:
  - name: asia_pacific
    conditions:
      - type: country
        values: [CN, JP, KR, SG]
    provider: ip2location
  
  - name: rest_of_world
    conditions:
      - type: country
        values: ["*"]  # Match all
    provider: geoip2
```

## Environment-Specific Configs

### Development

```yaml
cache:
  enabled: false  # Disable cache for testing
  
providers:
  - name: geoip2
    timeout: 5  # Shorter timeout
```

### Production

```yaml
cache:
  enabled: true
  max_size: 1000000  # Larger cache
  ttl: 7200  # 2 hours

providers:
  - name: geoip2
    timeout: 30
    max_retries: 3
    auto_update:
      enabled: true
```

## Troubleshooting

### Config Not Found

```bash
# Specify config location explicitly
geoip-geocode lookup 8.8.8.8 --config /path/to/config.yaml
```

### Database Not Found

Check database paths:
```bash
ls -la data/databases/maxmind/
```

Update paths in config:
```yaml
database:
  dir: /absolute/path/to/databases
```

### Provider Fails

Enable fallback provider:
```yaml
providers:
  - name: geoip2
    priority: 100
  - name: ip2location
    priority: 200  # Will be used if geoip2 fails
```

## Best Practices

1. **Start Simple**: Begin with `config.minimal.yaml`
2. **Use Environment Variables**: Never hardcode credentials
3. **Enable Caching**: Improves performance significantly
4. **Set Priorities**: Lower numbers = higher priority
5. **Test Changes**: Always validate after modifications
6. **Document Customizations**: Add comments for custom rules
7. **Version Control**: Track config changes (excluding secrets)

## Additional Resources

- [Configuration Reference](../api-reference/config.md)
- [Provider Documentation](../providers/)
- [Matching Rules Guide](MATCHING_RULES.md)
- [Environment Variables](.env.example)

## Support

If you need help choosing or configuring a template:

1. Check the [FAQ](../user-guide/FAQ.md)
2. Review [examples/](../../examples/)
3. Open an issue on GitHub

## Template Maintenance

These templates are maintained as part of the geoip-geocode project:

- **Updates**: Templates are updated with new features
- **Versioning**: Follow semantic versioning
- **Compatibility**: Backward compatible within major versions

---

**Quick Links:**
- [Back to Main Documentation](../index.md)
- [Quickstart Guide](../../QUICKSTART.md)
- [Examples](../../examples/README.md)
