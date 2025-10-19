# Data Directory

This directory contains data files used by the geoip-geocode package.

## Structure

- `databases/` - GeoIP and IP2Location database files (.mmdb, .BIN, .ZIP)
- `samples/` - Sample data files for testing and examples
- `outputs/` - Generated output files (CSV, HTML, etc.)

## Database Files

The `databases/` directory contains:
- **GeoLite2-City.mmdb** - MaxMind GeoIP2 City database
- **GeoLite2-ASN.mmdb** - MaxMind GeoIP2 ASN database
- **IP2LOCATION-LITE-DB11.BIN** - IP2Location database
- **IP2LOCATION-LITE-ASN.BIN** - IP2Location ASN database

## Notes

- Database files are not tracked in git for this project
- Keep databases updated regularly for accurate geolocation
- See provider documentation for download instructions
