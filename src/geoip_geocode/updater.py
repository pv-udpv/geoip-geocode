"""
Database updater utilities for downloading and managing GeoIP databases.

This module provides functionality to download and update GeoIP2/GeoLite2
and IP2Location databases from their respective sources.
"""

import os
import shutil
import tarfile
from pathlib import Path
from typing import Optional

import requests
from rich.console import Console
from rich.progress import (
    BarColumn,
    DownloadColumn,
    Progress,
    TextColumn,
    TimeRemainingColumn,
    TransferSpeedColumn,
)

console = Console()


class MaxMindUpdater:
    """
    Updater for MaxMind GeoIP2/GeoLite2 databases.

    Downloads databases from MaxMind using either:
    - GeoLite2 (free, requires license key)
    - GeoIP2 (paid, requires license key and account ID)

    Environment variables:
        MAXMIND_LICENSE_KEY: Your MaxMind license key (required)
        MAXMIND_ACCOUNT_ID: Your MaxMind account ID (optional, for GeoIP2)
        MAXMIND_EDITION_ID: Database edition (default: GeoLite2-City)
    """

    BASE_URL = "https://download.maxmind.com/app/geoip_download"
    DEFAULT_EDITION = "GeoLite2-City"

    def __init__(
        self,
        license_key: Optional[str] = None,
        account_id: Optional[str] = None,
        output_dir: Optional[str] = None,
    ):
        """
        Initialize MaxMind updater.

        Args:
            license_key: MaxMind license key (or from MAXMIND_LICENSE_KEY env)
            account_id: MaxMind account ID (or from MAXMIND_ACCOUNT_ID env)
            output_dir: Directory to save databases (default: ./data/databases)
        """
        self.license_key = license_key or os.getenv("MAXMIND_LICENSE_KEY")
        self.account_id = account_id or os.getenv("MAXMIND_ACCOUNT_ID")
        self.output_dir = Path(output_dir or "./data/databases")
        self.output_dir.mkdir(parents=True, exist_ok=True)

        if not self.license_key:
            raise ValueError(
                "MaxMind license key is required. "
                "Set MAXMIND_LICENSE_KEY environment variable "
                "or pass license_key parameter."
            )

    def download_database(
        self, edition_id: Optional[str] = None, suffix: str = "tar.gz"
    ) -> Optional[Path]:
        """
        Download a MaxMind database.

        Args:
            edition_id: Database edition (e.g., 'GeoLite2-City', 'GeoLite2-ASN')
            suffix: File suffix (tar.gz or zip)

        Returns:
            Path to downloaded database file, or None if failed

        Examples:
            >>> updater = MaxMindUpdater(license_key="your_key")
            >>> db_path = updater.download_database("GeoLite2-City")
        """
        edition_id = edition_id or self.DEFAULT_EDITION

        # Build download URL
        params = {
            "edition_id": edition_id,
            "license_key": self.license_key,
            "suffix": suffix,
        }

        console.print(f"[cyan]Downloading {edition_id}...[/cyan]")

        try:
            # Download with progress bar
            response = requests.get(
                self.BASE_URL, params=params, stream=True, timeout=30
            )
            response.raise_for_status()

            # Save to temporary file
            temp_file = self.output_dir / f"{edition_id}.{suffix}"
            total_size = int(response.headers.get("content-length", 0))

            with Progress(
                TextColumn("[bold blue]{task.description}"),
                BarColumn(),
                DownloadColumn(),
                TransferSpeedColumn(),
                TimeRemainingColumn(),
            ) as progress:
                task = progress.add_task(f"Downloading {edition_id}", total=total_size)

                with open(temp_file, "wb") as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                            progress.update(task, advance=len(chunk))

            # Extract database file
            db_file = self._extract_database(temp_file, edition_id)

            # Clean up temp file
            temp_file.unlink()

            if db_file:
                console.print(f"[green]✓[/green] Downloaded {edition_id} to {db_file}")
                return db_file
            else:
                console.print(f"[red]✗[/red] Failed to extract {edition_id}")
                return None

        except requests.RequestException as e:
            console.print(f"[red]✗[/red] Download failed: {e}")
            return None
        except Exception as e:
            console.print(f"[red]✗[/red] Error: {e}")
            return None

    def _extract_database(self, archive_path: Path, edition_id: str) -> Optional[Path]:
        """
        Extract .mmdb file from downloaded archive.

        Args:
            archive_path: Path to downloaded archive
            edition_id: Database edition ID

        Returns:
            Path to extracted .mmdb file
        """
        try:
            with tarfile.open(archive_path, "r:gz") as tar:
                # Find .mmdb file in archive
                mmdb_members = [m for m in tar.getmembers() if m.name.endswith(".mmdb")]

                if not mmdb_members:
                    console.print("[red]✗[/red] No .mmdb file found in archive")
                    return None

                # Extract the .mmdb file
                mmdb_member = mmdb_members[0]
                tar.extract(mmdb_member, path=self.output_dir)

                # Move to final location
                extracted_path = self.output_dir / mmdb_member.name
                final_path = self.output_dir / f"{edition_id}.mmdb"

                if extracted_path.exists():
                    shutil.move(str(extracted_path), str(final_path))

                    # Clean up extracted directory
                    parent_dir = extracted_path.parent
                    if parent_dir != self.output_dir and parent_dir.exists():
                        shutil.rmtree(parent_dir)

                    return final_path

                return None

        except Exception as e:
            console.print(f"[red]✗[/red] Extraction failed: {e}")
            return None

    def update_all(self) -> dict[str, Optional[Path]]:
        """
        Update all common GeoLite2 databases.

        Returns:
            Dictionary mapping edition IDs to downloaded file paths

        Examples:
            >>> updater = MaxMindUpdater(license_key="your_key")
            >>> results = updater.update_all()
            >>> print(results["GeoLite2-City"])
        """
        editions = ["GeoLite2-City", "GeoLite2-Country", "GeoLite2-ASN"]
        results = {}

        console.print("[bold cyan]Updating MaxMind databases...[/bold cyan]")

        for edition in editions:
            results[edition] = self.download_database(edition)

        console.print(
            f"[green]✓[/green] Updated {sum(1 for v in results.values() if v)} "
            f"of {len(editions)} databases"
        )

        return results


class IP2LocationUpdater:
    """
    Updater for IP2Location databases.

    Downloads databases from IP2Location using either:
    - Lite version (free, requires token)
    - Commercial version (paid, requires token)

    Environment variables:
        IP2LOCATION_TOKEN: Your IP2Location download token (required)
        IP2LOCATION_PRODUCT_CODE: Product code (default: DB11LITE)
    """

    BASE_URL = "https://www.ip2location.com/download/"
    DEFAULT_PRODUCT = "DB11LITE"

    def __init__(self, token: Optional[str] = None, output_dir: Optional[str] = None):
        """
        Initialize IP2Location updater.

        Args:
            token: IP2Location download token (or from IP2LOCATION_TOKEN env)
            output_dir: Directory to save databases (default: ./data/databases)
        """
        self.token = token or os.getenv("IP2LOCATION_TOKEN")
        self.output_dir = Path(output_dir or "./data/databases")
        self.output_dir.mkdir(parents=True, exist_ok=True)

        if not self.token:
            raise ValueError(
                "IP2Location token is required. "
                "Set IP2LOCATION_TOKEN environment variable or pass token parameter."
            )

    def download_database(self, product_code: Optional[str] = None) -> Optional[Path]:
        """
        Download an IP2Location database.

        Args:
            product_code: Product code (e.g., 'DB11LITE', 'DB11')

        Returns:
            Path to downloaded database file, or None if failed

        Examples:
            >>> updater = IP2LocationUpdater(token="your_token")
            >>> db_path = updater.download_database("DB11LITE")
        """
        product_code = product_code or self.DEFAULT_PRODUCT

        console.print(f"[cyan]Downloading IP2Location {product_code}...[/cyan]")

        try:
            # Build download URL
            url = f"{self.BASE_URL}?token={self.token}&file={product_code}"

            # Download with progress bar
            response = requests.get(url, stream=True, timeout=30)
            response.raise_for_status()

            # Save to file
            temp_file = self.output_dir / f"{product_code}.BIN.zip"
            total_size = int(response.headers.get("content-length", 0))

            with Progress(
                TextColumn("[bold blue]{task.description}"),
                BarColumn(),
                DownloadColumn(),
                TransferSpeedColumn(),
                TimeRemainingColumn(),
            ) as progress:
                task = progress.add_task(
                    f"Downloading {product_code}", total=total_size
                )

                with open(temp_file, "wb") as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                            progress.update(task, advance=len(chunk))

            # Extract database
            db_file = self._extract_database(temp_file, product_code)

            # Clean up temp file
            if temp_file.exists():
                temp_file.unlink()

            if db_file:
                console.print(
                    f"[green]✓[/green] Downloaded {product_code} to {db_file}"
                )
                return db_file
            else:
                console.print(f"[red]✗[/red] Failed to extract {product_code}")
                return None

        except requests.RequestException as e:
            console.print(f"[red]✗[/red] Download failed: {e}")
            return None
        except Exception as e:
            console.print(f"[red]✗[/red] Error: {e}")
            return None

    def _extract_database(
        self, archive_path: Path, product_code: str
    ) -> Optional[Path]:
        """
        Extract .BIN file from downloaded archive.

        Args:
            archive_path: Path to downloaded archive
            product_code: Product code

        Returns:
            Path to extracted .BIN file
        """
        try:
            import zipfile

            with zipfile.ZipFile(archive_path, "r") as zip_ref:
                # Find .BIN file in archive
                bin_files = [f for f in zip_ref.namelist() if f.endswith(".BIN")]

                if not bin_files:
                    console.print("[red]✗[/red] No .BIN file found in archive")
                    return None

                # Extract the .BIN file
                bin_file = bin_files[0]
                zip_ref.extract(bin_file, path=self.output_dir)

                # Move to final location
                extracted_path = self.output_dir / bin_file
                final_path = self.output_dir / f"{product_code}.BIN"

                if extracted_path.exists():
                    shutil.move(str(extracted_path), str(final_path))
                    return final_path

                return None

        except Exception as e:
            console.print(f"[red]✗[/red] Extraction failed: {e}")
            return None


def update_databases(provider_type: str = "maxmind") -> bool:
    """
    Update databases for specified provider type.

    Args:
        provider_type: Provider type ('maxmind' or 'ip2location')

    Returns:
        True if update was successful, False otherwise

    Examples:
        >>> # Update MaxMind databases
        >>> update_databases("maxmind")

        >>> # Update IP2Location databases
        >>> update_databases("ip2location")
    """
    try:
        if provider_type.lower() == "maxmind":
            updater = MaxMindUpdater()
            results = updater.update_all()
            return any(results.values())

        elif provider_type.lower() == "ip2location":
            updater = IP2LocationUpdater()
            result = updater.download_database()
            return result is not None

        else:
            console.print(f"[red]✗[/red] Unknown provider type: {provider_type}")
            return False

    except ValueError as e:
        console.print(f"[red]✗[/red] Configuration error: {e}")
        return False
    except Exception as e:
        console.print(f"[red]✗[/red] Update failed: {e}")
        return False
