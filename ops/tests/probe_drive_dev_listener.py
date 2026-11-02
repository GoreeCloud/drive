#!/usr/bin/env python3
"""Read-only private-interface listener preflight for GoreeCloud Drive dev.

A bound socket is NOT evidence of a Drive route, authenticated NetBird peer,
server-side peer ACL, firewall isolation, DNS provenance, or trusted TLS.
This script never starts a listener or modifies any host configuration.
Public CI may run only --self-test with synthetic ss output.
"""
import argparse
import ipaddress
import json
import re
import subprocess
import sys

CGNAT = ipaddress.ip_network("100.64.0.0/10")
LOCAL = re.compile(r"^(?:\[([^\]]+)\]|([^:]+)):(\d+)$")


def evaluate(ss_text: str, expected_ip: str, port: int) -> list[str]:
    issues = []
    try:
        address = ipaddress.IPv4Address(expected_ip)
        if address not in CGNAT:
            issues.append("expected_ip_not_netbird_range")
    except ipaddress.AddressValueError:
        return ["invalid_expected_vpn_ipv4"]
    if not 1 <= port <= 65535:
        return ["invalid_port"]
    listeners = []
    for line in ss_text.splitlines():
        parts = line.split()
        if not parts or parts[0] != "LISTEN":
            continue
        if len(parts) < 5:
            issues.append("unparseable_listener")
            continue
        match = LOCAL.fullmatch(parts[3])
        if not match:
            issues.append("unparseable_listener")
            continue
        host = match.group(1) or match.group(2)
        if int(match.group(3)) == port:
            listeners.append(host)
    if not listeners:
        issues.append("no_candidate_listener")
    if len(listeners) > 1:
        issues.append("multiple_candidate_listeners")
    for host in listeners:
        if host in ("0.0.0.0", "::", "*"):
            issues.append("wildcard_candidate_listener")
        elif host != expected_ip:
            issues.append("candidate_not_bound_to_expected_vpn_ipv4")
    return sorted(set(issues))


def self_test() -> None:
    good = "LISTEN 0 4096 100.71.27.119:8443 0.0.0.0:*"
    assert evaluate(good, "100.71.27.119", 8443) == []
    bad = [
        ("LISTEN 0 4096 0.0.0.0:8443 0.0.0.0:*", "100.71.27.119", 8443),
        ("LISTEN 0 4096 [::]:8443 [::]:*", "100.71.27.119", 8443),
        ("LISTEN 0 4096 127.0.0.1:8443 0.0.0.0:*", "100.71.27.119", 8443),
        (good + "\nLISTEN 0 4096 0.0.0.0:8443 0.0.0.0:*", "100.71.27.119", 8443),
        ("", "100.71.27.119", 8443),
        (good + "\n" + good, "100.71.27.119", 8443),
        (good, "100.71.27.120", 8443),
        ("LISTEN incomplete", "100.71.27.119", 8443),
        (good, "135.148.45.22", 8443),
    ]
    for index, (raw, ip, candidate_port) in enumerate(bad, 1):
        assert evaluate(raw, ip, candidate_port), "unsafe listener regression " + str(index)
    print("PASS: private listener parser and nine unsafe synthetic regressions")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--expected-vpn-ip")
    parser.add_argument("--port", type=int)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        self_test()
        return 0
    if args.expected_vpn_ip is None or args.port is None:
        parser.error("--expected-vpn-ip and --port required for live check")
    try:
        output = subprocess.run(["ss", "-H", "-ltn"], check=True,
                                capture_output=True, text=True, timeout=6).stdout
        issues = evaluate(output, args.expected_vpn_ip, args.port)
    except (OSError, subprocess.SubprocessError):
        print(json.dumps({"status": "ERROR", "reason": "socket_inventory_unavailable"}))
        return 3
    print(json.dumps({
        "status": "PASS_SOCKET_BIND_ONLY" if not issues else "NOT_READY",
        "expected_vpn_ip": args.expected_vpn_ip,
        "candidate_port": args.port,
        "findings": issues,
        "caveat": "No service identity, peer ACL/firewall, DNS rewrite or TLS trust verified",
    }, sort_keys=True))
    return 0 if not issues else 2


if __name__ == "__main__":
    sys.exit(main())
