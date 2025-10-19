"""
Example: Configuration loading and usage.

Demonstrates how to load and use configuration files with validation.
"""

from pathlib import Path

from geoip_geocode.config import AppConfig, create_default_config, load_config


def example_create_default_config():
    """Create a default configuration."""
    print("=" * 60)
    print("Creating default configuration...")
    print("=" * 60)

    config = create_default_config()

    print(f"Default Provider: {config.default_provider}")
    print(f"Locales: {config.locales}")
    print(f"Cache Enabled: {config.cache.enabled}")
    print(f"Cache TTL: {config.cache.ttl}s")
    print(f"Providers: {len(config.providers)}")
    print(f"Matching Rules: {len(config.matching_rules)}")

    # Save to file
    output_path = "config/config.example.yaml"
    config.to_yaml(output_path)
    print(f"\n✓ Configuration saved to: {output_path}")


def example_load_from_yaml():
    """Load configuration from YAML file."""
    print("\n" + "=" * 60)
    print("Loading configuration from YAML...")
    print("=" * 60)

    config_path = "config/config.minimal.yaml"

    if not Path(config_path).exists():
        print(f"⚠ Configuration file not found: {config_path}")
        return

    config = load_config(yaml_path=config_path)

    print(f"Loaded from: {config_path}")
    print(f"Default Provider: {config.default_provider}")
    print(f"Locales: {config.locales}")
    print(f"Cache: {config.cache.enabled}")
    print(f"Providers: {len(config.providers)}")

    # Show providers
    print("\nProviders:")
    for provider in config.providers:
        print(f"  - {provider.name} (priority: {provider.priority}, enabled: {provider.enabled})")


def example_validate_config():
    """Validate configuration."""
    print("\n" + "=" * 60)
    print("Validating configuration...")
    print("=" * 60)

    config_path = "config/config.minimal.yaml"

    if not Path(config_path).exists():
        print(f"⚠ Configuration file not found: {config_path}")
        return

    config = load_config(yaml_path=config_path)
    results = config.validate_config()

    print(f"Valid: {results['valid']}")
    print(f"Enabled Providers: {results['enabled_providers']}")
    print(f"Total Providers: {results['total_providers']}")
    print(f"Matching Rules: {results['matching_rules']}")

    if results["issues"]:
        print("\nIssues:")
        for issue in results["issues"]:
            print(f"  ✗ {issue}")

    if results["warnings"]:
        print("\nWarnings:")
        for warning in results["warnings"]:
            print(f"  ⚠ {warning}")


def example_get_enabled_providers():
    """Get enabled providers sorted by priority."""
    print("\n" + "=" * 60)
    print("Getting enabled providers...")
    print("=" * 60)

    config_path = "config/config.full.yaml"

    if not Path(config_path).exists():
        print(f"⚠ Configuration file not found: {config_path}")
        return

    config = load_config(yaml_path=config_path)
    enabled = config.get_enabled_providers()

    print(f"Found {len(enabled)} enabled providers:")
    for provider in enabled:
        print(f"  {provider.priority:3d} - {provider.name}")
        if provider.description:
            print(f"       {provider.description}")


def example_access_advanced_config():
    """Access advanced configuration sections."""
    print("\n" + "=" * 60)
    print("Accessing advanced configuration...")
    print("=" * 60)

    config_path = "config/config.full.yaml"

    if not Path(config_path).exists():
        print(f"⚠ Configuration file not found: {config_path}")
        return

    config = load_config(yaml_path=config_path)

    # Cache configuration
    print("Cache Configuration:")
    print(f"  Enabled: {config.cache.enabled}")
    print(f"  Backend: {config.cache.backend}")
    print(f"  Max Size: {config.cache.max_size}")
    print(f"  TTL: {config.cache.ttl}s")

    # Logging configuration
    if config.logging:
        print("\nLogging Configuration:")
        print(f"  Level: {config.logging.level}")
        print(f"  Format: {config.logging.format}")
        if config.logging.file:
            print(f"  File: {config.logging.file}")

    # Matching rules
    if config.matching_rules:
        print(f"\nMatching Rules: {len(config.matching_rules)}")
        for rule in config.matching_rules[:3]:  # Show first 3
            print(f"  - {rule.name} (priority: {rule.priority}, provider: {rule.provider})")


def example_provider_config_details():
    """Show detailed provider configuration."""
    print("\n" + "=" * 60)
    print("Provider configuration details...")
    print("=" * 60)

    config_path = "config/config.full.yaml"

    if not Path(config_path).exists():
        print(f"⚠ Configuration file not found: {config_path}")
        return

    config = load_config(yaml_path=config_path)

    # Get specific provider
    provider = config.get_provider_config("geoip2")
    if provider:
        print("GeoIP2 Provider:")
        print(f"  Name: {provider.name}")
        print(f"  Enabled: {provider.enabled}")
        print(f"  Priority: {provider.priority}")
        print(f"  Locales: {provider.locales}")
        print(f"  Timeout: {provider.timeout}s")
        print(f"  Max Retries: {provider.max_retries}")

        if provider.database:
            print(f"  Database Dir: {provider.database.dir}")
            if provider.database.editions:
                print("  Editions:")
                for key, value in provider.database.editions.items():
                    print(f"    {key}: {value}")

        if provider.auto_update:
            print(f"  Auto-update: {provider.auto_update.enabled}")
            if provider.auto_update.enabled:
                print(f"  Schedule: {provider.auto_update.schedule}")


if __name__ == "__main__":
    # Run all examples
    example_create_default_config()
    example_load_from_yaml()
    example_validate_config()
    example_get_enabled_providers()
    example_access_advanced_config()
    example_provider_config_details()

    print("\n" + "=" * 60)
    print("✓ All examples completed")
    print("=" * 60)
