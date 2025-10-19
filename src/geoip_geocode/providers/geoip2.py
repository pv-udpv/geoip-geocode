"""GeoIP2/MaxMind provider implementation."""

from pathlib import Path
from typing import Optional

import geoip2.database
import geoip2.errors

from geoip_geocode.models import GeoData, ProviderConfig
from geoip_geocode.registry import BaseProvider


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

        if config.database_path:
            db_path = Path(config.database_path)
            if not db_path.exists():
                raise FileNotFoundError(
                    f"GeoIP2 database not found: {config.database_path}"
                )
            self.reader = geoip2.database.Reader(str(db_path))

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
        return self.config.enabled and self.reader is not None

    def close(self) -> None:
        """Close the database reader."""
        if self.reader:
            self.reader.close()
            self.reader = None

    def __del__(self):
        """Cleanup when provider is destroyed."""
        self.close()
