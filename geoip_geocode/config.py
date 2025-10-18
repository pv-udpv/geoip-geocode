"""
Configuration management for geoip-geocode.

Supports loading configuration from environment variables, .env files,
and YAML files using Pydantic settings.
"""

from pathlib import Path
from typing import List, Optional

import yaml
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from geoip_geocode.models import ProviderConfig


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
        cache_enabled: Whether to enable caching
        cache_ttl: Cache time-to-live in seconds
        providers: List of provider configurations

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
    )

    config_file: Optional[str] = Field(
        None, description="Path to YAML configuration file"
    )
    default_provider: str = Field("geoip2", description="Default provider to use")
    cache_enabled: bool = Field(False, description="Enable result caching")
    cache_ttl: int = Field(3600, description="Cache TTL in seconds")
    providers: List[ProviderConfig] = Field(
        default_factory=list, description="Provider configurations"
    )

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

        # Convert provider configs if present
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
        data = self.model_dump(exclude_none=True)

        # Convert provider configs to dicts
        if "providers" in data:
            data["providers"] = [
                p if isinstance(p, dict) else p.model_dump(exclude_none=True)
                for p in data["providers"]
            ]

        yaml_file = Path(yaml_path)
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
