# Configuration Templates

This directory contains three configuration templates for geoip-geocode, each optimized for different use cases.

## Available Templates

### 🚀 config.minimal.yaml (~40 lines)
**Quick start configuration with essential settings only**

**Use when:**
- Getting started with the library
- Simple single-provider setups
- Development and testing environments
- You only need basic IP geolocation

**Includes:**
- Single GeoIP2 provider
- Basic cache settings
- Minimal documentation

**Setup:**
```bash
cp config/config.minimal.yaml config.yaml
```

---

### ⚙️ config.standard.yaml (~110 lines)
**Balanced configuration for production use**

**Use when:**
- Deploying to production
- Need multiple providers with fallback
- Want intelligent routing based on IP characteristics
- Require localization support

**Includes:**
- Two providers (GeoIP2 + IP2Location)
- Matching rules for smart routing
- Private network detection
- IPv6 support
- Auto-update configuration

**Setup:**
```bash
cp config/config.standard.yaml config.yaml
```

---

### 🔧 config.full.yaml (~250 lines)
**Complete configuration with all features**

**Use when:**
- Need advanced customization
- Enterprise deployments
- Complex routing requirements
- Want to explore all available options

**Includes:**
- All provider types and configurations
- Advanced matching rules (ASN, regex, continent)
- Multi-database provider
- Performance tuning options
- HTTP API provider templates
- Comprehensive documentation

**Setup:**
```bash
cp config/config.full.yaml config.yaml
```

---

## Quick Comparison

| Feature | Minimal | Standard | Full |
|---------|---------|----------|------|
| **Providers** | 1 | 2 | 3+ |
| **Matching Rules** | ❌ | ✅ Basic | ✅ Advanced |
| **Localization** | ✅ | ✅ | ✅ |
| **Cache** | ✅ | ✅ | ✅ |
| **Auto-update** | ❌ | ✅ | ✅ |
| **Performance Tuning** | ❌ | ❌ | ✅ |
| **API Templates** | ❌ | ❌ | ✅ |
| **Documentation** | Minimal | Medium | Extensive |

## Environment Variables

All templates require environment variables for sensitive data. Copy `.env.example` to `.env`:

```bash
cp .env.example .env
```

### Required Variables

**For GeoIP2/MaxMind:**
```env
MAXMIND_ACCOUNT_ID=your_account_id
MAXMIND_LICENSE_KEY=your_license_key
```

**For IP2Location:**
```env
IP2LOCATION_TOKEN=your_token
IP2LOCATION_PRODUCT_CODE=DB11LITE
```

## Database Setup

### MaxMind GeoLite2 (Free)

1. Sign up: https://www.maxmind.com/en/geolite2/signup
2. Get your license key
3. Download databases to: `./data/databases/maxmind/`

**Required files:**
- `GeoLite2-City.mmdb`
- `GeoLite2-ASN.mmdb` (optional)
- `GeoLite2-Country.mmdb` (optional)

### IP2Location (Optional)

1. Sign up: https://www.ip2location.com
2. Download databases to: `./data/databases/ip2location/`

## Validation

After setup, validate your configuration:

```bash
# Check if config is valid
geoip-geocode config validate

# View effective configuration
geoip-geocode config show

# Test with sample lookup
geoip-geocode lookup 8.8.8.8 --config config.yaml
```

## Migration Guide

### From Minimal to Standard

1. Copy standard template
2. Add IP2Location provider configuration
3. Enable matching rules
4. Configure auto-update settings

### From Standard to Full

1. Copy full template
2. Uncomment desired advanced features
3. Configure performance settings
4. Add custom matching rules as needed

## Documentation

For detailed information, see:

- **[Configuration Templates Guide](../docs/guides/CONFIG_TEMPLATES.md)** - Complete guide with examples
- **[Matching Rules](../docs/guides/MATCHING_RULES.md)** - How to configure intelligent routing
- **[Locales Guide](../docs/guides/LOCALES.md)** - Localization support
- **[Examples](../examples/README.md)** - Usage examples

## Troubleshooting

### Config Not Loading

```bash
# Specify config explicitly
geoip-geocode lookup 8.8.8.8 --config /path/to/config.yaml
```

### Database Not Found

Check paths in your config:
```yaml
database:
  dir: ./data/databases/maxmind  # Adjust if needed
```

### Provider Fails

Enable debug logging to diagnose:
```yaml
logging:
  level: DEBUG
```

## Best Practices

1. **Start Simple**: Begin with `config.minimal.yaml`
2. **Never Commit Secrets**: Use `.env` for credentials
3. **Enable Caching**: Significantly improves performance
4. **Test After Changes**: Run validation after editing config
5. **Use Version Control**: Track config changes (excluding `.env`)

## Getting Help

- **Documentation**: https://github.com/pv-udpv/geoip-geocode
- **Examples**: `../examples/`
- **Issues**: Open a GitHub issue

---

**Quick Start:**
```bash
# 1. Choose and copy template
cp config/config.minimal.yaml config.yaml

# 2. Setup environment variables
cp .env.example .env
# Edit .env with your credentials

# 3. Download databases (see Database Setup above)

# 4. Test
geoip-geocode lookup 8.8.8.8
