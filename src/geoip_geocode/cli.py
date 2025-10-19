"""
Command-line interface for geoip-geocode.

Provides commands for IP lookups, MMDB database updates, and provider management.
"""

from pathlib import Path
from typing import Optional

import typer
from rich import print as rprint
from rich.console import Console
from rich.table import Table

from geoip_geocode.config import AppConfig, load_config
from geoip_geocode.models import ProviderConfig
from geoip_geocode.providers import (
    GeoIP2Provider,
    IP2LocationProvider,
    MultiDatabaseGeoIP2Provider,
)
from geoip_geocode.registry import get_registry

app = typer.Typer(
    name="geoip-geocode",
    help="Geocoding and IP lookup tool with multiple provider support",
    add_completion=False,
)
console = Console()


@app.command()
def lookup(
    ip_address: str = typer.Argument(..., help="IP address to look up"),
    provider: Optional[str] = typer.Option(
        None, "--provider", "-p", help="Provider to use (default: from config)"
    ),
    config_file: Optional[str] = typer.Option(
        None, "--config", "-c", help="Path to configuration file"
    ),
    database: Optional[str] = typer.Option(
        None, "--database", "-d", help="Path to GeoIP2 database file"
    ),
) -> None:
    """
    Look up geographic information for an IP address.

    Examples:
        geoip-geocode lookup 8.8.8.8

        geoip-geocode lookup 8.8.8.8 --database /path/to/GeoLite2-City.mmdb

        geoip-geocode lookup 8.8.8.8 --config config.yaml --provider geoip2
    """
    try:
        # Load configuration
        config = load_config(yaml_path=config_file)

        # Determine provider to use
        provider_name = provider or config.default_provider

        # Get or create provider config
        provider_config = config.get_provider_config(provider_name)

        if not provider_config:
            # Create default config
            if provider_name == "geoip2":
                db_path = database or "./GeoLite2-City.mmdb"
                provider_config = ProviderConfig(
                    name="geoip2",
                    enabled=True,
                    database_path=db_path,
                )
            else:
                rprint(f"[red]Error: Unknown provider '{provider_name}'[/red]")
                raise typer.Exit(1)

        # Override database path if provided
        if database and provider_name == "geoip2":
            provider_config.database_path = database

        # Initialize registry and provider
        registry = get_registry()
        registry.register("geoip2", GeoIP2Provider)
        registry.register("ip2location", IP2LocationProvider)
        registry.register("geoip2-multi", MultiDatabaseGeoIP2Provider)

        geo_provider = registry.get_provider(provider_name, provider_config)

        if not geo_provider:
            rprint(f"[red]Error: Failed to initialize provider '{provider_name}'[/red]")
            raise typer.Exit(1)

        if not geo_provider.is_available():
            rprint(f"[red]Error: Provider '{provider_name}' is not available[/red]")
            raise typer.Exit(1)

        # Perform lookup
        rprint(f"[cyan]Looking up {ip_address} using {provider_name}...[/cyan]")
        result = geo_provider.lookup(ip_address)

        if result:
            # Display results in a nice table
            table = Table(title=f"Geo Data for {ip_address}")
            table.add_column("Field", style="cyan")
            table.add_column("Value", style="green")

            table.add_row("GeoName ID", str(result.geoname_id))
            if result.country_name:
                table.add_row(
                    "Country", f"{result.country_name} ({result.country_code})"
                )
            if result.city:
                table.add_row("City", result.city)
            if result.subdivision:
                table.add_row(
                    "Subdivision", f"{result.subdivision} ({result.subdivision_code})"
                )
            if result.postal_code:
                table.add_row("Postal Code", result.postal_code)
            if result.latitude and result.longitude:
                table.add_row("Coordinates", f"{result.latitude}, {result.longitude}")
            if result.time_zone:
                table.add_row("Time Zone", result.time_zone)
            if result.accuracy_radius:
                table.add_row("Accuracy Radius", f"{result.accuracy_radius} km")
            table.add_row("Provider", result.provider or provider_name)

            console.print(table)
        else:
            rprint(f"[yellow]No data found for {ip_address}[/yellow]")

    except FileNotFoundError as e:
        rprint(f"[red]Error: {e}[/red]")
        rprint(
            "[yellow]Hint: Download GeoLite2 database using "
            "'geoip-geocode update-db'[/yellow]"
        )
        raise typer.Exit(1)
    except Exception as e:
        rprint(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)


@app.command()
def update_db(
    output_path: str = typer.Option(
        "./GeoLite2-City.mmdb",
        "--output",
        "-o",
        help="Output path for the database file",
    ),
    license_key: Optional[str] = typer.Option(
        None,
        "--license-key",
        "-k",
        help="MaxMind license key (or set MAXMIND_LICENSE_KEY env var)",
    ),
) -> None:
    """
    Download or update the GeoIP2/GeoLite2 database.

    Note: This requires a MaxMind license key. You can get a free key at:
    https://www.maxmind.com/en/geolite2/signup

    Examples:
        geoip-geocode update-db --license-key YOUR_KEY

        geoip-geocode update-db --output /usr/share/GeoIP/GeoLite2-City.mmdb
    """
    import os

    # Get license key from option or environment
    key = license_key or os.getenv("MAXMIND_LICENSE_KEY")

    if not key:
        rprint("[red]Error: MaxMind license key required[/red]")
        rprint(
            "[yellow]Get a free key at: "
            "https://www.maxmind.com/en/geolite2/signup[/yellow]"
        )
        rprint(
            "[yellow]Then use --license-key option or set "
            "MAXMIND_LICENSE_KEY env var[/yellow]"
        )
        raise typer.Exit(1)

    rprint(
        "[cyan]Note: MaxMind now requires manual download of GeoLite2 databases.[/cyan]"
    )
    rprint(
        "[yellow]Please visit: https://dev.maxmind.com/geoip/geolite2-free-geolocation-data[/yellow]"
    )
    rprint(
        f"[yellow]Download GeoLite2-City.mmdb and save it to: {output_path}[/yellow]"
    )
    rprint(f"[yellow]Your license key: {key}[/yellow]")


@app.command()
def list_providers(
    config_file: Optional[str] = typer.Option(
        None, "--config", "-c", help="Path to configuration file"
    ),
) -> None:
    """
    List all available providers and their status.

    Examples:
        geoip-geocode list-providers

        geoip-geocode list-providers --config config.yaml
    """
    try:
        config = load_config(yaml_path=config_file)

        # Initialize registry
        registry = get_registry()
        registry.register("geoip2", GeoIP2Provider)
        registry.register("ip2location", IP2LocationProvider)
        registry.register("geoip2-multi", MultiDatabaseGeoIP2Provider)

        # Create table
        table = Table(title="Available Providers")
        table.add_column("Provider", style="cyan")
        table.add_column("Status", style="green")
        table.add_column("Priority", style="yellow")
        table.add_column("Details", style="white")

        # Show registered providers
        for provider_name in registry.list_providers():
            provider_config = config.get_provider_config(provider_name)

            if provider_config:
                status = "✓ Enabled" if provider_config.enabled else "✗ Disabled"
                priority = str(provider_config.priority)
                details = ""

                if provider_config.database_path:
                    db_exists = Path(provider_config.database_path).exists()
                    status_icon = "✓" if db_exists else "✗"
                    details = f"DB: {provider_config.database_path} {status_icon}"
                elif provider_config.api_key:
                    details = "API Key configured"

                table.add_row(provider_name, status, priority, details)
            else:
                table.add_row(provider_name, "Not configured", "-", "")

        console.print(table)

        if config.providers:
            rprint(f"\n[cyan]Default provider: {config.default_provider}[/cyan]")
        else:
            rprint(
                "\n[yellow]No providers configured. "
                "Use 'config init' to create a configuration.[/yellow]"
            )

    except Exception as e:
        rprint(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)


# Configuration management commands
config_app = typer.Typer(help="Configuration management commands")
app.add_typer(config_app, name="config")

@config_app.command("init")
def config_init(
    output: str = typer.Option(
        "config.yaml", "--output", "-o", help="Output configuration file path"
    ),
    template: str = typer.Option(
        "standard", "--template", "-t", help="Template: minimal, standard, or full"
    ),
    database_path: Optional[str] = typer.Option(
        None, "--database", "-d", help="Path to GeoIP2 database"
    ),
) -> None:
    """
    Initialize a configuration file with default settings.

    Examples:
        geoip-geocode config init

        geoip-geocode config init --template full

        geoip-geocode config init --database /path/to/GeoLite2-City.mmdb
    """
    try:
        from geoip_geocode.config import create_default_config

        # Create default configuration
        config = create_default_config()

        # Override database path if provided
        if database_path:
            for provider in config.providers:
                if provider.name == "geoip2":
                    provider.database_path = database_path

        # Save to file
        config.to_yaml(output)

        rprint(f"[green]✓ Configuration file created: {output}[/green]")
        rprint(f"[cyan]Template: {template}[/cyan]")
        rprint("[yellow]Edit the file to customize settings[/yellow]")

    except Exception as e:
        rprint(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)

@config_app.command("validate")
def config_validate(
    config_file: str = typer.Option(
        "config.yaml", "--config", "-c", help="Path to configuration file"
    ),
) -> None:
    """
    Validate a configuration file.

    Examples:
        geoip-geocode config validate

        geoip-geocode config validate --config config/config.yaml
    """
    try:
        config = load_config(yaml_path=config_file)
        results = config.validate_config()

        if results["valid"]:
            rprint("[green]✓ Configuration is valid[/green]")
        else:
            rprint("[red]✗ Configuration has issues[/red]")

        # Show statistics
        table = Table(title="Configuration Summary")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="green")

        table.add_row("Enabled Providers", str(results["enabled_providers"]))
        table.add_row("Total Providers", str(results["total_providers"]))
        table.add_row("Matching Rules", str(results["matching_rules"]))

        console.print(table)

        # Show issues
        if results["issues"]:
            rprint("\n[red bold]Issues:[/red bold]")
            for issue in results["issues"]:
                rprint(f"[red]  ✗ {issue}[/red]")

        # Show warnings
        if results["warnings"]:
            rprint("\n[yellow bold]Warnings:[/yellow bold]")
            for warning in results["warnings"]:
                rprint(f"[yellow]  ⚠ {warning}[/yellow]")

        if not results["valid"]:
            raise typer.Exit(1)

    except FileNotFoundError:
        rprint(f"[red]Error: Configuration file not found: {config_file}[/red]")
        raise typer.Exit(1)
    except Exception as e:
        rprint(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)

@config_app.command("show")
def config_show(
    config_file: str = typer.Option(
        "config.yaml", "--config", "-c", help="Path to configuration file"
    ),
    section: Optional[str] = typer.Option(
        None, "--section", "-s", help="Show specific section (providers, cache, rules)"
    ),
) -> None:
    """
    Display current configuration.

    Examples:
        geoip-geocode config show

        geoip-geocode config show --section providers

        geoip-geocode config show --section cache
    """
    try:
        config = load_config(yaml_path=config_file)

        if section == "providers":
            # Show providers table
            table = Table(title="Providers Configuration")
            table.add_column("Name", style="cyan")
            table.add_column("Enabled", style="green")
            table.add_column("Priority", style="yellow")
            table.add_column("Database", style="white")

            for provider in config.providers:
                enabled = "✓" if provider.enabled else "✗"
                db_path = provider.database_path or "-"
                table.add_row(
                    provider.name,
                    enabled,
                    str(provider.priority),
                    db_path[:50] + "..." if len(db_path) > 50 else db_path,
                )

            console.print(table)

        elif section == "cache":
            # Show cache config
            table = Table(title="Cache Configuration")
            table.add_column("Setting", style="cyan")
            table.add_column("Value", style="green")

            table.add_row("Enabled", "✓" if config.cache.enabled else "✗")
            table.add_row("Backend", config.cache.backend)
            table.add_row("Max Size", str(config.cache.max_size))
            table.add_row("TTL", f"{config.cache.ttl}s")

            console.print(table)

        elif section == "rules":
            # Show matching rules
            table = Table(title="Matching Rules")
            table.add_column("Name", style="cyan")
            table.add_column("Enabled", style="green")
            table.add_column("Priority", style="yellow")
            table.add_column("Provider", style="white")

            for rule in config.matching_rules:
                enabled = "✓" if rule.enabled else "✗"
                table.add_row(
                    rule.name,
                    enabled,
                    str(rule.priority),
                    rule.provider,
                )

            console.print(table)

        else:
            # Show overview
            rprint(f"[cyan bold]Configuration Overview[/cyan bold]")
            rprint(f"Default Provider: [green]{config.default_provider}[/green]")
            rprint(f"Locales: [green]{', '.join(config.locales)}[/green]")
            rprint(f"Cache: [green]{'Enabled' if config.cache.enabled else 'Disabled'}[/green]")
            rprint(f"Providers: [green]{len(config.providers)}[/green]")
            rprint(f"Matching Rules: [green]{len(config.matching_rules)}[/green]")

            if config.logging:
                rprint(f"Logging: [green]{config.logging.level}[/green]")

    except FileNotFoundError:
        rprint(f"[red]Error: Configuration file not found: {config_file}[/red]")
        raise typer.Exit(1)
    except Exception as e:
        rprint(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)

@config_app.command("check")
def config_check(
    config_file: str = typer.Option(
        "config.yaml", "--config", "-c", help="Path to configuration file"
    ),
) -> None:
    """
    Check provider availability and database files.

    Examples:
        geoip-geocode config check

        geoip-geocode config check --config config/config.yaml
    """
    try:
        config = load_config(yaml_path=config_file)

        # Initialize registry
        registry = get_registry()
        registry.register("geoip2", GeoIP2Provider)
        registry.register("ip2location", IP2LocationProvider)
        registry.register("geoip2-multi", MultiDatabaseGeoIP2Provider)

        # Check each provider
        table = Table(title="Provider Status Check")
        table.add_column("Provider", style="cyan")
        table.add_column("Enabled", style="green")
        table.add_column("Available", style="yellow")
        table.add_column("Details", style="white")

        for provider_config in config.providers:
            enabled = "✓" if provider_config.enabled else "✗"
            
            if provider_config.enabled:
                try:
                    provider = registry.get_provider(
                        provider_config.name, provider_config
                    )
                    if provider and provider.is_available():
                        available = "✓"
                        details = "Ready"
                    else:
                        available = "✗"
                        details = "Not available"
                except Exception as e:
                    available = "✗"
                    details = str(e)[:50]
            else:
                available = "-"
                details = "Disabled"

            table.add_row(
                provider_config.name,
                enabled,
                available,
                details,
            )

        console.print(table)

        # Validate config
        results = config.validate_config()
        if results["issues"]:
            rprint("\n[red bold]Configuration Issues:[/red bold]")
            for issue in results["issues"]:
                rprint(f"[red]  ✗ {issue}[/red]")

    except FileNotFoundError:
        rprint(f"[red]Error: Configuration file not found: {config_file}[/red]")
        raise typer.Exit(1)
    except Exception as e:
        rprint(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)


@app.command()
def version() -> None:
    """Show version information."""
    from geoip_geocode import __version__

    rprint(f"[cyan]geoip-geocode version {__version__}[/cyan]")


if __name__ == "__main__":
    app()
