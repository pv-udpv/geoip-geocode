"""
geoip-geocode: Geocoding and IP lookup tools with support for multiple providers.

This package provides a unified interface for geocoding and IP geolocation
using various providers. It is designed to be modular and extensible.
"""

__version__ = "0.1.0"

from geoip_geocode.models import GeoData, ProviderConfig
from geoip_geocode.registry import ProviderRegistry, get_registry

__all__ = [
    "GeoData",
    "ProviderConfig",
    "ProviderRegistry",
    "get_registry",
]
