"""
Configuration management for geoip-geocode.

Supports loading configuration from environment variables, .env files,
and YAML files using Pydantic settings.
"""

from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from geoip_geocode.matching import MatchingRule
from geoip_geocode.models import (
    CacheConfig,
    ErrorHandlingConfig,
    LoggingConfig,
    OutputConfig,
    PerformanceConfig,
    ProviderConfig,
    SecurityConfig,
)


class AppConfig(BaseSettings):
    """
    Application configuration.

    Configuration can be loaded from:
    - Environment variables (prefixed with GEOIP_)
    - .env file
    - YAML configuration file

    Attributes:
        config_file: Path to YAML configuration file
        default_provider: Default provider to use
        locales: Default locales for localized data
        cache: Cache configuration
        matching_rules: Provider selection rules
        logging: Logging configuration
        providers: List of provider configurations
        performance: Performance tuning settings
        error_handling: Error handling configuration
        output: Output configuration
        security: Security settings

    Examples:
        >>> config = AppConfig()
        >>> print(config.default_provider)
        geoip2

        >>> # Load from YAML file
        >>> config = AppConfig.from_yaml("config.yaml")
    """

    model_config = SettingsConfigDict(
        env_prefix="GEOIP_",
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Basic settings
    config_file: Optional[str] = Field(
        None, description="Path to YAML configuration file"
    )
    default_provider: str = Field("geoip2", description="Default provider to use")
    locales: List[str] = Field(
        default_factory=lambda: ["en"],
        description="Default locales for localized data (e.g., ['ru', 'en'])",
    )

    # Cache configuration
    cache: CacheConfig = Field(
        default_factory=CacheConfig,
        description="Cache configuration",
    )

    # Legacy cache fields for backward compatibility
    cache_enabled: Optional[bool] = Field(None, description="Enable result caching (legacy)")
    cache_ttl: Optional[int] = Field(None, description="Cache TTL in seconds (legacy)")

    # Matching rules
    matching_rules: List[MatchingRule] = Field(
        default_factory=list,
        description="Provider selection rules",
    )

    # Logging configuration
    logging: Optional[LoggingConfig] = Field(
        None,
        description="Logging configuration",
    )

    # Provider configurations
    providers: List[ProviderConfig] = Field(
        default_factory=list, description="Provider configurations"
    )

    # Advanced configurations
    performance: Optional[PerformanceConfig] = Field(
        None,
        description="Performance tuning settings",
    )

    error_handling: Optional[ErrorHandlingConfig] = Field(
        None,
        description="Error handling configuration",
    )

    output: Optional[OutputConfig] = Field(
        None,
        description="Output configuration",
    )

    security: Optional[SecurityConfig] = Field(
        None,
        description="Security settings",
    )

    def model_post_init(self, __context: Any) -> None:
        """Post-initialization hook to handle legacy fields."""
        # Merge legacy cache fields into cache config
        if self.cache_enabled is not None:
            self.cache.enabled = self.cache_enabled
        if self.cache_ttl is not None:
            self.cache.ttl = self.cache_ttl

    @classmethod
    def from_yaml(cls, yaml_path: str) -> "AppConfig":
        """
        Load configuration from a YAML file.

        Args:
            yaml_path: Path to YAML configuration file

        Returns:
            AppConfig instance loaded from YAML

        Raises:
            FileNotFoundError: If YAML file doesn't exist
            ValueError: If YAML is invalid

        Examples:
            >>> config = AppConfig.from_yaml("config.yaml")
            >>> print(config.default_provider)
        """
        yaml_file = Path(yaml_path)
        if not yaml_file.exists():
            raise FileNotFoundError(f"Config file not found: {yaml_path}")

        with open(yaml_file) as f:
            data = yaml.safe_load(f)

        if not data:
            data = {}

        # Convert cache config
        if "cache" in data and isinstance(data["cache"], dict):
            data["cache"] = CacheConfig(**data["cache"])

        # Convert logging config
        if "logging" in data and isinstance(data["logging"], dict):
            data["logging"] = LoggingConfig(**data["logging"])

        # Convert performance config
        if "performance" in data and isinstance(data["performance"], dict):
            data["performance"] = PerformanceConfig(**data["performance"])

        # Convert error_handling config
        if "error_handling" in data and isinstance(data["error_handling"], dict):
            data["error_handling"] = ErrorHandlingConfig(**data["error_handling"])

        # Convert output config
        if "output" in data and isinstance(data["output"], dict):
            data["output"] = OutputConfig(**data["output"])

        # Convert security config
        if "security" in data and isinstance(data["security"], dict):
            data["security"] = SecurityConfig(**data["security"])

        # Convert matching rules
        if "matching_rules" in data:
            rules = []
            for rule_data in data["matching_rules"]:
                if isinstance(rule_data, dict):
                    rules.append(MatchingRule(**rule_data))
                else:
                    rules.append(rule_data)
            data["matching_rules"] = rules

        # Convert provider configs
        if "providers" in data:
            provider_configs = []
            for p in data["providers"]:
                if isinstance(p, dict):
                    provider_configs.append(ProviderConfig(**p))
                else:
                    provider_configs.append(p)
            data["providers"] = provider_configs

        return cls(**data)

    def to_yaml(self, yaml_path: str) -> None:
        """
        Save configuration to a YAML file.

        Args:
            yaml_path: Path where to save the YAML file

        Examples:
            >>> config = AppConfig()
            >>> config.to_yaml("config.yaml")
        """
        data = self.model_dump(
            exclude_none=True, 
            exclude={"cache_enabled", "cache_ttl"},
            mode="json"  # Use JSON mode to convert enums to values
        )

        yaml_file = Path(yaml_path)
        yaml_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(yaml_file, "w") as f:
            yaml.safe_dump(data, f, default_flow_style=False, sort_keys=False)

    def get_provider_config(self, name: str) -> Optional[ProviderConfig]:
        """
        Get configuration for a specific provider.

        Args:
            name: Provider name

        Returns:
            ProviderConfig if found, None otherwise

        Examples:
            >>> config = AppConfig()
            >>> geoip2_config = config.get_provider_config("geoip2")
        """
        for provider in self.providers:
            if provider.name == name:
                return provider
        return None

    def add_provider_config(self, provider_config: ProviderConfig) -> None:
        """
        Add or update a provider configuration.

        Args:
            provider_config: Provider configuration to add/update

        Examples:
            >>> config = AppConfig()
            >>> provider = ProviderConfig(name="geoip2", database_path="/path/to/db")
            >>> config.add_provider_config(provider)
        """
        # Remove existing config with same name
        self.providers = [p for p in self.providers if p.name != provider_config.name]
        # Add new config
        self.providers.append(provider_config)

    def get_enabled_providers(self) -> List[ProviderConfig]:
        """
        Get all enabled providers sorted by priority.

        Returns:
            List of enabled provider configs, sorted by priority (lower = higher)

        Examples:
            >>> config = AppConfig()
            >>> enabled = config.get_enabled_providers()
        """
        enabled = [p for p in self.providers if p.enabled]
        return sorted(enabled, key=lambda p: p.priority)

    def validate_config(self) -> Dict[str, Any]:
        """
        Validate the configuration and return validation results.

        Returns:
            Dictionary with validation results

        Examples:
            >>> config = AppConfig.from_yaml("config.yaml")
            >>> results = config.validate_config()
            >>> if results["valid"]:
            ...     print("Configuration is valid")
        """
        issues = []
        warnings = []

        # Check if at least one provider is enabled
        enabled_providers = self.get_enabled_providers()
        if not enabled_providers:
            issues.append("No enabled providers found")

        # Check if default provider exists and is enabled
        default_provider_config = self.get_provider_config(self.default_provider)
        if not default_provider_config:
            issues.append(f"Default provider '{self.default_provider}' not found in providers")
        elif not default_provider_config.enabled:
            warnings.append(f"Default provider '{self.default_provider}' is disabled")

        # Check for duplicate provider priorities
        priorities = [p.priority for p in enabled_providers]
        if len(priorities) != len(set(priorities)):
            warnings.append("Multiple providers have the same priority")

        # Check matching rules
        for rule in self.matching_rules:
            if rule.enabled:
                # Check if rule's provider exists
                provider = self.get_provider_config(rule.provider)
                if not provider:
                    issues.append(f"Matching rule '{rule.name}' references unknown provider '{rule.provider}'")
                elif not provider.enabled:
                    warnings.append(f"Matching rule '{rule.name}' references disabled provider '{rule.provider}'")

                # Check fallback provider
                if rule.fallback_provider:
                    fallback = self.get_provider_config(rule.fallback_provider)
                    if not fallback:
                        warnings.append(f"Matching rule '{rule.name}' references unknown fallback provider '{rule.fallback_provider}'")

        # Check cache configuration
        if self.cache.enabled:
            if self.cache.max_size < 1:
                issues.append("Cache max_size must be at least 1")
            if self.cache.ttl < 60:
                warnings.append("Cache TTL is very low (< 60 seconds)")

        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "warnings": warnings,
            "enabled_providers": len(enabled_providers),
            "total_providers": len(self.providers),
            "matching_rules": len([r for r in self.matching_rules if r.enabled]),
        }


def load_config(
    yaml_path: Optional[str] = None, env_file: Optional[str] = None
) -> AppConfig:
    """
    Load configuration from various sources.

    Priority (highest to lowest):
    1. YAML file (if provided)
    2. Environment variables
    3. .env file
    4. Defaults

    Args:
        yaml_path: Optional path to YAML configuration file
        env_file: Optional path to .env file

    Returns:
        AppConfig instance

    Examples:
        >>> # Load from defaults and environment
        >>> config = load_config()

        >>> # Load from YAML
        >>> config = load_config(yaml_path="config.yaml")

        >>> # Load from custom .env
        >>> config = load_config(env_file="custom.env")
    """
    if yaml_path:
        return AppConfig.from_yaml(yaml_path)

    if env_file:
        return AppConfig(_env_file=env_file)

    return AppConfig()


def create_default_config() -> AppConfig:
    """
    Create a default configuration with sensible defaults.

    Returns:
        AppConfig instance with default settings

    Examples:
        >>> config = create_default_config()
        >>> config.to_yaml("config.yaml")
    """
    from geoip_geocode.matching import create_default_rules

    return AppConfig(
        default_provider="geoip2",
        locales=["en"],
        cache=CacheConfig(
            enabled=True,
            backend="lru",
            max_size=100000,
            ttl=3600,
        ),
        matching_rules=create_default_rules(),
        providers=[
            ProviderConfig(
                name="geoip2",
                enabled=True,
                priority=100,
                description="MaxMind GeoIP2 / GeoLite2 database provider",
                timeout=30,
                max_retries=3,
            ),
        ],
    )
