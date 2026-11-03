#!/usr/bin/env python3
"""Read-only consistency and provenance checks for the OpenCloud IDP pnpm lock.

Not a vulnerability scan. Requires PyYAML. Never runs install scripts or modifies files.
"""
import json
import re
import shlex
from pathlib import Path

try:
    import yaml
except ImportError as exc:
    raise SystemExit("PyYAML is required; no checks performed") from exc

ROOT = Path(__file__).resolve().parents[2]
IDP = ROOT / "services" / "idp"


def check():
    pkg = json.loads((IDP / "package.json").read_text(encoding="utf-8"))
    lock = yaml.safe_load((IDP / "pnpm-lock.yaml").read_text(encoding="utf-8"))
    assert isinstance(lock, dict) and str(lock.get("lockfileVersion")) == "9.0"
    assert pkg.get("private") is True, "IDP should remain a private package"
    assert pkg.get("packageManager") == "pnpm@11.1.3", "Pinned package manager changed"
    # The project ships an authentication UI. A production asset build must
    # not silently resolve new dependencies when its manifest and lock disagree.
    makefile = (IDP / "Makefile").read_text(encoding="utf-8")
    recipes = re.findall(r"(?m)^node_modules:[^\n]*\n(\t[^\n]+)$", makefile)
    assert len(recipes) == 1, "Unique IDP node_modules recipe not found"
    assert shlex.split(recipes[0].strip()) == [
        "pnpm", "install", "--frozen-lockfile"
    ], "IDP install must fail closed with --frozen-lockfile"
    imp = lock.get("importers", {}).get(".")
    assert isinstance(imp, dict), "Root importer not found"
    summary = {}
    for key in ("dependencies", "devDependencies"):
        declared = pkg.get(key, {})
        recorded = imp.get(key, {})
        assert set(declared) == set(recorded), (
            key + " importer mismatch; only-in-package=" +
            repr(sorted(set(declared) - set(recorded))) +
            "; only-in-lock=" + repr(sorted(set(recorded) - set(declared)))
        )
        for name, spec in declared.items():
            entry = recorded[name]
            assert isinstance(entry, dict)
            assert entry.get("specifier") == spec, "Specifier drift for " + name
            assert entry.get("version"), "Unresolved direct dependency " + name
        summary[key] = len(declared)
    assert lock.get("packages") and lock.get("snapshots"), "Incomplete lockfile"
    assert isinstance(lock.get("overrides", {}), dict)
    summary["lockedPackages"] = len(lock["packages"])
    summary["snapshots"] = len(lock["snapshots"])
    summary["overrides"] = len(lock.get("overrides", {}))
    summary["packageManager"] = pkg["packageManager"]
    print(json.dumps({"status": "PASS", "idpLockContract": summary}, sort_keys=True))


if __name__ == "__main__":
    check()
