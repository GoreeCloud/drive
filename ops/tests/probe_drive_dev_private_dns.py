#!/usr/bin/env python3
"""Read-only client-side preflight for a PRIVATE GoreeCloud Drive dev hostname.

Does NOT edit DNS, VPN, firewall, proxies, certificates or application state.
A green result establishes DNS consistency only, not peer authorization.
"""
import argparse
import ipaddress
import json
from pathlib import Path
import socket
import ssl
import sys

HOST = "drive-dev.goreecloud.com"
CGNAT = ipaddress.ip_network("100.64.0.0/10")
DEFAULT_HOSTS = Path("/etc/hosts")


def evaluate(addresses: list[str], expected_ip: str, hosts_text: str) -> list[str]:
    issues = []
    expected = ipaddress.ip_address(expected_ip)
    if expected.version != 4 or expected not in CGNAT:
        issues.append("expected_ip_not_netbird_cgnat_range")
    if not addresses:
        issues.append("dns_has_no_ipv4_address")
    for raw in addresses:
        try:
            addr = ipaddress.ip_address(raw)
            if addr.version != 4 or addr not in CGNAT:
                issues.append("dns_address_outside_expected_vpn_range")
            if addr != expected:
                issues.append("dns_address_differs_from_verified_gateway")
        except ValueError:
            issues.append("invalid_dns_address")
    for line in hosts_text.splitlines():
        tokens = line.split("#", 1)[0].split()
        if len(tokens) > 1 and HOST in tokens[1:]:
            issues.append("local_hosts_override_present")
            break
    return sorted(set(issues))


def resolve_v4(host: str) -> list[str]:
    result = socket.getaddrinfo(host, None, family=socket.AF_INET,
                                type=socket.SOCK_STREAM)
    return sorted({item[4][0] for item in result})


def test_https(host: str, address: str, timeout: float) -> dict:
    """No auth or payload; verify TLS hostname and CA trust on VPN IP."""
    try:
        ctx = ssl.create_default_context()
        with socket.create_connection((address, 443), timeout=timeout) as conn:
            with ctx.wrap_socket(conn, server_hostname=host) as tls:
                return {"status": "PASS",
                        "protocol": tls.version(),
                        "peer_certificate_valid": True}
    except (OSError, ssl.SSLError) as exc:
        return {"status": "NOT_READY",
                "reason": type(exc).__name__}


def self_test() -> None:
    cases = [
        (["100.71.27.119"], "100.71.27.119", "", True),
        (["100.71.27.120"], "100.71.27.119", "", False),
        (["135.148.45.22"], "100.71.27.119", "", False),
        ([], "100.71.27.119", "", False),
        (["100.71.27.119"], "100.71.27.119",
         "100.71.27.119 drive-dev.goreecloud.com", False),
        (["100.71.27.119", "135.148.45.22"], "100.71.27.119", "", False),
    ]
    for addresses, expected, hosts, should_pass in cases:
        if (not evaluate(addresses, expected, hosts)) != should_pass:
            raise AssertionError("DNS security regression case failed")
    print("PASS: six private DNS preflight regression scenarios")


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--expected-vpn-ip", help="Verified gateway NetBird IPv4 address")
    p.add_argument("--hosts-file", type=Path, default=DEFAULT_HOSTS)
    p.add_argument("--check-tls", action="store_true",
                   help="Attempt verified TLS handshake; never disables trust checks")
    p.add_argument("--timeout", type=float, default=4.0)
    p.add_argument("--self-test", action="store_true")
    args = p.parse_args()
    if args.self_test:
        self_test()
        return 0
    if not args.expected_vpn_ip:
        p.error("--expected-vpn-ip required")
    if not (0 < args.timeout <= 15):
        p.error("--timeout must be between 0 and 15 seconds")
    try:
        ipaddress.IPv4Address(args.expected_vpn_ip)
    except ValueError:
        p.error("invalid --expected-vpn-ip")
    try:
        addresses = resolve_v4(HOST)
        resolve_error = None
    except socket.gaierror as exc:
        addresses = []
        resolve_error = type(exc).__name__
    try:
        hosts_text = args.hosts_file.read_text(encoding="utf-8")
    except OSError:
        print(json.dumps({"status": "ERROR", "reason": "hosts_file_unreadable"}))
        return 3
    findings = evaluate(addresses, args.expected_vpn_ip, hosts_text)
    report = {
        "hostname": HOST,
        "expected_vpn_ip": args.expected_vpn_ip,
        "resolved_ipv4": addresses,
        "dns_status": "PASS" if not findings else "BLOCKED",
        "findings": findings,
        "dns_error": resolve_error,
        "caveat": "DNS match alone does not verify VPN peer ACLs, TLS or app readiness",
    }
    if args.check_tls:
        if findings:
            report["tls"] = {"status": "SKIPPED", "reason": "dns_preflight_blocked"}
        else:
            report["tls"] = test_https(HOST, args.expected_vpn_ip, args.timeout)
    print(json.dumps(report, sort_keys=True))
    return 2 if findings or (args.check_tls and report["tls"]["status"] != "PASS") else 0


if __name__ == "__main__":
    sys.exit(main())
