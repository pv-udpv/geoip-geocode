"""
Example 08: Matching Rules

This example demonstrates how to use matching rules to automatically
select the appropriate provider based on IP characteristics.

Matching rules allow you to:
- Route different IP ranges to different providers
- Use specialized providers for specific regions
- Implement fallback strategies
- Optimize provider selection based on context
"""

from geoip_geocode.matching import (
    MatchCondition,
    MatchingEngine,
    MatchingRule,
    MatchType,
    create_default_rules,
)
from geoip_geocode.models import GeoData


def example_basic_matching():
    """Basic matching rules example."""
    print("=" * 60)
    print("Basic Matching Rules Example")
    print("=" * 60)

    # Create a simple rule for private IPs
    rule = MatchingRule(
        name="private_ips",
        description="Route private IPs to local provider",
        priority=10,
        conditions=[
            MatchCondition(
                type=MatchType.IP_RANGE,
                values=["192.168.0.0/16", "10.0.0.0/8"],
            )
        ],
        provider="geoip2",
    )

    # Create matching engine
    engine = MatchingEngine(rules=[rule])

    # Test various IPs
    test_ips = [
        "192.168.1.1",  # Should match private rule
        "10.0.0.1",  # Should match private rule
        "8.8.8.8",  # Should not match
    ]

    print("\nTesting IP matching:")
    for ip in test_ips:
        provider = engine.find_provider(ip)
        if provider:
            print(f"  {ip:20s} → {provider}")
        else:
            print(f"  {ip:20s} → No match")


def example_ip_version_matching():
    """Match based on IP version (IPv4 vs IPv6)."""
    print("\n" + "=" * 60)
    print("IP Version Matching Example")
    print("=" * 60)

    # Rule for IPv6
    ipv6_rule = MatchingRule(
        name="ipv6_traffic",
        description="Use specialized provider for IPv6",
        priority=10,
        conditions=[MatchCondition(type=MatchType.IP_VERSION, values=["6"])],
        provider="geoip2-ipv6",
    )

    # Rule for IPv4
    ipv4_rule = MatchingRule(
        name="ipv4_traffic",
        description="Standard provider for IPv4",
        priority=20,
        conditions=[MatchCondition(type=MatchType.IP_VERSION, values=["4"])],
        provider="geoip2",
    )

    engine = MatchingEngine(rules=[ipv6_rule, ipv4_rule])

    test_ips = [
        "8.8.8.8",  # IPv4
        "2001:4860:4860::8888",  # IPv6 (Google DNS)
        "192.168.1.1",  # IPv4
        "2a00:1450:4001:800::200e",  # IPv6
    ]

    print("\nTesting IP version matching:")
    for ip in test_ips:
        provider = engine.find_provider(ip)
        print(f"  {ip:35s} → {provider}")


def example_geographic_matching():
    """Match based on geographic location."""
    print("\n" + "=" * 60)
    print("Geographic Matching Example")
    print("=" * 60)

    # Rule for Asian countries
    asian_rule = MatchingRule(
        name="asian_countries",
        description="IP2Location has better Asian coverage",
        priority=10,
        conditions=[
            MatchCondition(
                type=MatchType.COUNTRY,
                values=["CN", "JP", "KR", "IN"],
            )
        ],
        provider="ip2location",
        fallback_provider="geoip2",
    )

    # Rule for European countries
    european_rule = MatchingRule(
        name="european_countries",
        description="MaxMind preferred for Europe",
        priority=20,
        conditions=[MatchCondition(type=MatchType.CONTINENT, values=["EU"])],
        provider="geoip2",
    )

    engine = MatchingEngine(rules=[asian_rule, european_rule])

    # Create mock geo data
    test_cases = [
        ("1.2.3.4", GeoData(geoname_id=1, country_code="CN", ip_address="1.2.3.4")),
        ("5.6.7.8", GeoData(geoname_id=2, country_code="JP", ip_address="5.6.7.8")),
        (
            "9.10.11.12",
            GeoData(
                geoname_id=3,
                country_code="DE",
                continent_code="EU",
                ip_address="9.10.11.12",
            ),
        ),
    ]

    print("\nTesting geographic matching:")
    for ip, geo_data in test_cases:
        provider = engine.find_provider(ip, geo_data)
        country = geo_data.country_code
        print(f"  {ip:20s} ({country:2s}) → {provider}")


def example_complex_rules():
    """Complex matching with multiple conditions."""
    print("\n" + "=" * 60)
    print("Complex Matching Rules Example")
    print("=" * 60)

    # Rule: European IPv6 addresses
    rule = MatchingRule(
        name="eu_ipv6",
        description="European IPv6 traffic",
        priority=10,
        match_all=True,  # AND logic: both conditions must match
        conditions=[
            MatchCondition(type=MatchType.IP_VERSION, values=["6"]),
            MatchCondition(type=MatchType.CONTINENT, values=["EU"]),
        ],
        provider="geoip2-eu-ipv6",
    )

    engine = MatchingEngine(rules=[rule])

    # Test cases
    test_cases = [
        (
            "2001:4860:4860::8888",
            GeoData(
                geoname_id=1,
                continent_code="EU",
                ip_address="2001:4860:4860::8888",
            ),
        ),  # Matches
        (
            "8.8.8.8",
            GeoData(geoname_id=2, continent_code="EU", ip_address="8.8.8.8"),
        ),  # No match (IPv4)
        (
            "2001:4860:4860::8888",
            GeoData(
                geoname_id=3,
                continent_code="NA",
                ip_address="2001:4860:4860::8888",
            ),
        ),  # No match (not EU)
    ]

    print("\nTesting complex rules (IPv6 AND Europe):")
    for ip, geo_data in test_cases:
        provider = engine.find_provider(ip, geo_data)
        continent = geo_data.continent_code or "N/A"
        if provider:
            print(f"  {ip:35s} ({continent:2s}) → {provider}")
        else:
            print(f"  {ip:35s} ({continent:2s}) → No match")


def example_or_logic():
    """Match with OR logic (any condition matches)."""
    print("\n" + "=" * 60)
    print("OR Logic Matching Example")
    print("=" * 60)

    # Rule: High-priority IPs (CDN or private)
    rule = MatchingRule(
        name="priority_ips",
        description="CDN or private IPs",
        priority=10,
        match_all=False,  # OR logic: any condition matches
        conditions=[
            MatchCondition(type=MatchType.IP_RANGE, values=["192.168.0.0/16"]),
            MatchCondition(
                type=MatchType.ASN, values=["13335", "16509"]
            ),  # Cloudflare, AWS
        ],
        provider="fast-cache",
    )

    engine = MatchingEngine(rules=[rule])

    # Test with mock data
    test_cases = [
        ("192.168.1.1", None),  # Matches IP range
        (
            "1.1.1.1",
            GeoData(geoname_id=1, asn=13335, ip_address="1.1.1.1"),
        ),  # Matches ASN
        (
            "8.8.8.8",
            GeoData(geoname_id=2, asn=15169, ip_address="8.8.8.8"),
        ),  # No match
    ]

    print("\nTesting OR logic (private OR CDN):")
    for ip, geo_data in test_cases:
        provider = engine.find_provider(ip, geo_data)
        asn = f"ASN {geo_data.asn}" if geo_data and hasattr(geo_data, "asn") else "N/A"
        if provider:
            print(f"  {ip:20s} ({asn:10s}) → {provider}")
        else:
            print(f"  {ip:20s} ({asn:10s}) → No match")


def example_negation():
    """Match with negated conditions."""
    print("\n" + "=" * 60)
    print("Negation Example")
    print("=" * 60)

    # Rule: Non-private IPs
    rule = MatchingRule(
        name="public_ips",
        description="Public (non-private) IPs",
        priority=10,
        conditions=[
            MatchCondition(
                type=MatchType.IP_RANGE,
                values=["10.0.0.0/8", "192.168.0.0/16", "172.16.0.0/12"],
                negate=True,  # Match IPs NOT in these ranges
            )
        ],
        provider="public-provider",
    )

    engine = MatchingEngine(rules=[rule])

    test_ips = [
        "8.8.8.8",  # Should match (public)
        "192.168.1.1",  # Should not match (private)
        "10.0.0.1",  # Should not match (private)
        "1.1.1.1",  # Should match (public)
    ]

    print("\nTesting negation (NOT private):")
    for ip in test_ips:
        provider = engine.find_provider(ip)
        if provider:
            print(f"  {ip:20s} → {provider}")
        else:
            print(f"  {ip:20s} → No match (private IP)")


def example_default_rules():
    """Use predefined default rules."""
    print("\n" + "=" * 60)
    print("Default Rules Example")
    print("=" * 60)

    # Create engine with default rules
    rules = create_default_rules()
    engine = MatchingEngine(rules=rules)

    print(f"\nLoaded {len(rules)} default rules:")
    for rule in rules:
        status = "✓" if rule.enabled else "✗"
        print(f"  {status} [{rule.priority:3d}] {rule.name:25s} → {rule.provider}")

    # Test some IPs
    test_ips = [
        "192.168.1.1",
        "8.8.8.8",
        "2001:4860:4860::8888",
    ]

    print("\nTesting with default rules:")
    for ip in test_ips:
        provider = engine.find_provider(ip)
        if provider:
            print(f"  {ip:35s} → {provider}")
        else:
            print(f"  {ip:35s} → No match (use default_provider)")


def example_fallback():
    """Provider selection with fallback."""
    print("\n" + "=" * 60)
    print("Fallback Provider Example")
    print("=" * 60)

    rule = MatchingRule(
        name="experimental",
        description="Experimental provider with fallback",
        priority=10,
        conditions=[MatchCondition(type=MatchType.IP_RANGE, values=["8.8.0.0/16"])],
        provider="experimental-provider",
        fallback_provider="geoip2",
    )

    engine = MatchingEngine(rules=[rule])

    test_ips = ["8.8.8.8", "1.1.1.1"]

    print("\nTesting with fallback:")
    for ip in test_ips:
        primary, fallback = engine.find_provider_with_fallback(ip)
        if primary:
            print(f"  {ip:20s} → Primary: {primary}")
            if fallback:
                print(f"  {'':<20s}   Fallback: {fallback}")
        else:
            print(f"  {ip:20s} → No match")


if __name__ == "__main__":
    print("\n🎯 GeoIP Matching Rules Examples\n")

    # Run examples
    example_basic_matching()
    example_ip_version_matching()
    example_geographic_matching()
    example_complex_rules()
    example_or_logic()
    example_negation()
    example_default_rules()
    example_fallback()

    print("\n" + "=" * 60)
    print("✨ All examples completed!")
    print("=" * 60)
    print("\nSee config/config.yaml.example for configuration examples")
    print("and docs/guides/MATCHING_RULES.md for detailed documentation.")
