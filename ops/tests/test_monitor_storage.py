"""Offline, read-only storage monitor policy tests: no mounted drives are altered."""
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from ops.monitor_storage import evaluate, enforce_filesystem_policy

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "ops" / "monitor_storage.py"
GIB = 1024 ** 3


class StorageHeadroomContracts(unittest.TestCase):
    def test_evaluate_disk_and_inode_critical_states(self):
        healthy = evaluate(100 * GIB, 50 * GIB, 1000, 750, 20.0, 20.0, 10.0)
        self.assertEqual(healthy["status"], "PASS")
        self.assertEqual(healthy["findings"], [])
        disk = evaluate(100 * GIB, 10 * GIB, 1000, 750, 20.0, 20.0, 10.0)
        self.assertIn("disk_free_below_absolute_limit", disk["findings"])
        self.assertIn("disk_free_below_percent_limit", disk["findings"])
        inode = evaluate(100 * GIB, 80 * GIB, 1000, 50, 20.0, 20.0, 10.0)
        self.assertIn("inode_free_below_percent_limit", inode["findings"])

    def test_missing_or_inconsistent_filesystem_metrics_never_pass(self):
        bad_counters = [
            (0, 0, 1000, 500),
            (100, 101, 1000, 500),
            (100, -1, 1000, 500),
            (100, 50, 1000, 1001),
            (100, 50, -1, 0),
            (100, 50, 0, 0),
            (100.0, 50, 1000, 500),
        ]
        for args in bad_counters:
            with self.subTest(args=args):
                with self.assertRaises(ValueError):
                    evaluate(*args, 0.0, 0.0, 10.0)
        # Filesystems that do not expose inode counts can explicitly disable
        # inode alerting, while remaining transparent about unknown usage.
        allowed = evaluate(100 * GIB, 60 * GIB, 0, 0, 0.0, 0.0, 0.0)
        self.assertEqual(allowed["status"], "PASS")
        self.assertIsNone(allowed["inode_free_percent"])

    def test_root_device_policy_is_opt_in_and_never_changes_original(self):
        original = evaluate(100 * GIB, 80 * GIB, 100, 90, 20.0, 20.0, 10.0)
        warned = enforce_filesystem_policy(original, True)
        self.assertEqual(warned["status"], "PASS")
        self.assertTrue(warned["shares_root_device"])
        strict = enforce_filesystem_policy(original, True, True)
        self.assertEqual(strict["status"], "CRITICAL")
        self.assertIn("target_shares_root_filesystem", strict["findings"])
        self.assertEqual(original["findings"], [])
        self.assertEqual(enforce_filesystem_policy(original, False, True)["status"], "PASS")

    def test_invalid_non_finite_thresholds_fail_closed_before_storage_reads(self):
        for value in ("nan", "inf", "-inf", "-1"):
            with self.subTest(value=value):
                result = subprocess.run(
                    [sys.executable, str(SCRIPT), "--path", "/", f"--min-percent={value}"],
                    stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=8
                )
                self.assertEqual(result.returncode, 3)
                self.assertIn("thresholds must be finite and nonnegative", result.stderr)
                self.assertNotIn("free_gib", result.stdout)


    def test_invalid_cli_configuration_is_not_a_false_capacity_alert(self):
        for options in (
            ["--path", "/", "--min-percent=101"],
            ["--path", "/", "--min-inode-percent=101"],
            ["--path", "/", "--min-gib=not-a-number"],
            ["--path", "/"],
            ["--unknown-option"],
        ):
            with self.subTest(options=options):
                args = options if options != ["--path", "/"] else ["--path", "/", "--min-gib=-1"]
                result = subprocess.run([sys.executable, str(SCRIPT), *args],
                                        stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                        text=True, timeout=8)
                self.assertEqual(result.returncode, 3)
                self.assertIn("ERROR: Invalid storage monitor arguments:", result.stderr)
                self.assertNotIn("free_gib", result.stdout)

if __name__ == "__main__":
    unittest.main()
