#!/usr/bin/env python3
"""
Example: Demonstrating the improved abstract base provider class.

This example shows the enhanced BaseProvider with better abstracts,
context manager support, and validation utilities.
"""

from pathlib import Path
from typing import Optional

from geoip_geocode.models import GeoData, ProviderConfig
from geoip_geocode.registry import BaseProvider


class CustomProvider(BaseProvider):
    """
    Example custom provider implementation.

    This demonstrates how to implement a custom provider using the
    improved BaseProvider abstract class.
    """

    def __init__(self, config: ProviderConfig):
        """Initialize the custom provider."""
        super().__init__(config)

        # Example: validate database path if provided
        if config.database_path:
            self.db_path = self.validate_database_path(config.database_path)
            print(f"✓ Database path validated: {self.db_path}")
        else:
            self.db_path = None

    def lookup(self, ip_address: str) -> Optional[GeoData]:
        """
        Perform IP lookup (mock implementation).

        This is a mock implementation that returns hardcoded data
        for demonstration purposes.
        """
        print(f"Looking up {ip_address} with CustomProvider...")

        # Mock data for demonstration
        if ip_address == "8.8.8.8":
            return GeoData(
                geoname_id=12345,
                ip_address=ip_address,
                country_code="US",
                country_name="United States",
                city="Mountain View",
                latitude=37.386,
                longitude=-122.0838,
                provider="custom",
            )

        return None

    def is_available(self) -> bool:
        """Check if provider is available."""
        # Use base class check and add custom logic
        return super().is_available() and (
            self.db_path is not None or self.config.api_key is not None
        )

    def close(self) -> None:
        """Clean up resources."""
        print("CustomProvider resources cleaned up")
        self.db_path = None


def base_provider_features_demo():
    """Demonstrate BaseProvider features."""
    print("=== BaseProvider Features Demo ===\n")

    # 1. Basic provider creation
    config = ProviderConfig(name="custom", enabled=True, api_key="test-key")

    provider = CustomProvider(config)
    print(f"1. Provider created: {provider.config.name}")
    print(f"   Enabled: {provider.config.enabled}")
    print(f"   Available: {provider.is_available()}\n")

    # 2. Lookup functionality
    print("2. Lookup functionality:")
    result = provider.lookup("8.8.8.8")
    if result:
        print(f"   ✓ Found: {result.city}, {result.country_name}")
    else:
        print("   ❌ No result found")
    print()

    # 3. Context manager usage
    print("3. Context manager usage:")
    with CustomProvider(config) as ctx_provider:
        print(f"   Provider in context: {ctx_provider.config.name}")
        result = ctx_provider.lookup("8.8.8.8")
        if result:
            print(f"   ✓ Lookup successful: {result.city}")
    print("   Context exited, resources cleaned up\n")

    # 4. Database path validation
    print("4. Database path validation:")

    # Create a test file for validation
    test_db_path = Path("test_db.dat")
    test_db_path.touch()

    try:
        config_with_db = ProviderConfig(
            name="custom", enabled=True, database_path=str(test_db_path)
        )

        provider_with_db = CustomProvider(config_with_db)
        print(f"   ✓ Valid database path accepted: {provider_with_db.db_path}")

        # Test invalid path
        try:
            invalid_config = ProviderConfig(
                name="custom", database_path="/nonexistent/path.db"
            )
            CustomProvider(invalid_config)
        except FileNotFoundError as e:
            print(f"   ✓ Invalid path rejected: {e}")

    finally:
        # Clean up test file
        if test_db_path.exists():
            test_db_path.unlink()

    print()

    # 5. Disabled provider
    print("5. Disabled provider behavior:")
    disabled_config = ProviderConfig(name="custom", enabled=False, api_key="test-key")

    disabled_provider = CustomProvider(disabled_config)
    print(f"   Provider available: {disabled_provider.is_available()}")
    print(f"   (Expected: False due to enabled=False)\n")


def abstract_methods_demo():
    """Demonstrate abstract method enforcement."""
    print("=== Abstract Methods Demo ===\n")

    # This would fail if uncommented because lookup() is not implemented
    """
    class IncompleteProvider(BaseProvider):
        pass  # Missing lookup() implementation
    
    try:
        config = ProviderConfig(name="incomplete")
        IncompleteProvider(config)  # This would raise TypeError
    except TypeError as e:
        print(f"✓ Abstract method enforcement: {e}")
    """

    # This demonstrates that you must implement the abstract method
    print("✓ Abstract method enforcement ensures all providers implement lookup()")
    print("  (Providers that don't implement lookup() cannot be instantiated)")
    print()


def provider_lifecycle_demo():
    """Demonstrate provider lifecycle management."""
    print("=== Provider Lifecycle Demo ===\n")

    config = ProviderConfig(name="lifecycle_test", enabled=True)

    print("1. Creating provider...")
    provider = CustomProvider(config)

    print("2. Using provider...")
    result = provider.lookup("8.8.8.8")

    print("3. Manually closing provider...")
    provider.close()

    print("4. Provider lifecycle complete\n")

    # Demonstrate automatic cleanup with context manager
    print("5. Using context manager for automatic cleanup:")
    with CustomProvider(config) as provider:
        print("   Provider active in context")
        result = provider.lookup("8.8.8.8")
    print("   Provider automatically cleaned up on context exit\n")


if __name__ == "__main__":
    base_provider_features_demo()
    abstract_methods_demo()
    provider_lifecycle_demo()

    print("=== Summary ===")
    print("The improved BaseProvider class provides:")
    print("✓ Abstract method enforcement")
    print("✓ Context manager support")
    print("✓ Database path validation utilities")
    print("✓ Consistent resource management")
    print("✓ Extensible availability checks")
    print("✓ Proper lifecycle management")
