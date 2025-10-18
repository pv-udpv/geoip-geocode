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
        database_path: Path to local database file (for offline providers)
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
    """

    name: str = Field(..., description="Provider identifier")
    enabled: bool = Field(True, description="Whether provider is enabled")
    priority: int = Field(0, description="Provider priority (higher = more priority)")
    api_key: Optional[str] = Field(None, description="API key")
    database_path: Optional[str] = Field(None, description="Local database path")
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
