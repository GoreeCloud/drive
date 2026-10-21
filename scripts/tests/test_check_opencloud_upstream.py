"""Offline tests for read-only GoreeCloud Drive OpenCloud upstream monitoring."""
import importlib.util
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location("check_opencloud_upstream", ROOT / "scripts" / "check_opencloud_upstream.py")
watch = importlib.util.module_from_spec(spec)
spec.loader.exec_module(watch)


class UpstreamWatchTests(unittest.TestCase):
    def setUp(self):
        self.baseline = json.loads((ROOT / "docs" / "UPSTREAM-WATCH.json").read_text())
        self.current = {
            "source_sha": self.baseline["source_sha"],
            "latest_release": self.baseline["latest_release"],
            "advisories": self.baseline["advisories"],
        }

    def test_recorded_sha_is_actual_import(self):
        self.assertIn(self.baseline["source_sha"], (ROOT / "docs" / "UPSTREAM.md").read_text())
        self.assertEqual(len(self.baseline["source_sha"]), 40)

    def test_no_drift(self):
        self.assertEqual(watch.detect_changes(self.baseline, self.current), [])

    def test_source_change_requires_review(self):
        changed = dict(self.current, source_sha="f" * 40)
        self.assertEqual(watch.detect_changes(self.baseline, changed)[0]["type"], "upstream_commit")

    def test_release_change_requires_review(self):
        changed = dict(self.current, latest_release="v8.2.0")
        self.assertEqual(watch.detect_changes(self.baseline, changed)[0]["type"], "upstream_release")

    def test_new_advisory_requires_review(self):
        advisories = self.current["advisories"] + [
            {"ghsa_id": "GHSA-xxxx-yyyy-zzzz", "severity": "high", "updated_at": "2026-10-21T00:00:00Z"}
        ]
        self.assertEqual(watch.detect_changes(self.baseline, dict(self.current, advisories=advisories))[0]["type"], "new_public_security_advisory")

    def test_changed_advisory_requires_review(self):
        advisories = [dict(x) for x in self.current["advisories"]]
        advisories[0]["updated_at"] = "2026-10-22T00:00:00Z"
        self.assertEqual(watch.detect_changes(self.baseline, dict(self.current, advisories=advisories))[0]["type"], "changed_public_security_advisory")

    def test_removed_advisory_requires_review(self):
        advisories = self.current["advisories"][:1]
        self.assertEqual(watch.detect_changes(self.baseline, dict(self.current, advisories=advisories))[0]["type"], "public_advisory_feed_changed")

    def test_other_source_rejected(self):
        bad = dict(self.baseline, upstream_repo="untrusted/other-project")
        with self.assertRaises(ValueError):
            watch.detect_changes(bad, self.current)

    def test_invalid_advisory_api_shape_rejected(self):
        with self.assertRaises(ValueError):
            watch.make_snapshot({"sha": "a" * 40}, {"tag_name": "v8.1.0"}, {"not": "an array"})


if __name__ == "__main__":
    unittest.main()
