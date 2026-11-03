#!/usr/bin/env python3
"""Exercise the IDP lock contract against genuine files and a synthetic drift case.

Read-only to the checkout. Makes disposable copies; no pnpm scripts or networking.
"""
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

import yaml

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "ops/tests/test_idp_lock_contract.py"
IDP = ROOT / "services/idp"


def test():
    with tempfile.TemporaryDirectory(prefix="gc-idp-contract-") as tmp:
        root = Path(tmp)
        (root / "ops/tests").mkdir(parents=True)
        (root / "services/idp").mkdir(parents=True)
        shutil.copyfile(SCRIPT, root / "ops/tests/test_idp_lock_contract.py")
        shutil.copyfile(IDP / "package.json", root / "services/idp/package.json")
        shutil.copyfile(IDP / "pnpm-lock.yaml", root / "services/idp/pnpm-lock.yaml")
        shutil.copyfile(IDP / "Makefile", root / "services/idp/Makefile")
        cmd = [sys.executable, str(root / "ops/tests/test_idp_lock_contract.py")]
        good = subprocess.run(cmd, capture_output=True, text=True, timeout=20)
        assert good.returncode == 0, "Valid locked source must pass"
        pkg = root / "services/idp/package.json"
        data = json.loads(pkg.read_text(encoding="utf-8"))
        assert "axios" in data["dependencies"]
        data["dependencies"]["axios"] = "999.0.0"
        pkg.write_text(json.dumps(data) + "\n", encoding="utf-8")
        bad = subprocess.run(cmd, capture_output=True, text=True, timeout=20)
        assert bad.returncode != 0, "Manifest-to-lock drift must fail"
        assert "Specifier drift for axios" in bad.stderr, "Wrong failure reason"
        # Restore legitimate manifest and make the Makefile silently mutable.
        # The same contract must fail before any frontend dependency installation.
        shutil.copyfile(IDP / "package.json", pkg)
        makefile = root / "services/idp/Makefile"
        original = makefile.read_text(encoding="utf-8")
        assert "\tpnpm install --frozen-lockfile\n" in original
        makefile.write_text(
            original.replace("\tpnpm install --frozen-lockfile\n", "\tpnpm install\n"),
            encoding="utf-8",
        )
        bad_install = subprocess.run(cmd, capture_output=True, text=True, timeout=20)
        assert bad_install.returncode != 0, "Unfrozen IDP install must fail"
        assert "IDP install must fail closed" in bad_install.stderr, "Wrong failure reason"
        # Restoring the trusted recipe isolates lockfile tampering tests.
        shutil.copyfile(IDP / "Makefile", makefile)
        lock = root / "services/idp/pnpm-lock.yaml"
        for mutation, expected in (
            ("bad_digest", "Invalid SHA-512 integrity metadata"),
            ("untrusted_url", "Untrusted or missing registry integrity metadata"),
        ):
            data = yaml.safe_load((IDP / "pnpm-lock.yaml").read_text(encoding="utf-8"))
            first = next(iter(data["packages"]))
            resolution = data["packages"][first]["resolution"]
            if mutation == "bad_digest":
                resolution["integrity"] = "sha512-not-valid-base64!"
            else:
                resolution["tarball"] = "http://untrusted.invalid/package.tgz"
            lock.write_text(yaml.safe_dump(data), encoding="utf-8")
            negative = subprocess.run(cmd, capture_output=True, text=True, timeout=20)
            assert negative.returncode != 0, mutation + " must fail"
            assert expected in negative.stderr, mutation + " rejected for wrong reason"

    print("PASS: IDP lock contract rejects drift, unfrozen installs, invalid hashes and custom tarballs")


if __name__ == "__main__":
    test()
