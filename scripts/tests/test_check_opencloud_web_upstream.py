"""Offline regression coverage for the separately licensed upstream browser client."""
import importlib.util
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location("check_opencloud_upstream", ROOT / "scripts" / "check_opencloud_upstream.py")
watch = importlib.util.module_from_spec(spec)
spec.loader.exec_module(watch)
WEB_REPO = "opencloud-eu/web"


class WebUpstreamWatchTests(unittest.TestCase):
    def setUp(self):
        self.baseline = json.loads((ROOT / "docs" / "WEB-CLIENT-WATCH.json").read_text())
        self.current = {
            "source_sha": self.baseline["source_sha"],
            "latest_release": self.baseline["latest_release"],
            "advisories": self.baseline["advisories"],
        }

    def test_source_matches_imported_web_client(self):
        self.assertIn(self.baseline["source_sha"], (ROOT / "docs" / "WEB-CLIENT-UPSTREAM.md").read_text())
        self.assertEqual(len(self.baseline["source_sha"]), 40)

    def test_clean_baseline(self):
        self.assertEqual(watch.detect_changes(self.baseline, self.current, WEB_REPO), [])

    def test_commit_drift(self):
        c = dict(self.current, source_sha="f" * 40)
        self.assertEqual(watch.detect_changes(self.baseline, c, WEB_REPO)[0]["type"], "upstream_commit")

    def test_release_drift(self):
        c = dict(self.current, latest_release="v8.2.0")
        self.assertEqual(watch.detect_changes(self.baseline, c, WEB_REPO)[0]["type"], "upstream_release")

    def test_new_public_advisory(self):
        advisory = {"ghsa_id": "GHSA-xxxx-yyyy-zzzz", "severity": "high", "updated_at": "2026-10-21T00:00:00Z"}
        c = dict(self.current, advisories=[advisory])
        self.assertEqual(watch.detect_changes(self.baseline, c, WEB_REPO)[0]["type"], "new_public_security_advisory")

    def test_modified_advisory(self):
        advisory = {"ghsa_id": "GHSA-xxxx-yyyy-zzzz", "severity": "high", "updated_at": "2026-10-21T00:00:00Z"}
        prior = dict(self.baseline, advisories=[advisory])
        c = dict(self.current, advisories=[dict(advisory, severity="critical")])
        self.assertEqual(watch.detect_changes(prior, c, WEB_REPO)[0]["type"], "changed_public_security_advisory")

    def test_removed_advisory(self):
        advisory = {"ghsa_id": "GHSA-xxxx-yyyy-zzzz", "severity": "high", "updated_at": "2026-10-21T00:00:00Z"}
        prior = dict(self.baseline, advisories=[advisory])
        self.assertEqual(watch.detect_changes(prior, self.current, WEB_REPO)[0]["type"], "public_advisory_feed_changed")

    def test_cannot_compare_against_wrong_upstream(self):
        with self.assertRaises(ValueError):
            watch.detect_changes(self.baseline, self.current, "opencloud-eu/opencloud")

    def test_reject_non_list_advisories(self):
        with self.assertRaises(ValueError):
            watch.make_snapshot({"sha": self.baseline["source_sha"]}, {"tag_name": "v8.1.0"}, {"bad": "shape"})


if __name__ == "__main__":
    unittest.main()
