#!/usr/bin/env python3
"""Read-only Linux NetBird path and DNS-interface check for GoreeCloud Drive dev.

Only observes kernel route selection and systemd-resolved's DNS link.
Does not establish peer ACL authorization, server firewall policy or TLS trust.
Never runs a command that changes network configuration.
"""
import argparse
import ipaddress
import json
import re
import subprocess
import sys

HOST = "drive-dev.goreecloud.com"
CGNAT = ipaddress.ip_network("100.64.0.0/10")


def evaluate(route_json, dns_output: str, expected_ip: str, interface: str) -> list[str]:
    findings = []
    if not re.fullmatch(r"[A-Za-z0-9_.-]{1,32}", interface):
        return ["invalid_interface_name"]
    expected = ipaddress.ip_address(expected_ip)
    if not isinstance(route_json, list) or len(route_json) != 1 or not isinstance(route_json[0], dict):
        findings.append("unexpected_route_result")
    else:
        route = route_json[0]
        if route.get("dst") != expected_ip:
            findings.append("wrong_route_destination")
        if route.get("dev") != interface:
            findings.append("route_does_not_use_expected_vpn_interface")
        source = route.get("prefsrc", route.get("src"))
        try:
            if not source or ipaddress.ip_address(source) not in CGNAT:
                findings.append("route_source_not_netbird_ipv4")
        except ValueError:
            findings.append("invalid_route_source")
    # Require the answer itself to carry the systemd-resolved link marker.
    # Other lines in resolvectl output must not override this association.
    first_line = next((ln for ln in dns_output.splitlines()
                       if ln.startswith(HOST + ":")), "")
    matches = re.findall(r"\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b", first_line)
    if matches != [expected_ip]:
        findings.append("dns_answer_not_expected_vpn_ip")
    match = re.search(r"-- link: ([A-Za-z0-9_.-]+)", first_line)
    if not match or match.group(1) != interface:
        findings.append("dns_not_from_expected_vpn_interface")
    if "-- Data from: network" not in dns_output:
        findings.append("dns_not_reported_from_network")
    return sorted(set(findings))


def read_only_command(*args: str) -> str:
    output = subprocess.run(args, capture_output=True, text=True,
                            timeout=6, check=True)
    return output.stdout


def self_test() -> None:
    good_route = [{"dst": "100.71.27.119", "dev": "wt0", "prefsrc": "100.71.238.171"}]
    good_dns = (HOST + ": 100.71.27.119 -- link: wt0\n"
                "-- Information acquired via protocol DNS\n"
                "-- Data from: network\n")
    assert evaluate(good_route, good_dns, "100.71.27.119", "wt0") == []
    bad = [
        ([{"dst": "100.71.27.119", "dev": "ens3", "prefsrc": "135.148.45.22"}], good_dns),
        ([{"dst": "100.71.27.119", "dev": "wt0", "prefsrc": "135.148.45.22"}], good_dns),
        ([{"dst": "100.71.27.120", "dev": "wt0", "prefsrc": "100.71.238.171"}], good_dns),
        ([], good_dns),
        (good_route, good_dns.replace("-- link: wt0", "-- link: ens3")),
        (good_route, good_dns.replace("100.71.27.119 -- link", "135.148.45.22 -- link")),
        (good_route, good_dns.replace("-- Data from: network", "-- Data from: cache")),
    ]
    for i, (route, dns) in enumerate(bad, start=1):
        assert evaluate(route, dns, "100.71.27.119", "wt0"), (
            "Unsafe network path accepted in regression " + str(i))
    print("PASS: NetBird route/DNS link verifier and seven negative regressions")


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--expected-vpn-ip")
    p.add_argument("--interface", default="wt0")
    p.add_argument("--self-test", action="store_true")
    args = p.parse_args()
    if args.self_test:
        self_test()
        return 0
    if not args.expected_vpn_ip:
        p.error("--expected-vpn-ip required")
    try:
        expected = ipaddress.IPv4Address(args.expected_vpn_ip)
    except ipaddress.AddressValueError:
        p.error("expected IP must be valid IPv4")
    if expected not in CGNAT:
        p.error("expected gateway IP must be in 100.64.0.0/10")
    if not re.fullmatch(r"[A-Za-z0-9_.-]{1,32}", args.interface):
        p.error("invalid interface")
    try:
        raw_route = read_only_command("ip", "-j", "route", "get", str(expected))
        raw_dns = read_only_command("resolvectl", "query", HOST)
        findings = evaluate(json.loads(raw_route), raw_dns,
                            str(expected), args.interface)
        result = {
            "host": HOST,
            "expected_vpn_ip": str(expected),
            "interface": args.interface,
            "path_status": "PASS" if not findings else "BLOCKED",
            "findings": findings,
            "caveat": "Client path only; does not authorize server-side ingress",
        }
        print(json.dumps(result, sort_keys=True))
        return 0 if not findings else 2
    except (OSError, subprocess.SubprocessError, ValueError, json.JSONDecodeError):
        print(json.dumps({"path_status": "ERROR",
                          "reason": "client_route_or_dns_inspection_failed"}))
        return 3


if __name__ == "__main__":
    sys.exit(main())
