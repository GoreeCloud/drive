#!/usr/bin/env python3
"""Read-only GitHub upstream drift and public security advisory watch for GoreeCloud Drive."""

import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path

BASELINE_PATH = Path(__file__).resolve().parents[1] / "docs" / "UPSTREAM-WATCH.json"
UPSTREAM_REPO = "opencloud-eu/opencloud"


def fetch_json(path):
    url = "https://api.github.com/repos/" + UPSTREAM_REPO + "/" + path
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "GoreeCloud-Drive-Upstream-Watch",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    token = os.environ.get("GH_TOKEN", "")
    if token:
        headers["Authorization"] = "Bearer " + token
    request = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(request, timeout=20) as response:
        return json.load(response)


def make_snapshot(commit, release, advisories):
    if not isinstance(advisories, list):
        raise ValueError("unexpected GitHub advisory response shape")
    return {
        "source_sha": commit["sha"],
        "latest_release": release["tag_name"],
        "advisories": sorted(
            [
                {
                    "ghsa_id": advisory["ghsa_id"],
                    "severity": advisory["severity"],
                    "updated_at": advisory["updated_at"],
                }
                for advisory in advisories
            ],
            key=lambda a: a["ghsa_id"],
        ),
    }


def detect_changes(baseline, current):
    if baseline.get("upstream_repo") != UPSTREAM_REPO:
        raise ValueError("baseline upstream repository does not match guarded source")
    changes = []
    for field, label in (
        ("source_sha", "upstream_commit"),
        ("latest_release", "upstream_release"),
    ):
        if baseline[field] != current[field]:
            changes.append({
                "type": label,
                "reviewed": baseline[field],
                "current": current[field],
            })

    known = {a["ghsa_id"]: a for a in baseline["advisories"]}
    live = {a["ghsa_id"]: a for a in current["advisories"]}
    for ghsa_id in sorted(live.keys() - known.keys()):
        changes.append({
            "type": "new_public_security_advisory",
            "ghsa_id": ghsa_id,
            "severity": live[ghsa_id]["severity"],
        })
    for ghsa_id in sorted(known.keys() & live.keys()):
        if any(
            known[ghsa_id][field] != live[ghsa_id][field]
            for field in ("severity", "updated_at")
        ):
            changes.append({
                "type": "changed_public_security_advisory",
                "ghsa_id": ghsa_id,
                "previous": known[ghsa_id],
                "current": live[ghsa_id],
            })
    for ghsa_id in sorted(known.keys() - live.keys()):
        changes.append({
            "type": "public_advisory_feed_changed",
            "ghsa_id": ghsa_id,
        })
    return changes


def main():
    baseline = json.loads(BASELINE_PATH.read_text(encoding="utf-8"))
    try:
        commit = fetch_json("commits/main")
        release = fetch_json("releases/latest")
        advisories = fetch_json("security-advisories?per_page=100")
        current = make_snapshot(commit, release, advisories)
        findings = detect_changes(baseline, current)
    except (urllib.error.URLError, TimeoutError, OSError, ValueError, KeyError, TypeError) as err:
        print("UPSTREAM_WATCH_UNVERIFIED: GitHub source could not be fully checked: " + str(err), file=sys.stderr)
        return 2

    if findings:
        print("UPSTREAM_REVIEW_REQUIRED: GoreeCloud Drive upstream baseline needs manual review.")
        for change in findings:
            print(json.dumps(change, sort_keys=True))
        print("Do not auto-merge or advance the snapshot without reviewing changes and regression tests.")
        return 1

    print("UPSTREAM_NO_DRIFT: main SHA, latest public release and known advisory metadata match the last reviewed snapshot.")
    print("This does NOT certify that there are no vulnerabilities or that the fork is production-ready.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
