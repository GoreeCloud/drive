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
    print("PASS: IDP lock contract detects a synthetic dependency version drift")


if __name__ == "__main__":
    test()
