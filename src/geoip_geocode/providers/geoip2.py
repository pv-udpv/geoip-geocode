"""GeoIP2/MaxMind provider implementation."""

import os
from pathlib import Path
from typing import Optional

import geoip2.database
import geoip2.errors

from geoip_geocode.models import GeoData, ProviderConfig
from geoip_geocode.registry import BaseProvider
from geoip_geocode.updater import MaxMindUpdater


from pydantic_settings import  BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    license_key: Optional[str] = None
    account_id: Optional[str] = None
    edition_id: str = "GeoLite2-City"
    config: SettingsConfigDict = SettingsConfigDict(
        env_prefix='MAXMIND_',
        env_file='.env',
        env_file_encoding='utf-8'
    
    )

class GeoIP2Provider(BaseProvider):
    """
    GeoIP2/MaxMind database provider.

    This provider uses MaxMind's GeoIP2/GeoLite2 databases for IP geolocation.
    It requires a local MMDB database file.

    Attributes:
        config: Provider configuration
        reader: GeoIP2 database reader instance

    Examples:
        >>> config = ProviderConfig(
        ...     name="geoip2",
        ...     database_path="/path/to/GeoLite2-City.mmdb"
        ... )
        >>> provider = GeoIP2Provider(config)
        >>> result = provider.lookup("8.8.8.8")
        >>> print(result.city)
        Mountain View
    """

    def __init__(self, config: ProviderConfig):
        """
        Initialize GeoIP2 provider.

        Args:
            config: Provider configuration with database_path

        Raises:
            ValueError: If database_path is not provided
            FileNotFoundError: If database file doesn't exist
        """
        super().__init__(config)
        self.reader: Optional[geoip2.database.Reader] = None
        self.locales = config.locales if config.locales else ["en"]

        if not config.database_path:
            raise ValueError("database_path is required for GeoIP2 provider")

        # Validate database path using base class method
        db_path = self.validate_database_path(config.database_path)
        self.reader = geoip2.database.Reader(str(db_path), locales=self.locales)

    def lookup(self, ip_address: str) -> Optional[GeoData]:
        """
        Look up geographic data for an IP address using GeoIP2.

        Args:
            ip_address: IP address to look up (IPv4 or IPv6)

        Returns:
            GeoData object if found, None if not found or on error

        Examples:
            >>> result = provider.lookup("8.8.8.8")
            >>> if result:
            ...     print(f"City: {result.city}, Country: {result.country_name}")
        """
        if not self.reader:
            return None

        try:
            response = self.reader.city(ip_address)

            # Extract geoname_id - use city geoname_id as primary, fall back to country
            geoname_id = None
            if response.city.geoname_id:
                geoname_id = response.city.geoname_id
            elif response.country.geoname_id:
                geoname_id = response.country.geoname_id

            if geoname_id is None:
                # If no geoname_id available, we can't create a valid GeoData object
                return None

            # Extract subdivision info (state/province)
            subdivision = None
            subdivision_code = None
            if response.subdivisions:
                subdivision = response.subdivisions.most_specific.name
                subdivision_code = response.subdivisions.most_specific.iso_code

            # Create GeoData object
            geo_data = GeoData(
                geoname_id=geoname_id,
                ip_address=ip_address,
                country_code=response.country.iso_code,
                country_name=response.country.name,
                city=response.city.name,
                postal_code=response.postal.code,
                latitude=response.location.latitude,
                longitude=response.location.longitude,
                time_zone=response.location.time_zone,
                continent_code=response.continent.code,
                continent_name=response.continent.name,
                subdivision=subdivision,
                subdivision_code=subdivision_code,
                accuracy_radius=response.location.accuracy_radius,
                provider="geoip2",
            )

            return geo_data

        except geoip2.errors.AddressNotFoundError:
            # IP address not found in database
            return None
        except Exception as e:
            # Log error and return None
            # In production, you might want to use proper logging
            print(f"GeoIP2 lookup error: {e}")
            return None

    def is_available(self) -> bool:
        """
        Check if the provider is available.

        Returns:
            True if enabled and database reader is initialized
        """
        return super().is_available() and self.reader is not None

    def close(self) -> None:
        """Close the database reader."""
        if self.reader:
            self.reader.close()
            self.reader = None

    def update(self) -> bool:
        """
        Update MaxMind databases from remote source.

        Reads configuration from environment variables:
            MAXMIND_LICENSE_KEY: MaxMind license key (required)
            MAXMIND_ACCOUNT_ID: MaxMind account ID (optional)
            MAXMIND_EDITION_ID: Database edition (default: GeoLite2-City)

        Returns:
            True if update was successful, False otherwise

        Examples:
            >>> provider = GeoIP2Provider(config)
            >>> if provider.update():
            ...     print("Database updated successfully")
        """
        # Check if auto_update is enabled
        if not self.config.auto_update:
            return False

        # Get configuration from environment or config
        license_key = os.getenv("MAXMIND_LICENSE_KEY") or self.config.license_key
        if not license_key:
            print("MaxMind license key not found in environment or config")
            return False

        account_id = os.getenv("MAXMIND_ACCOUNT_ID")

        # Get database path or use default
        db_path = self.config.database_path or "./data/databases/GeoLite2-City.mmdb"
        edition_id = os.getenv(
            "MAXMIND_EDITION_ID",
            Path(db_path).stem,  # Use database filename
        )

        # Get output directory from database path
        output_dir = Path(db_path).parent

        try:
            # Create updater and download
            updater = MaxMindUpdater(
                license_key=license_key,
                account_id=account_id,
                output_dir=str(output_dir),
            )

            db_path = updater.download_database(edition_id=edition_id)

            if db_path:
                # Reload database reader with new database
                self.close()
                self.reader = geoip2.database.Reader(str(db_path), locales=self.locales)
                return True

            return False

        except Exception as e:
            print(f"Database update failed: {e}")
            return False
