"""
Core data models for geoip-geocode package.

These models define the structure of geographic data and configuration
using Pydantic for validation and serialization.
"""

from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class GeoData(BaseModel):
    """
    Geographic data model indexed by geoname_id.

    This is the core data structure representing geographic information
    from any provider.

    Attributes:
        geoname_id: Primary key - unique identifier from GeoNames database
        ip_address: IP address that was looked up (if applicable)
        country_code: ISO country code (e.g., 'US', 'GB')
        country_name: Full country name
        city: City name
        postal_code: Postal/ZIP code
        latitude: Latitude coordinate
        longitude: Longitude coordinate
        time_zone: Time zone identifier
        continent_code: Continent code (e.g., 'NA', 'EU')
        continent_name: Full continent name
        subdivision: State/province/region name
        subdivision_code: State/province/region code
        accuracy_radius: Accuracy radius in kilometers
        provider: Name of the provider that returned this data

    Examples:
        >>> geo_data = GeoData(
        ...     geoname_id=5375480,
        ...     country_code="US",
        ...     country_name="United States",
        ...     city="Mountain View",
        ...     latitude=37.386,
        ...     longitude=-122.0838,
        ... )
        >>> print(geo_data.geoname_id)
        5375480
    """

    geoname_id: int = Field(..., description="Primary key from GeoNames database")
    ip_address: Optional[str] = Field(None, description="IP address looked up")
    country_code: Optional[str] = Field(None, description="ISO country code")
    country_name: Optional[str] = Field(None, description="Country name")
    city: Optional[str] = Field(None, description="City name")
    postal_code: Optional[str] = Field(None, description="Postal code")
    latitude: Optional[float] = Field(None, description="Latitude coordinate")
    longitude: Optional[float] = Field(None, description="Longitude coordinate")
    time_zone: Optional[str] = Field(None, description="Time zone identifier")
    continent_code: Optional[str] = Field(None, description="Continent code")
    continent_name: Optional[str] = Field(None, description="Continent name")
    subdivision: Optional[str] = Field(None, description="Subdivision name")
    subdivision_code: Optional[str] = Field(None, description="Subdivision code")
    accuracy_radius: Optional[int] = Field(None, description="Accuracy radius in km")
    provider: Optional[str] = Field(None, description="Provider name")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "geoname_id": 5375480,
                "ip_address": "8.8.8.8",
                "country_code": "US",
                "country_name": "United States",
                "city": "Mountain View",
                "latitude": 37.386,
                "longitude": -122.0838,
                "time_zone": "America/Los_Angeles",
            }
        }
    )


class ProviderConfig(BaseModel):
    """
    Configuration model for geocoding providers.

    Attributes:
        name: Provider name/identifier
        enabled: Whether this provider is enabled
        priority: Priority when multiple providers are available
                  (higher = more priority)
        api_key: API key for the provider (if required)
        database_path: Path to local database file (backward compatibility)
        city_database_path: Path to City database file
        asn_database_path: Path to ASN database file
        base_url: Base URL for API providers
        timeout: Request timeout in seconds
        max_retries: Maximum number of retries for failed requests

    Examples:
        >>> config = ProviderConfig(
        ...     name="geoip2",
        ...     enabled=True,
        ...     database_path="/path/to/GeoLite2-City.mmdb",
        ... )
        >>> print(config.name)
        geoip2
        
        >>> # Multi-database configuration
        >>> config = ProviderConfig(
        ...     name="geoip2-enriched",
        ...     city_database_path="/path/to/GeoLite2-City.mmdb",
        ...     asn_database_path="/path/to/GeoLite2-ASN.mmdb"
        ... )
    """

    name: str = Field(..., description="Provider identifier")
    enabled: bool = Field(True, description="Whether provider is enabled")
    priority: int = Field(0, description="Provider priority (higher = more priority)")
    api_key: Optional[str] = Field(None, description="API key")
    database_path: Optional[str] = Field(None, description="Local database path (backward compatibility)")
    city_database_path: Optional[str] = Field(None, description="City database path")
    asn_database_path: Optional[str] = Field(None, description="ASN database path")
    base_url: Optional[str] = Field(None, description="API base URL")
    timeout: int = Field(30, description="Request timeout in seconds")
    max_retries: int = Field(3, description="Maximum retry attempts")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "geoip2",
                "enabled": True,
                "priority": 100,
                "database_path": "/usr/share/GeoIP/GeoLite2-City.mmdb",
                "timeout": 30,
            }
        }
    )

class EnrichedGeoData(GeoData):
    """
    Enhanced geographic data model with ASN information.

    Extends GeoData with additional fields for Autonomous System Number (ASN)
    and network information, providing enriched geolocation data.

    Attributes:
        asn: Autonomous System Number
        asn_organization: ISP or organization name
        network: IP network range in CIDR notation

    Examples:
        >>> enriched_data = EnrichedGeoData(
        ...     geoname_id=5375480,
        ...     country_code="US",
        ...     city="Mountain View",
        ...     latitude=37.386,
        ...     longitude=-122.0838,
        ...     asn=15169,
        ...     asn_organization="Google LLC",
        ...     network="8.8.8.0/24"
        ... )
        >>> print(enriched_data.asn_organization)
        Google LLC
    """

    asn: Optional[int] = Field(None, description="Autonomous System Number")
    asn_organization: Optional[str] = Field(None, description="ISP/Organization name")
    network: Optional[str] = Field(None, description="IP network range (CIDR)")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "geoname_id": 5375480,
                "ip_address": "8.8.8.8",
                "country_code": "US",
                "country_name": "United States",
                "city": "Mountain View",
                "latitude": 37.386,
                "longitude": -122.0838,
                "time_zone": "America/Los_Angeles",
                "asn": 15169,
                "asn_organization": "Google LLC",
                "network": "8.8.8.0/24",
            }
        }
    )

class CacheConfig(BaseModel):
    """
    Cache configuration model.

    Configures caching behavior for IP lookup results to improve performance
    by reducing repeated database queries.

    Attributes:
        enabled: Whether caching is enabled
        backend: Cache backend type ('lru', 'redis', etc.)
        max_size: Maximum number of entries in cache
        ttl: Time-to-live for cache entries in seconds

    Examples:
        >>> config = CacheConfig(
        ...     enabled=True,
        ...     backend="lru",
        ...     max_size=10000,
        ...     ttl=3600
        ... )
        >>> print(config.max_size)
        10000
    """

    enabled: bool = Field(True, description="Enable caching")
    backend: str = Field("lru", description="Cache backend type: 'lru'")
    max_size: int = Field(10000, description="Maximum cache size (number of entries)")
    ttl: int = Field(3600, description="Cache TTL in seconds (default: 1 hour)")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "enabled": True,
                "backend": "lru",
                "max_size": 10000,
                "ttl": 3600,
            }
        }
    )
