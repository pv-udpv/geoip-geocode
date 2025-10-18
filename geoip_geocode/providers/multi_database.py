"""Multi-database GeoIP2 provider with caching support."""

from pathlib import Path
from typing import Optional

import geoip2.database
import geoip2.errors

from geoip_geocode.cache import CacheBackend, CacheFactory, CacheStats
from geoip_geocode.models import CacheConfig, EnrichedGeoData, ProviderConfig
from geoip_geocode.registry import BaseProvider

class MultiDatabaseGeoIP2Provider(BaseProvider):
    """
    GeoIP2 provider supporting multiple databases (City + ASN) with caching.

    This provider can query multiple MaxMind databases simultaneously to provide
    enriched geolocation data including ASN information. It includes built-in
    caching to improve performance for repeated lookups.

    Attributes:
        config: Provider configuration
        cache: Cache backend for storing lookup results
        city_reader: GeoIP2 City database reader
        asn_reader: GeoIP2 ASN database reader (optional)

    Examples:
        >>> from geoip_geocode.models import ProviderConfig, CacheConfig
        >>> 
        >>> # Basic configuration with City database only
        >>> config = ProviderConfig(
        ...     name="geoip2-enriched",
        ...     city_database_path="./GeoLite2-City.mmdb"
        ... )
        >>> provider = MultiDatabaseGeoIP2Provider(config)
        >>> 
        >>> # Full configuration with City + ASN + caching
        >>> config = ProviderConfig(
        ...     name="geoip2-enriched",
        ...     city_database_path="./GeoLite2-City.mmdb",
        ...     asn_database_path="./GeoLite2-ASN.mmdb"
        ... )
        >>> cache_config = CacheConfig(enabled=True, max_size=10000, ttl=3600)
        >>> provider = MultiDatabaseGeoIP2Provider(config, cache_config)
        >>> 
        >>> # Perform enriched lookup
        >>> result = provider.lookup("8.8.8.8")
        >>> print(f"City: {result.city}, ASN: {result.asn}")
    """

    def __init__(
        self,
        config: ProviderConfig,
        cache_config: Optional[CacheConfig] = None,
    ):
        """
        Initialize multi-database GeoIP2 provider.

        Args:
            config: Provider configuration with database paths
            cache_config: Optional cache configuration (defaults to disabled)

        Raises:
            ValueError: If neither database_path nor city_database_path is provided
            FileNotFoundError: If specified database files don't exist
        """
        super().__init__(config)

        # Initialize cache
        if cache_config is None:
            cache_config = CacheConfig(enabled=False)
        self.cache: CacheBackend = CacheFactory.create_cache(cache_config)

        # Determine City database path (support backward compatibility)
        city_db_path = config.city_database_path or config.database_path
        if not city_db_path:
            raise ValueError(
                "Either 'city_database_path' or 'database_path' must be provided"
            )

        # Initialize City database reader
        city_path = Path(city_db_path)
        if not city_path.exists():
            raise FileNotFoundError(f"City database not found: {city_db_path}")
        self.city_reader = geoip2.database.Reader(str(city_path))

        # Initialize ASN database reader (optional)
        self.asn_reader: Optional[geoip2.database.Reader] = None
        if config.asn_database_path:
            asn_path = Path(config.asn_database_path)
            if not asn_path.exists():
                raise FileNotFoundError(
                    f"ASN database not found: {config.asn_database_path}"
                )
            self.asn_reader = geoip2.database.Reader(str(asn_path))

    def lookup(self, ip_address: str) -> Optional[EnrichedGeoData]:
        """
        Look up geographic and ASN data for an IP address.

        This method:
        1. Checks the cache for existing results
        2. If cache miss, queries City database for location data
        3. Queries ASN database for network information (if available)
        4. Merges results into EnrichedGeoData
        5. Caches the result for future lookups
        6. Returns the enriched data

        Args:
            ip_address: IP address to look up (IPv4 or IPv6)

        Returns:
            EnrichedGeoData object if found, None if not found or on error

        Examples:
            >>> result = provider.lookup("8.8.8.8")
            >>> if result:
            ...     print(f"City: {result.city}")
            ...     print(f"ASN: {result.asn}")
            ...     print(f"Organization: {result.asn_organization}")
        """
        # Try cache first
        cached = self.cache.get(ip_address)
        if cached is not None:
            # Ensure we return EnrichedGeoData
            if isinstance(cached, EnrichedGeoData):
                return cached
            # Convert GeoData to EnrichedGeoData if needed
            return EnrichedGeoData(**cached.model_dump())

        # Cache miss - perform actual lookup
        result = self._do_lookup(ip_address)

        # Cache the result
        if result is not None:
            self.cache.set(ip_address, result)

        return result

    def _do_lookup(self, ip_address: str) -> Optional[EnrichedGeoData]:
        """
        Perform actual database lookups and merge results.

        Args:
            ip_address: IP address to look up

        Returns:
            EnrichedGeoData with merged City + ASN information
        """
        # Query City database
        city_data = self._lookup_city(ip_address)
        if city_data is None:
            return None

        # Query ASN database (optional)
        asn_data = self._lookup_asn(ip_address)

        # Merge results
        enriched_data = EnrichedGeoData(
            **city_data,
            asn=asn_data.get("asn") if asn_data else None,
            asn_organization=asn_data.get("asn_organization") if asn_data else None,
            network=asn_data.get("network") if asn_data else None,
        )

        return enriched_data

    def _lookup_city(self, ip_address: str) -> Optional[dict]:
        """
        Look up City database for location information.

        Args:
            ip_address: IP address to look up

        Returns:
            Dictionary with city data fields, or None if not found
        """
        try:
            response = self.city_reader.city(ip_address)

            # Extract geoname_id - use city geoname_id as primary, fall back to country
            geoname_id = None
            if response.city.geoname_id:
                geoname_id = response.city.geoname_id
            elif response.country.geoname_id:
                geoname_id = response.country.geoname_id

            if geoname_id is None:
                return None

            # Extract subdivision info (state/province)
            subdivision = None
            subdivision_code = None
            if response.subdivisions:
                subdivision = response.subdivisions.most_specific.name
                subdivision_code = response.subdivisions.most_specific.iso_code

            # Build city data dictionary
            return {
                "geoname_id": geoname_id,
                "ip_address": ip_address,
                "country_code": response.country.iso_code,
                "country_name": response.country.name,
                "city": response.city.name,
                "postal_code": response.postal.code,
                "latitude": response.location.latitude,
                "longitude": response.location.longitude,
                "time_zone": response.location.time_zone,
                "continent_code": response.continent.code,
                "continent_name": response.continent.name,
                "subdivision": subdivision,
                "subdivision_code": subdivision_code,
                "accuracy_radius": response.location.accuracy_radius,
                "provider": self.config.name,
            }

        except geoip2.errors.AddressNotFoundError:
            return None
        except Exception as e:
            print(f"City database lookup error for {ip_address}: {e}")
            return None

    def _lookup_asn(self, ip_address: str) -> Optional[dict]:
        """
        Look up ASN database for network information.

        Args:
            ip_address: IP address to look up

        Returns:
            Dictionary with ASN data fields, or None if not found/unavailable
        """
        if self.asn_reader is None:
            return None

        try:
            response = self.asn_reader.asn(ip_address)

            return {
                "asn": response.autonomous_system_number,
                "asn_organization": response.autonomous_system_organization,
                "network": str(response.network) if response.network else None,
            }

        except geoip2.errors.AddressNotFoundError:
            return None
        except Exception as e:
            print(f"ASN database lookup error for {ip_address}: {e}")
            return None

    def is_available(self) -> bool:
        """
        Check if the provider is available.

        Returns:
            True if enabled and at least City database reader is initialized
        """
        return self.config.enabled and self.city_reader is not None

    def get_cache_stats(self) -> CacheStats:
        """
        Get cache statistics.

        Returns:
            CacheStats object with hits, misses, size, and hit rate

        Examples:
            >>> stats = provider.get_cache_stats()
            >>> print(f"Cache hit rate: {stats.hit_rate:.2f}%")
            >>> print(f"Cache size: {stats.size}/{stats.max_size}")
        """
        return self.cache.get_stats()

    def clear_cache(self) -> None:
        """
        Clear all cached entries and reset cache statistics.

        Examples:
            >>> provider.clear_cache()
            >>> stats = provider.get_cache_stats()
            >>> print(stats.size)  # Should be 0
        """
        self.cache.clear()

    def close(self) -> None:
        """Close all database readers."""
        if hasattr(self, 'city_reader') and self.city_reader:
            self.city_reader.close()
            self.city_reader = None

        if hasattr(self, 'asn_reader') and self.asn_reader:
            self.asn_reader.close()
            self.asn_reader = None

    def __del__(self):
        """Cleanup when provider is destroyed."""
        try:
            self.close()
        except:
            pass  # Ignore errors during cleanup
