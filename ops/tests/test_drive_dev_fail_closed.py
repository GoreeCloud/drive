#!/usr/bin/env python3
"""Guard the review-only GoreeCloud Drive development Caddy placeholder.

This intentionally verifies a strict, fail-closed configuration, not VPN
connectivity, TLS trust, DNS, application health, or deployment readiness.
An active route requires independent approval and new acceptance tests.
"""
from pathlib import Path

ROUTE = Path(__file__).resolve().parents[2] / "ops/dev/Caddyfile.private.example"
EXPECTED = (
    "drive-dev.goreecloud.com {",
    "tls internal",
    'respond "Development environment unavailable" 404',
    "}",
)


def active_lines(source: str) -> tuple[str, ...]:
    return tuple(
        line.split("#", 1)[0].strip()
        for line in source.splitlines()
        if line.split("#", 1)[0].strip()
    )


def is_fail_closed(source: str) -> bool:
    return active_lines(source) == EXPECTED


def main() -> None:
    source = ROUTE.read_text(encoding="utf-8")
    if not is_fail_closed(source):
        raise SystemExit(
            "FAIL: drive-dev Caddy placeholder changed; no active route is "
            "approved. Review VPN peer ACL, private DNS, TLS and recovery gates."
        )
    # Regression probes: these must not be accepted as a safe placeholder.
    for changed in (
        source.replace('respond "Development environment unavailable" 404',
                       "reverse_proxy goreecloud-drive-dev:9200"),
        source.replace(" 404", " 200"),
        source.replace("tls internal", "tls internal\n    @vpn remote_ip 100.64.0.0/10"),
        source.replace("drive-dev.goreecloud.com", "drive.goreecloud.com"),
    ):
        if is_fail_closed(changed):
            raise SystemExit("FAIL: fail-closed regression probe was accepted")
    print("PASS: private dev Caddy example remains strictly fail-closed")


if __name__ == "__main__":
    main()
