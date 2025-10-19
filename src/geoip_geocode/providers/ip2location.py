"""IP2Location provider implementation."""

import os
from pathlib import Path
from typing import Any, Optional

try:
    import IP2Location
except ImportError:
    IP2Location = None

from geoip_geocode.models import GeoData, ProviderConfig
from geoip_geocode.registry import BaseProvider
from geoip_geocode.updater import IP2LocationUpdater


from pydantic_settings import  BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    license_key: Optional[str] = None
    account_id: Optional[str] = None
    edition_id: str = "DB11LITEBIN"
    config: SettingsConfigDict = SettingsConfigDict(
        env_prefix='IP2LOCATION_',
        env_file='.env',
        env_file_encoding='utf-8'
    
    )


class IP2LocationProvider(BaseProvider):
    """
    IP2Location database provider.

    This provider uses IP2Location's BIN database files for IP geolocation.
    It requires a local BIN database file and the IP2Location Python library.

    Attributes:
        config: Provider configuration
        database: IP2Location database instance

    Examples:
        >>> config = ProviderConfig(
        ...     name="ip2location",
        ...     database_path="/path/to/IP2LOCATION-LITE-DB11.BIN"
        ... )
        >>> provider = IP2LocationProvider(config)
        >>> result = provider.lookup("8.8.8.8")
        >>> print(result.city)
        Mountain View
    """

    def __init__(self, config: ProviderConfig):
        """
        Initialize IP2Location provider.

        Args:
            config: Provider configuration with database_path

        Raises:
            ImportError: If IP2Location library is not installed
            ValueError: If database_path is not provided
            FileNotFoundError: If database file doesn't exist
        """
        super().__init__(config)

        if IP2Location is None:
            raise ImportError(
                "IP2Location library is not installed. "
                "Install it with: pip install IP2Location"
            )

        self.database: Optional[Any] = None

        if not config.database_path:
            raise ValueError("database_path is required for IP2Location provider")

        # Validate database path
        db_path = self.validate_database_path(config.database_path)

        # Initialize IP2Location database
        self.database = IP2Location.IP2Location(str(db_path))

    def lookup(self, ip_address: str) -> Optional[GeoData]:
        """
        Look up geographic data for an IP address using IP2Location.

        Args:
            ip_address: IP address to look up (IPv4 or IPv6)

        Returns:
            GeoData object if found, None if not found or on error

        Examples:
            >>> result = provider.lookup("8.8.8.8")
            >>> if result:
            ...     print(f"City: {result.city}, Country: {result.country_name}")
        """
        if not self.database:
            return None

        try:
            result = self.database.get_all(ip_address)

            # Check if the result is valid
            if not result or result.country_short == "INVALID_IP_ADDRESS":
                return None

            # IP2Location doesn't provide geoname_id, so we'll create a synthetic one
            # based on the combination of country and city for consistency
            geoname_id = self._generate_synthetic_geoname_id(
                result.country_short, result.city
            )

            # Handle missing or invalid coordinates
            latitude = None
            longitude = None
            if (
                hasattr(result, "latitude")
                and hasattr(result, "longitude")
                and result.latitude != 0.0
                and result.longitude != 0.0
            ):
                latitude = float(result.latitude)
                longitude = float(result.longitude)

            # Handle optional fields
            city = (
                result.city if hasattr(result, "city") and result.city != "-" else None
            )
            region = (
                result.region
                if hasattr(result, "region") and result.region != "-"
                else None
            )
            zipcode = (
                result.zipcode
                if hasattr(result, "zipcode") and result.zipcode != "-"
                else None
            )
            timezone = (
                result.timezone
                if hasattr(result, "timezone") and result.timezone != "-"
                else None
            )

            # Create GeoData object
            geo_data = GeoData(
                geoname_id=geoname_id,
                ip_address=ip_address,
                country_code=result.country_short,
                country_name=result.country_long,
                city=city,
                postal_code=zipcode,
                latitude=latitude,
                longitude=longitude,
                time_zone=timezone,
                subdivision=region,
                # IP2Location doesn't provide continent info by default
                continent_code=self._get_continent_code(result.country_short),
                continent_name=self._get_continent_name(result.country_short),
                provider="ip2location",
            )

            return geo_data

        except Exception as e:
            # Log error and return None
            # In production, you might want to use proper logging
            print(f"IP2Location lookup error: {e}")
            return None

    def is_available(self) -> bool:
        """
        Check if the provider is available.

        Returns:
            True if enabled, IP2Location library is available,
            and database is initialized
        """
        return (
            super().is_available()
            and IP2Location is not None
            and self.database is not None
        )

    def close(self) -> None:
        """Close the database connection."""
        # IP2Location Python library doesn't require explicit closing
        self.database = None

    def _generate_synthetic_geoname_id(
        self, country_code: Optional[str], city: Optional[str]
    ) -> int:
        """
        Generate a synthetic geoname_id for consistency with other providers.

        This creates a hash-based ID from country and city for locations
        that don't have a real geoname_id.

        Args:
            country_code: ISO country code
            city: City name

        Returns:
            Synthetic geoname_id as integer
        """
        if not country_code:
            country_code = "UNKNOWN"
        if not city:
            city = "UNKNOWN"

        # Create a consistent hash for the location
        location_string = f"{country_code}:{city}".upper()
        # Use a simple hash function that produces consistent results
        hash_value = abs(hash(location_string))
        # Ensure it's in a reasonable range (avoiding conflict with real geoname_ids)
        # Real geoname_ids are typically 1-8 digits, we'll use 9+ digit range
        return 900000000 + (hash_value % 99999999)

    def _get_continent_code(self, country_code: str) -> Optional[str]:
        """
        Get continent code for a country.

        Args:
            country_code: ISO country code

        Returns:
            Continent code (e.g., 'NA', 'EU', 'AS')
        """
        # Basic mapping of countries to continents
        continent_mapping = {
            # North America
            "US": "NA",
            "CA": "NA",
            "MX": "NA",
            "GT": "NA",
            "BZ": "NA",
            "SV": "NA",
            "HN": "NA",
            "NI": "NA",
            "CR": "NA",
            "PA": "NA",
            # Europe
            "GB": "EU",
            "FR": "EU",
            "DE": "EU",
            "IT": "EU",
            "ES": "EU",
            "PT": "EU",
            "NL": "EU",
            "BE": "EU",
            "LU": "EU",
            "CH": "EU",
            "AT": "EU",
            "DK": "EU",
            "SE": "EU",
            "NO": "EU",
            "FI": "EU",
            "IS": "EU",
            "IE": "EU",
            "PL": "EU",
            "CZ": "EU",
            "SK": "EU",
            "HU": "EU",
            "SI": "EU",
            "HR": "EU",
            "RS": "EU",
            "BA": "EU",
            "ME": "EU",
            "MK": "EU",
            "AL": "EU",
            "GR": "EU",
            "BG": "EU",
            "RO": "EU",
            "MD": "EU",
            "UA": "EU",
            "BY": "EU",
            "LT": "EU",
            "LV": "EU",
            "EE": "EU",
            "RU": "EU",
            # Asia
            "CN": "AS",
            "JP": "AS",
            "KR": "AS",
            "IN": "AS",
            "ID": "AS",
            "TH": "AS",
            "VN": "AS",
            "PH": "AS",
            "MY": "AS",
            "SG": "AS",
            "MM": "AS",
            "KH": "AS",
            "LA": "AS",
            "BD": "AS",
            "PK": "AS",
            "AF": "AS",
            "IR": "AS",
            "IQ": "AS",
            "TR": "AS",
            "SY": "AS",
            "LB": "AS",
            "JO": "AS",
            "SA": "AS",
            "AE": "AS",
            "QA": "AS",
            "KW": "AS",
            "BH": "AS",
            "OM": "AS",
            "YE": "AS",
            "IL": "AS",
            "PS": "AS",
            "AM": "AS",
            "AZ": "AS",
            "GE": "AS",
            "KZ": "AS",
            "UZ": "AS",
            "TM": "AS",
            "KG": "AS",
            "TJ": "AS",
            "MN": "AS",
            "NP": "AS",
            "BT": "AS",
            "LK": "AS",
            "MV": "AS",
            # Africa
            "ZA": "AF",
            "EG": "AF",
            "NG": "AF",
            "KE": "AF",
            "ET": "AF",
            "TZ": "AF",
            "UG": "AF",
            "MZ": "AF",
            "MG": "AF",
            "CM": "AF",
            "CI": "AF",
            "NE": "AF",
            "BF": "AF",
            "ML": "AF",
            "MW": "AF",
            "ZM": "AF",
            "ZW": "AF",
            "SN": "AF",
            "SO": "AF",
            "TD": "AF",
            "GN": "AF",
            "RW": "AF",
            "BI": "AF",
            "TN": "AF",
            "MA": "AF",
            "DZ": "AF",
            "LY": "AF",
            "SD": "AF",
            "SS": "AF",
            # South America
            "BR": "SA",
            "AR": "SA",
            "CO": "SA",
            "PE": "SA",
            "VE": "SA",
            "CL": "SA",
            "EC": "SA",
            "BO": "SA",
            "PY": "SA",
            "UY": "SA",
            "GY": "SA",
            "SR": "SA",
            "GF": "SA",
            # Oceania
            "AU": "OC",
            "NZ": "OC",
            "FJ": "OC",
            "PG": "OC",
            "SB": "OC",
            "VU": "OC",
            "NC": "OC",
            "PF": "OC",
            "WS": "OC",
            "TO": "OC",
            "TV": "OC",
            "NR": "OC",
            "KI": "OC",
            "FM": "OC",
            "MH": "OC",
            "PW": "OC",
        }

        return continent_mapping.get(country_code)

    def _get_continent_name(self, country_code: str) -> Optional[str]:
        """
        Get continent name for a country.

        Args:
            country_code: ISO country code

        Returns:
            Continent name
        """
        continent_code = self._get_continent_code(country_code)
        if not continent_code:
            return None

        continent_names = {
            "NA": "North America",
            "SA": "South America",
            "EU": "Europe",
            "AS": "Asia",
            "AF": "Africa",
            "OC": "Oceania",
            "AN": "Antarctica",
        }

        return continent_names.get(continent_code)

    def update(self) -> bool:
        """
        Update IP2Location database from remote source.

        Reads configuration from environment variables:
            IP2LOCATION_TOKEN: IP2Location download token (required)
            IP2LOCATION_PRODUCT_CODE: Product code (default: DB11LITE)

        Returns:
            True if update was successful, False otherwise

        Examples:
            >>> provider = IP2LocationProvider(config)
            >>> if provider.update():
            ...     print("Database updated successfully")
        """
        # Check if auto_update is enabled
        if not self.config.auto_update:
            return False

        # Get configuration from environment or config
        token = os.getenv("IP2LOCATION_TOKEN") or self.config.license_key
        if not token:
            print("IP2Location token not found in environment or config")
            return False

        # Get database path or use default
        db_path = (
            self.config.database_path or "./data/databases/IP2LOCATION-LITE-DB11.BIN"
        )
        product_code = os.getenv(
            "IP2LOCATION_PRODUCT_CODE",
            Path(db_path).stem,  # Use database filename
        )

        # Get output directory from database path
        output_dir = Path(db_path).parent

        try:
            # Create updater and download
            updater = IP2LocationUpdater(token=token, output_dir=str(output_dir))

            result_path = updater.download_database(product_code=product_code)

            if result_path:
                # Reload database with new file
                self.close()
                if IP2Location:
                    self.database = IP2Location.IP2Location(str(result_path))
                return True

            return False

        except Exception as e:
            print(f"Database update failed: {e}")
            return False
