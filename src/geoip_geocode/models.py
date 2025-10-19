"""
Core data models for geoip-geocode package.

These models define the structure of geographic data and configuration
using Pydantic for validation and serialization.
"""

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator

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
        backend: Cache backend type ('lru', 'memory')
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
    backend: str = Field("lru", description="Cache backend type: 'lru' or 'memory'")
    max_size: int = Field(10000, description="Maximum cache size (1-1000000)")
    ttl: int = Field(3600, description="Cache TTL in seconds (60-86400)")

    @field_validator("max_size")
    @classmethod
    def validate_max_size(cls, v: int) -> int:
        if not 1 <= v <= 1000000:
            raise ValueError("max_size must be between 1 and 1000000")
        return v

    @field_validator("ttl")
    @classmethod
    def validate_ttl(cls, v: int) -> int:
        if not 60 <= v <= 86400:
            raise ValueError("ttl must be between 60 and 86400 seconds")
        return v

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

class DatabaseConfig(BaseModel):
    """
    Database configuration for local database providers.

    Attributes:
        dir: Directory containing database files
        editions: Mapping of data types to database file names
        compressed: Compression format ('zip', 'gz', or None)
        extension: File extension (e.g., 'mmdb', 'BIN')
        tier: Database tier/product level
    """

    dir: str = Field(..., description="Database directory path")
    editions: Optional[Dict[str, str]] = Field(
        None, description="Database editions mapping (city, asn, country)"
    )
    compressed: Optional[str] = Field(None, description="Compression format")
    extension: Optional[str] = Field(None, description="File extension")
    tier: Optional[str] = Field(None, description="Database tier/product")

class AutoUpdateConfig(BaseModel):
    """
    Auto-update configuration for database providers.

    Attributes:
        enabled: Whether auto-update is enabled
        schedule: Cron expression for update schedule
        update_url: Custom update URL (optional)
    """

    enabled: bool = Field(False, description="Enable automatic updates")
    schedule: str = Field("0 3 * * 2", description="Cron schedule (default: 3 AM Tuesday)")
    update_url: Optional[str] = Field(None, description="Custom update URL")

class ProviderConfig(BaseModel):
    """
    Configuration model for geocoding providers.

    Attributes:
        name: Provider name/identifier
        enabled: Whether this provider is enabled
        priority: Priority (lower number = higher priority, 1-999)
        description: Provider description
        locales: Preferred locales for localized data
        database: Database configuration
        api_key: API key for the provider (if required)
        database_path: Path to local database file (backward compatibility)
        city_database_path: Path to City database file
        asn_database_path: Path to ASN database file
        base_url: Base URL for API providers
        timeout: Request timeout in seconds (1-300)
        max_retries: Maximum number of retries (0-10)
        auto_update: Auto-update configuration
        databases: List of database types for multi-database providers
        variants: Database variants mapping
        export: Data types to export

    Examples:
        >>> config = ProviderConfig(
        ...     name="geoip2
        ...     enabled=Tru",e,
        ...     priority=100,
        ...     database_path="/path/to/GeoLite2-City.mmdb",
        ... )
        >>> print(config.name)
        geoip2
    """

    name: str = Field(..., description="Provider identifier")
    enabled: bool = Field(True, description="Whether provider is enabled")
    priority: int = Field(100, description="Provider priority (lower = higher, 1-999)")
    description: Optional[str] = Field(None, description="Provider description")
    locales: List[str] = Field(
        default_factory=lambda: ["en"],
        description="Preferred locales for localized data",
    )
    
    # Database configuration
    database: Optional[DatabaseConfig] = Field(None, description="Database configuration")
    
    # Legacy/backward compatibility fields
    api_key: Optional[str] = Field(None, description="API key")
    database_path: Optional[str] = Field(None, description="Database path (legacy)")
    city_database_path: Optional[str] = Field(None, description="City database path")
    asn_database_path: Optional[str] = Field(None, description="ASN database path")
    
    # API configuration
    base_url: Optional[str] = Field(None, description="API base URL")
    
    # Connection settings
    timeout: int = Field(30, description="Request timeout in seconds (1-300)")
    max_retries: int = Field(3, description="Maximum retry attempts (0-10)")
    
    # Auto-update configuration
    auto_update: Optional[AutoUpdateConfig] = Field(None, description="Auto-update config")
    
    # Multi-database configuration
    databases: Optional[List[str]] = Field(None, description="Database types (city, asn)")
    variants: Optional[Dict[str, List[str]]] = Field(None, description="Database variants")
    export: Optional[List[str]] = Field(None, description="Data types to export")

    @field_validator("priority")
    @classmethod
    def validate_priority(cls, v: int) -> int:
        if not 1 <= v <= 999:
            raise ValueError("priority must be between 1 and 999")
        return v

    @field_validator("timeout")
    @classmethod
    def validate_timeout(cls, v: int) -> int:
        if not 1 <= v <= 300:
            raise ValueError("timeout must be between 1 and 300 seconds")
        return v

    @field_validator("max_retries")
    @classmethod
    def validate_max_retries(cls, v: int) -> int:
        if not 0 <= v <= 10:
            raise ValueError("max_retries must be between 0 and 10")
        return v

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

class LoggingConfig(BaseModel):
    """
    Logging configuration.

    Attributes:
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        format: Log format ('json' or 'text')
        file: Optional log file path
    """

    level: str = Field("INFO", description="Log level")
    format: str = Field("text", description="Log format: 'json' or 'text'")
    file: Optional[str] = Field(None, description="Log file path")

    @field_validator("level")
    @classmethod
    def validate_level(cls, v: str) -> str:
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if v.upper() not in valid_levels:
            raise ValueError(f"level must be one of: {', '.join(valid_levels)}")
        return v.upper()

    @field_validator("format")
    @classmethod
    def validate_format(cls, v: str) -> str:
        if v not in ["json", "text"]:
            raise ValueError("format must be 'json' or 'text'")
        return v

class PerformanceConfig(BaseModel):
    """
    Performance tuning configuration.

    Attributes:
        connection_pool: Connection pool settings
        parallel_lookups: Parallel lookup settings
        memory: Memory optimization settings
    """

    connection_pool: Optional[Dict[str, Any]] = Field(None, description="Connection pool config")
    parallel_lookups: Optional[Dict[str, Any]] = Field(None, description="Parallel lookup config")
    memory: Optional[Dict[str, Any]] = Field(None, description="Memory optimization config")

class ErrorHandlingConfig(BaseModel):
    """
    Error handling configuration.

    Attributes:
        retry_policy: Retry policy settings
        fallback: Fallback behavior settings
        notifications: Error notification settings
    """

    retry_policy: Optional[Dict[str, Any]] = Field(None, description="Retry policy")
    fallback: Optional[Dict[str, Any]] = Field(None, description="Fallback settings")
    notifications: Optional[Dict[str, Any]] = Field(None, description="Notification settings")

class OutputConfig(BaseModel):
    """
    Output configuration.

    Attributes:
        format: Output format ('json', 'yaml', 'csv', 'text')
        pretty_print: Enable pretty printing
        include_metadata: Include metadata in responses
        fields: Field filtering list
    """

    format: str = Field("json", description="Output format")
    pretty_print: bool = Field(True, description="Pretty print output")
    include_metadata: bool = Field(False, description="Include metadata")
    fields: Optional[List[str]] = Field(None, description="Fields to include")

    @field_validator("format")
    @classmethod
    def validate_format(cls, v: str) -> str:
        valid_formats = ["json", "yaml", "csv", "text"]
        if v not in valid_formats:
            raise ValueError(f"format must be one of: {', '.join(valid_formats)}")
        return v

class SecurityConfig(BaseModel):
    """
    Security configuration.

    Attributes:
        allowed_ranges: Allowed IP ranges (CIDR)
        blocked_ranges: Blocked IP ranges (CIDR)
        api_key: API key for access control
    """

    allowed_ranges: Optional[List[str]] = Field(None, description="Allowed IP ranges")
    blocked_ranges: Optional[List[str]] = Field(None, description="Blocked IP ranges")
    api_key: Optional[str] = Field(None, description="API key")
