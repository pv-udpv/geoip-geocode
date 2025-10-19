"""
Base provider interface and registry system.

This module defines the abstract base class for providers and the registry
system that manages multiple providers.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Type

from geoip_geocode.models import GeoData, ProviderConfig


class BaseProvider(ABC):
    """
    Abstract base class for geocoding/IP lookup providers.

    All providers must implement the lookup method. This ensures a consistent
    interface across different provider implementations.

    Attributes:
        config: Provider configuration

    Examples:
        >>> class MyProvider(BaseProvider):
        ...     def lookup(self, ip_address: str) -> Optional[GeoData]:
        ...         # Implementation here
        ...         pass
    """

    def __init__(self, config: ProviderConfig):
        """
        Initialize provider with configuration.

        Args:
            config: Provider configuration object
        """
        self.config = config

    @abstractmethod
    def lookup(self, ip_address: str) -> Optional[GeoData]:
        """
        Look up geographic data for an IP address.

        Args:
            ip_address: IP address to look up

        Returns:
            GeoData object if found, None otherwise

        Raises:
            NotImplementedError: If not implemented by subclass
        """
        raise NotImplementedError("Subclasses must implement lookup()")

    def is_available(self) -> bool:
        """
        Check if the provider is available and ready to use.

        Returns:
            True if provider is available, False otherwise
        """
        return self.config.enabled


class ProviderRegistry:
    """
    Registry for managing multiple geocoding providers.

    The registry maintains a collection of provider classes and can instantiate
    them with appropriate configurations. It supports priority-based provider
    selection.

    Attributes:
        _providers: Dictionary mapping provider names to provider classes
        _instances: Dictionary of instantiated provider instances

    Examples:
        >>> registry = ProviderRegistry()
        >>> registry.register("geoip2", GeoIP2Provider)
        >>> provider = registry.get_provider("geoip2", config)
    """

    def __init__(self):
        """Initialize the provider registry."""
        self._providers: Dict[str, Type[BaseProvider]] = {}
        self._instances: Dict[str, BaseProvider] = {}

    def register(self, name: str, provider_class: Type[BaseProvider]) -> None:
        """
        Register a provider class.

        Args:
            name: Provider name/identifier
            provider_class: Provider class (must inherit from BaseProvider)

        Examples:
            >>> registry = ProviderRegistry()
            >>> registry.register("geoip2", GeoIP2Provider)
        """
        if not issubclass(provider_class, BaseProvider):
            raise ValueError(f"{provider_class} must inherit from BaseProvider")
        self._providers[name] = provider_class

    def unregister(self, name: str) -> None:
        """
        Unregister a provider.

        Args:
            name: Provider name to unregister
        """
        self._providers.pop(name, None)
        self._instances.pop(name, None)

    def get_provider(
        self, name: str, config: Optional[ProviderConfig] = None
    ) -> Optional[BaseProvider]:
        """
        Get a provider instance by name.

        Args:
            name: Provider name
            config: Optional provider configuration. If not provided,
                   uses a cached instance if available.

        Returns:
            Provider instance if found, None otherwise

        Examples:
            >>> config = ProviderConfig(name="geoip2", database_path="/path/to/db")
            >>> provider = registry.get_provider("geoip2", config)
        """
        if name not in self._providers:
            return None

        # If config provided, create new instance
        if config:
            instance = self._providers[name](config)
            self._instances[name] = instance
            return instance

        # Return cached instance if available
        return self._instances.get(name)

    def list_providers(self) -> List[str]:
        """
        List all registered provider names.

        Returns:
            List of registered provider names

        Examples:
            >>> registry.list_providers()
            ['geoip2', 'ipapi']
        """
        return list(self._providers.keys())

    def get_available_providers(self) -> List[BaseProvider]:
        """
        Get all available (enabled) provider instances.

        Returns:
            List of available provider instances sorted by priority (descending)

        Examples:
            >>> providers = registry.get_available_providers()
            >>> for provider in providers:
            ...     result = provider.lookup("8.8.8.8")
        """
        available = [p for p in self._instances.values() if p.is_available()]
        return sorted(available, key=lambda p: p.config.priority, reverse=True)


# Global registry instance
_global_registry: Optional[ProviderRegistry] = None


def get_registry() -> ProviderRegistry:
    """
    Get the global provider registry instance.

    This function returns a singleton instance of the provider registry
    that can be used throughout the application.

    Returns:
        Global ProviderRegistry instance

    Examples:
        >>> registry = get_registry()
        >>> registry.register("geoip2", GeoIP2Provider)
    """
    global _global_registry
    if _global_registry is None:
        _global_registry = ProviderRegistry()
    return _global_registry
