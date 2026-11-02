#!/usr/bin/env python3
"""Check adapted Caddy JSON for a strictly fail-closed Drive dev placeholder.

This validator is NOT a test of VPN connectivity, private DNS, certificate
trust, or public ingress. It rejects any actual backend route or relaxation.
"""
import copy
import json
import sys
from pathlib import Path

HOST = "drive-dev.goreecloud.com"
EXPECTED = {
    "apps": {
        "http": {
            "servers": {
                "srv0": {
                    "listen": [":443"],
                    "routes": [
                        {
                            "match": [{"host": [HOST]}],
                            "handle": [
                                {
                                    "handler": "subroute",
                                    "routes": [
                                        {
                                            "handle": [
                                                {
                                                    "body": "Development environment unavailable",
                                                    "handler": "static_response",
                                                    "status_code": 404,
                                                }
                                            ]
                                        }
                                    ],
                                }
                            ],
                            "terminal": True,
                        }
                    ],
                }
            }
        },
        "tls": {
            "automation": {
                "policies": [
                    {
                        "subjects": [HOST],
                        "issuers": [{"module": "internal"}],
                    }
                ]
            }
        },
    }
}


def validate(config: object) -> None:
    if config != EXPECTED:
        raise ValueError(
            "Adapted drive-dev Caddy policy is not the exact fail-closed "
            "404-only candidate. No reverse proxy, extra route, additional "
            "hostname, or changed TLS policy is authorized."
        )


def self_test() -> None:
    validate(copy.deepcopy(EXPECTED))
    cases = []
    for label, mutate in (
        ("backend", lambda c: c["apps"]["http"]["servers"]["srv0"]["routes"][0]["handle"][0]["routes"][0]["handle"][0].update({"handler": "reverse_proxy"})),
        ("success-response", lambda c: c["apps"]["http"]["servers"]["srv0"]["routes"][0]["handle"][0]["routes"][0]["handle"][0].update({"status_code": 200})),
        ("host-wildcard", lambda c: c["apps"]["http"]["servers"]["srv0"]["routes"][0]["match"][0].update({"host": ["*.goreecloud.com"]})),
        ("public-listener", lambda c: c["apps"]["http"]["servers"]["srv0"].update({"listen": [":80", ":443"]})),
        ("tls-change", lambda c: c["apps"]["tls"]["automation"]["policies"][0].update({"issuers": [{"module": "acme"}]})),
        ("extra-route", lambda c: c["apps"]["http"]["servers"]["srv0"]["routes"].append({})),
    ):
        bad = copy.deepcopy(EXPECTED)
        mutate(bad)
        try:
            validate(bad)
        except ValueError:
            cases.append(label)
        else:
            raise AssertionError("Unsafe regression was accepted: " + label)
    print("PASS: Caddy JSON validator rejected " + str(len(cases)) + " simulated policy regressions")


def main() -> None:
    if len(sys.argv) == 2 and sys.argv[1] == "--self-test":
        self_test()
    elif len(sys.argv) == 2:
        data = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
        validate(data)
        print("PASS: adapted Caddy config exactly matches the fail-closed Drive dev placeholder")
    else:
        raise SystemExit("usage: python3 test_drive_dev_adapted_policy.py <adapted.json>|--self-test")


if __name__ == "__main__":
    try:
        main()
    except (ValueError, AssertionError, json.JSONDecodeError) as exc:
        raise SystemExit("FAIL: " + str(exc)) from exc
