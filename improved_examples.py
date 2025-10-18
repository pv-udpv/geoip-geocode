#!/usr/bin/env python3
"""
Improved code suggestions for the provider configuration snippet from examples.py.

This file demonstrates various improvements including:
- Constants for magic values
- Path validation and handling
- Error handling
- Configuration builders
- Environment variable support
- Better separation of concerns
"""

import os
from pathlib import Path
from typing import Optional
from geoip_geocode.models import ProviderConfig
from geoip_geocode.config import AppConfig


# Constants for better maintainability
class ProviderDefaults:
    """Constants for provider configuration defaults."""
    GEOIP2_NAME = "geoip2"
    DEFAULT_PRIORITY = 100
    DEFAULT_DATABASE_FILENAME = "GeoLite2-City.mmdb"
    DEFAULT_DATABASE_PATHS = [
        "./GeoLite2-City.mmdb",
        "/usr/share/GeoIP/GeoLite2-City.mmdb",
        "/opt/geoip/GeoLite2-City.mmdb",
        "~/geoip/GeoLite2-City.mmdb"
    ]


def find_database_file(custom_path: Optional[str] = None) -> Optional[Path]:
    """
    Find GeoIP2 database file in common locations.
    
    Args:
        custom_path: Custom path to check first
        
    Returns:
        Path to database file if found, None otherwise
    """
    search_paths = []
    
    # Add custom path first if provided
    if custom_path:
        search_paths.append(custom_path)
    
    # Add environment variable path if set
    env_path = os.getenv("GEOIP_DATABASE_PATH")
    if env_path:
        search_paths.append(env_path)
    
    # Add default paths
    search_paths.extend(ProviderDefaults.DEFAULT_DATABASE_PATHS)
    
    for path_str in search_paths:
        path = Path(path_str).expanduser().resolve()
        if path.exists() and path.is_file():
            return path
    
    return None


def create_provider_config_safe(
    name: str = ProviderDefaults.GEOIP2_NAME,
    enabled: bool = True,
    database_path: Optional[str] = None,
    priority: int = ProviderDefaults.DEFAULT_PRIORITY,
    validate_path: bool = True
) -> ProviderConfig:
    """
    Create a provider configuration with validation and error handling.
    
    Args:
        name: Provider name
        enabled: Whether provider is enabled
        database_path: Path to database file
        priority: Provider priority
        validate_path: Whether to validate database path exists
        
    Returns:
        ProviderConfig instance
        
    Raises:
        FileNotFoundError: If database path validation fails
        ValueError: If invalid parameters provided
    """
    if not name or not isinstance(name, str):
        raise ValueError("Provider name must be a non-empty string")
    
    if priority < 0:
        raise ValueError("Priority must be non-negative")
    
    # Find database file if not explicitly provided
    if database_path is None:
        db_path = find_database_file()
        if db_path is None:
            if validate_path:
                raise FileNotFoundError(
                    f"GeoIP2 database not found in default locations. "
                    f"Please download {ProviderDefaults.DEFAULT_DATABASE_FILENAME} "
                    f"or set GEOIP_DATABASE_PATH environment variable."
                )
            database_path = ProviderDefaults.DEFAULT_DATABASE_PATHS[0]
        else:
            database_path = str(db_path)
    else:
        # Validate provided path
        if validate_path:
            path = Path(database_path).expanduser().resolve()
            if not path.exists():
                raise FileNotFoundError(f"Database file not found: {database_path}")
            if not path.is_file():
                raise ValueError(f"Database path is not a file: {database_path}")
            database_path = str(path)
    
    return ProviderConfig(
        name=name,
        enabled=enabled,
        database_path=database_path,
        priority=priority
    )


class ProviderConfigBuilder:
    """Builder pattern for creating provider configurations."""
    
    def __init__(self):
        self._name = ProviderDefaults.GEOIP2_NAME
        self._enabled = True
        self._database_path = None
        self._priority = ProviderDefaults.DEFAULT_PRIORITY
        self._validate_path = True
    
    def name(self, name: str) -> 'ProviderConfigBuilder':
        """Set provider name."""
        self._name = name
        return self
    
    def enabled(self, enabled: bool) -> 'ProviderConfigBuilder':
        """Set enabled status."""
        self._enabled = enabled
        return self
    
    def database_path(self, path: str) -> 'ProviderConfigBuilder':
        """Set database path."""
        self._database_path = path
        return self
    
    def priority(self, priority: int) -> 'ProviderConfigBuilder':
        """Set priority."""
        self._priority = priority
        return self
    
    def skip_validation(self) -> 'ProviderConfigBuilder':
        """Skip database path validation."""
        self._validate_path = False
        return self
    
    def build(self) -> ProviderConfig:
        """Build the provider configuration."""
        return create_provider_config_safe(
            name=self._name,
            enabled=self._enabled,
            database_path=self._database_path,
            priority=self._priority,
            validate_path=self._validate_path
        )


def example_original_code():
    """Original code from examples.py with issues highlighted."""
    print("ORIGINAL CODE (with issues):")
    print("=" * 50)
    
    config = AppConfig(
        default_provider="geoip2",
        cache_enabled=False,
    )
    
    # ISSUES:
    # 1. Hardcoded database path
    # 2. Magic number (priority=100)
    # 3. No validation that file exists
    # 4. No error handling
    # 5. Path as string instead of Path object
    provider_config = ProviderConfig(
        name="geoip2",  # Hardcoded string
        enabled=True,
        database_path="./GeoLite2-City.mmdb",  # Hardcoded path, might not exist
        priority=100  # Magic number
    )
    config.add_provider_config(provider_config)
    
    print("✗ Issues: Hardcoded values, no validation, no error handling")


def example_improved_basic():
    """Improved version with constants and basic validation."""
    print("\nIMPROVED VERSION 1 (Basic improvements):")
    print("=" * 50)
    
    config = AppConfig(
        default_provider=ProviderDefaults.GEOIP2_NAME,
        cache_enabled=False,
    )
    
    try:
        # Use constants instead of magic values
        provider_config = ProviderConfig(
            name=ProviderDefaults.GEOIP2_NAME,
            enabled=True,
            database_path=str(find_database_file() or ProviderDefaults.DEFAULT_DATABASE_PATHS[0]),
            priority=ProviderDefaults.DEFAULT_PRIORITY
        )
        config.add_provider_config(provider_config)
        print("✓ Improvements: Constants, file search, basic error handling")
        
    except Exception as e:
        print(f"✗ Error creating provider config: {e}")


def example_improved_safe():
    """Improved version with comprehensive validation."""
    print("\nIMPROVED VERSION 2 (Safe with validation):")
    print("=" * 50)
    
    config = AppConfig(
        default_provider=ProviderDefaults.GEOIP2_NAME,
        cache_enabled=False,
    )
    
    try:
        # Use safe creation function with validation
        provider_config = create_provider_config_safe(
            name=ProviderDefaults.GEOIP2_NAME,
            enabled=True,
            priority=ProviderDefaults.DEFAULT_PRIORITY,
            validate_path=True  # Validates file exists
        )
        config.add_provider_config(provider_config)
        print("✓ Improvements: Full validation, error handling, path resolution")
        
    except FileNotFoundError as e:
        print(f"✗ Database file error: {e}")
        # Fallback: create config without validation for demonstration
        provider_config = create_provider_config_safe(
            validate_path=False
        )
        config.add_provider_config(provider_config)
        print("✓ Fallback: Created config without validation")
        
    except Exception as e:
        print(f"✗ Unexpected error: {e}")


def example_improved_builder():
    """Improved version using builder pattern."""
    print("\nIMPROVED VERSION 3 (Builder pattern):")
    print("=" * 50)
    
    config = AppConfig(
        default_provider=ProviderDefaults.GEOIP2_NAME,
        cache_enabled=False,
    )
    
    try:
        # Use builder pattern for flexible configuration
        provider_config = (ProviderConfigBuilder()
                          .name(ProviderDefaults.GEOIP2_NAME)
                          .enabled(True)
                          .priority(ProviderDefaults.DEFAULT_PRIORITY)
                          .skip_validation()  # Skip for demo purposes
                          .build())
        
        config.add_provider_config(provider_config)
        print("✓ Improvements: Builder pattern, fluent interface, flexible configuration")
        
    except Exception as e:
        print(f"✗ Error with builder: {e}")


def example_environment_aware():
    """Environment-aware configuration."""
    print("\nIMPROVED VERSION 4 (Environment-aware):")
    print("=" * 50)
    
    config = AppConfig(
        default_provider=ProviderDefaults.GEOIP2_NAME,
        cache_enabled=False,
    )
    
    # Read configuration from environment variables
    db_path = os.getenv("GEOIP_DATABASE_PATH")
    priority = int(os.getenv("GEOIP_PRIORITY", ProviderDefaults.DEFAULT_PRIORITY))
    enabled = os.getenv("GEOIP_ENABLED", "true").lower() == "true"
    
    try:
        provider_config = create_provider_config_safe(
            name=ProviderDefaults.GEOIP2_NAME,
            enabled=enabled,
            database_path=db_path,
            priority=priority,
            validate_path=False  # Skip validation for demo
        )
        config.add_provider_config(provider_config)
        print("✓ Improvements: Environment variable support, configurable without code changes")
        
    except Exception as e:
        print(f"✗ Error with environment config: {e}")


def main():
    """Demonstrate all improvements."""
    print("PROVIDER CONFIGURATION IMPROVEMENTS")
    print("=" * 60)
    print("\nDemonstrating various ways to improve the original code:")
    
    example_original_code()
    example_improved_basic()
    example_improved_safe()
    example_improved_builder()
    example_environment_aware()
    
    print("\n" + "=" * 60)
    print("KEY IMPROVEMENTS SUMMARY:")
    print("=" * 60)
    print("1. ✓ Use constants instead of magic values")
    print("2. ✓ Validate file paths and handle missing files")
    print("3. ✓ Add comprehensive error handling")
    print("4. ✓ Support environment variables for configuration")
    print("5. ✓ Use Path objects for better path handling")
    print("6. ✓ Implement builder pattern for flexibility")
    print("7. ✓ Provide fallback mechanisms")
    print("8. ✓ Better separation of concerns")
    print("9. ✓ More descriptive error messages")
    print("10. ✓ Support for multiple database locations")


if __name__ == "__main__":
    main()
