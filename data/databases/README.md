# Database Files

This directory should contain the GeoIP database files used by the geoip-geocode package.

**Note**: Database files are NOT tracked in git due to their large size (some exceed GitHub's 50MB limit).

## Required Databases

### MaxMind GeoIP2 Databases

1. **GeoLite2-City.mmdb** - City-level geolocation data
2. **GeoLite2-ASN.mmdb** - ASN (Autonomous System Number) data

**Download from**: https://dev.maxmind.com/geoip/geolite2-free-geolocation-data

You'll need to:
- Create a free MaxMind account
- Download the MMDB format databases
- Place them in this directory

### IP2Location Databases

1. **IP2LOCATION-LITE-DB11.BIN** - IP2Location city database
2. **IP2LOCATION-LITE-ASN.BIN** - IP2Location ASN database

**Download from**: https://lite.ip2location.com/

You'll need to:
- Create a free IP2Location account
- Download the BIN format databases
- Place them in this directory

## Quick Setup

```bash
# After downloading databases, place them here:
cd data/databases/

# You should have:
ls -lh
# GeoLite2-City.mmdb
# GeoLite2-ASN.mmdb
# IP2LOCATION-LITE-DB11.BIN
# IP2LOCATION-LITE-ASN.BIN
```

## Test Databases

For testing purposes, you may create smaller test databases or use the main databases.

## Important Notes

- Database files are excluded from git via `.gitignore`
- Keep databases updated for accurate geolocation
- Check provider licenses for usage terms
- Database files remain on your local disk even though they're not tracked in git
