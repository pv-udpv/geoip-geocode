"""
Matching rules engine for provider selection.

This module provides a flexible rule-based system for automatically selecting
the appropriate provider based on IP address characteristics, geographic location,
or custom conditions.
"""

import ipaddress
import re
from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, Field


class MatchType(str, Enum):
    """Types of matching conditions."""

    IP_RANGE = "ip_range"  # Match IP address range (CIDR)
    IP_VERSION = "ip_version"  # Match IPv4 or IPv6
    COUNTRY = "country"  # Match country code
    CONTINENT = "continent"  # Match continent code
    ASN = "asn"  # Match Autonomous System Number
    REGEX = "regex"  # Match IP with regex pattern
    CUSTOM = "custom"  # Custom matching function


class MatchCondition(BaseModel):
    """
    A single matching condition.

    Attributes:
        type: Type of matching condition
        values: Values to match against (depends on type)
        negate: Whether to negate the match result
    """

    type: MatchType
    values: list[str] = Field(default_factory=list)
    negate: bool = False

    def matches(self, ip_address: str, geo_data: Optional[Any] = None) -> bool:
        """
        Check if the condition matches.

        Args:
            ip_address: IP address to check
            geo_data: Optional geographic data for context-based matching

        Returns:
            True if condition matches, False otherwise
        """
        try:
            if self.type == MatchType.IP_RANGE:
                result = self._match_ip_range(ip_address)
            elif self.type == MatchType.IP_VERSION:
                result = self._match_ip_version(ip_address)
            elif self.type == MatchType.COUNTRY:
                result = self._match_country(geo_data)
            elif self.type == MatchType.CONTINENT:
                result = self._match_continent(geo_data)
            elif self.type == MatchType.ASN:
                result = self._match_asn(geo_data)
            elif self.type == MatchType.REGEX:
                result = self._match_regex(ip_address)
            else:
                result = False

            return not result if self.negate else result

        except Exception:
            return False

    def _match_ip_range(self, ip_address: str) -> bool:
        """Match IP against CIDR ranges."""
        try:
            ip = ipaddress.ip_address(ip_address)
            for cidr in self.values:
                network = ipaddress.ip_network(cidr, strict=False)
                if ip in network:
                    return True
            return False
        except ValueError:
            return False

    def _match_ip_version(self, ip_address: str) -> bool:
        """Match IP version (4 or 6)."""
        try:
            ip = ipaddress.ip_address(ip_address)
            version = str(ip.version)
            return version in self.values
        except ValueError:
            return False

    def _match_country(self, geo_data: Optional[Any]) -> bool:
        """Match country code."""
        if not geo_data or not hasattr(geo_data, "country_code"):
            return False
        return geo_data.country_code in self.values

    def _match_continent(self, geo_data: Optional[Any]) -> bool:
        """Match continent code."""
        if not geo_data or not hasattr(geo_data, "continent_code"):
            return False
        return geo_data.continent_code in self.values

    def _match_asn(self, geo_data: Optional[Any]) -> bool:
        """Match ASN."""
        if not geo_data or not hasattr(geo_data, "asn"):
            return False
        return str(geo_data.asn) in self.values

    def _match_regex(self, ip_address: str) -> bool:
        """Match IP with regex pattern."""
        for pattern in self.values:
            if re.match(pattern, ip_address):
                return True
        return False


class MatchingRule(BaseModel):
    """
    A provider selection rule based on matching conditions.

    Attributes:
        name: Descriptive name for the rule
        description: Optional description
        enabled: Whether the rule is active
        priority: Rule priority (lower = higher priority)
        conditions: List of conditions (all must match by default)
        match_all: If True, all conditions must match; if False, any condition
        provider: Provider name to use when rule matches
        fallback_provider: Optional fallback provider
    """

    name: str
    description: Optional[str] = None
    enabled: bool = True
    priority: int = 100
    conditions: list[MatchCondition] = Field(default_factory=list)
    match_all: bool = True  # AND logic if True, OR logic if False
    provider: str
    fallback_provider: Optional[str] = None

    def matches(self, ip_address: str, geo_data: Optional[Any] = None) -> bool:
        """
        Check if all rule conditions match.

        Args:
            ip_address: IP address to check
            geo_data: Optional geographic data for context-based matching

        Returns:
            True if rule matches, False otherwise
        """
        if not self.enabled:
            return False

        if not self.conditions:
            return False

        if self.match_all:
            # ALL conditions must match (AND logic)
            return all(
                condition.matches(ip_address, geo_data) for condition in self.conditions
            )
        else:
            # ANY condition must match (OR logic)
            return any(
                condition.matches(ip_address, geo_data) for condition in self.conditions
            )


class MatchingEngine:
    """
    Engine for evaluating matching rules and selecting providers.

    Attributes:
        rules: List of matching rules, sorted by priority
    """

    def __init__(self, rules: Optional[list[MatchingRule]] = None):
        """
        Initialize matching engine.

        Args:
            rules: List of matching rules
        """
        self.rules = rules or []
        self._sort_rules()

    def _sort_rules(self) -> None:
        """Sort rules by priority (lower priority number = higher priority)."""
        self.rules.sort(key=lambda r: r.priority)

    def add_rule(self, rule: MatchingRule) -> None:
        """
        Add a matching rule.

        Args:
            rule: Matching rule to add
        """
        self.rules.append(rule)
        self._sort_rules()

    def remove_rule(self, rule_name: str) -> bool:
        """
        Remove a matching rule by name.

        Args:
            rule_name: Name of rule to remove

        Returns:
            True if rule was removed, False if not found
        """
        initial_length = len(self.rules)
        self.rules = [r for r in self.rules if r.name != rule_name]
        return len(self.rules) < initial_length

    def find_provider(
        self, ip_address: str, geo_data: Optional[Any] = None
    ) -> Optional[str]:
        """
        Find the best matching provider for an IP address.

        Args:
            ip_address: IP address to check
            geo_data: Optional geographic data for context-based matching

        Returns:
            Provider name if a rule matches, None otherwise
        """
        for rule in self.rules:
            if rule.matches(ip_address, geo_data):
                return rule.provider

        return None

    def find_provider_with_fallback(
        self, ip_address: str, geo_data: Optional[Any] = None
    ) -> tuple[Optional[str], Optional[str]]:
        """
        Find provider with fallback option.

        Args:
            ip_address: IP address to check
            geo_data: Optional geographic data for context-based matching

        Returns:
            Tuple of (primary_provider, fallback_provider)
        """
        for rule in self.rules:
            if rule.matches(ip_address, geo_data):
                return (rule.provider, rule.fallback_provider)

        return (None, None)

    def get_matching_rules(
        self, ip_address: str, geo_data: Optional[Any] = None
    ) -> list[MatchingRule]:
        """
        Get all rules that match an IP address.

        Args:
            ip_address: IP address to check
            geo_data: Optional geographic data for context-based matching

        Returns:
            List of matching rules, sorted by priority
        """
        return [rule for rule in self.rules if rule.matches(ip_address, geo_data)]


def create_default_rules() -> list[MatchingRule]:
    """
    Create a set of default matching rules.

    Returns:
        List of default matching rules

    Examples:
        >>> rules = create_default_rules()
        >>> engine = MatchingEngine(rules)
        >>> provider = engine.find_provider("192.168.1.1")
    """
    return [
        # Private/Local IPs - use fastest local provider
        MatchingRule(
            name="private_networks",
            description="Private/internal IP addresses",
            priority=10,
            conditions=[
                MatchCondition(
                    type=MatchType.IP_RANGE,
                    values=[
                        "10.0.0.0/8",
                        "172.16.0.0/12",
                        "192.168.0.0/16",
                        "127.0.0.0/8",
                    ],
                )
            ],
            provider="geoip2",
        ),
        # IPv6 addresses
        MatchingRule(
            name="ipv6_addresses",
            description="IPv6 addresses",
            priority=20,
            conditions=[MatchCondition(type=MatchType.IP_VERSION, values=["6"])],
            provider="geoip2",
        ),
        # Asian countries - IP2Location has better coverage
        MatchingRule(
            name="asian_countries",
            description="Asian countries with better IP2Location coverage",
            priority=30,
            conditions=[
                MatchCondition(
                    type=MatchType.COUNTRY,
                    values=["CN", "JP", "KR", "IN", "ID", "TH", "VN", "PH", "MY"],
                )
            ],
            provider="ip2location",
            fallback_provider="geoip2",
        ),
        # European countries - MaxMind preferred
        MatchingRule(
            name="european_countries",
            description="European countries",
            priority=40,
            conditions=[
                MatchCondition(
                    type=MatchType.CONTINENT,
                    values=["EU"],
                )
            ],
            provider="geoip2",
        ),
    ]
