#!/usr/bin/env python3
"""Read-only NetBird peer/DNS identity verifier for GoreeCloud Drive dev.

Checks a client-reported management connection, the exact gateway peer and
the configured private DNS server. Does not establish server ACL or firewall
authorization. Does not modify VPN, DNS, TLS or application settings.
"""
import argparse
import ipaddress
import json
import subprocess
import sys

DEFAULT_PEER_FQDN = "goreecloud-vps-01.netbird.selfhosted"
CGNAT = ipaddress.ip_network("100.64.0.0/10")


def evaluate(data: dict, fqdn: str, ipv4: str) -> list[str]:
    issues = []
    try:
        expected = ipaddress.IPv4Address(ipv4)
    except ipaddress.AddressValueError:
        return ["invalid_gateway_ipv4"]
    if expected not in CGNAT:
        issues.append("gateway_outside_vpn_range")
    if data.get("management", {}).get("connected") is not True:
        issues.append("management_not_connected")
    if data.get("signal", {}).get("connected") is not True:
        issues.append("signaling_not_connected")
    peer_data = data.get("peers", {}).get("details", [])
    if not isinstance(peer_data, list):
        peer_data = []
    peers = [p for p in peer_data
             if isinstance(p, dict) and p.get("fqdn") == fqdn]
    if len(peers) != 1:
        issues.append("expected_peer_identity_not_unique")
    else:
        peer = peers[0]
        if peer.get("netbirdIp") != ipv4:
            issues.append("expected_peer_vpn_ip_mismatch")
        if peer.get("status") != "Connected":
            issues.append("expected_peer_not_connected")
    try:
        local = ipaddress.ip_interface(data.get("netbirdIp", "")).ip
        if local not in CGNAT or local == expected:
            issues.append("client_vpn_ip_invalid")
    except ValueError:
        issues.append("client_vpn_ip_invalid")
    dns = data.get("dnsServers", [])
    matches = [item for item in dns if isinstance(item, dict)
               and item.get("enabled") is True
               and ipv4 + ":53" in item.get("servers", [])]
    if len(matches) != 1:
        issues.append("expected_private_dns_server_not_active")
    return sorted(set(issues))


def self_test() -> None:
    sample = {
        "management": {"connected": True},
        "signal": {"connected": True},
        "netbirdIp": "100.71.238.171/16",
        "peers": {"details": [{"fqdn": DEFAULT_PEER_FQDN,
                               "netbirdIp": "100.71.27.119",
                               "status": "Connected"}]},
        "dnsServers": [{"enabled": True, "servers": ["100.71.27.119:53"]}],
    }
    assert evaluate(sample, DEFAULT_PEER_FQDN, "100.71.27.119") == []
    import copy
    changes = [
        lambda x: x["management"].update(connected=False),
        lambda x: x["signal"].update(connected=False),
        lambda x: x["peers"]["details"][0].update(status="Idle"),
        lambda x: x["peers"]["details"][0].update(netbirdIp="100.71.27.120"),
        lambda x: x["peers"]["details"][0].update(fqdn="unexpected.netbird.selfhosted"),
        lambda x: x["dnsServers"][0].update(enabled=False),
        lambda x: x["dnsServers"][0].update(servers=["135.148.45.22:53"]),
        lambda x: x.update(netbirdIp="135.148.45.22/32"),
    ]
    for i, change in enumerate(changes, start=1):
        bad = copy.deepcopy(sample)
        change(bad)
        assert evaluate(bad, DEFAULT_PEER_FQDN, "100.71.27.119"), (
            "Unsafe NetBird state accepted in regression " + str(i))
    print("PASS: NetBird peer/DNS identity verifier and eight negative regressions")


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--expected-peer", default=DEFAULT_PEER_FQDN)
    p.add_argument("--expected-vpn-ip")
    p.add_argument("--self-test", action="store_true")
    args = p.parse_args()
    if args.self_test:
        self_test()
        return 0
    if not args.expected_vpn_ip:
        p.error("--expected-vpn-ip is required for live check")
    try:
        result = subprocess.run(["netbird", "status", "--json"], capture_output=True,
                                text=True, timeout=8, check=True)
        current = json.loads(result.stdout)
        findings = evaluate(current, args.expected_peer, args.expected_vpn_ip)
    except (OSError, subprocess.SubprocessError, ValueError, TypeError):
        print(json.dumps({"status": "ERROR", "reason": "netbird_status_unavailable"}))
        return 3
    report = {"expected_peer": args.expected_peer,
              "expected_vpn_ip": args.expected_vpn_ip,
              "status": "PASS" if not findings else "BLOCKED",
              "findings": findings,
              "caveat": "Peer connectivity and configured DNS only; server ingress ACL still unverified"}
    print(json.dumps(report, sort_keys=True))
    return 0 if not findings else 2


if __name__ == "__main__":
    sys.exit(main())
