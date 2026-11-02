#!/usr/bin/env python3
"""Static source-grounded audit of non-secret GoreeCloud Drive runtime env names.

Run from any directory. No real credentials are needed or printed. This test
checks source-declared configuration names; it does not start OpenCloud.
"""
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[2]
EXAMPLE = ROOT / "ops/deploy/env.runtime.example"
MANUAL_ENV = {"OC_CONFIG_DIR", "OC_BASE_DATA_PATH"}

def source_tags():
    tagged = set()
    for src in ROOT.rglob("*.go"):
        if any(d in src.parts for d in ("vendor", "node_modules", ".git")):
            continue
        try:
            data = src.read_text(encoding="utf-8")
        except (UnicodeError, OSError):
            continue
        for raw in re.findall(r'env:"([^"]+)"', data):
            tagged.update(key for key in raw.split(";") if key)
    return tagged

def runtime_contract():
    items = {}
    for raw in EXAMPLE.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        assert "=" in line, "Malformed environment example"
        key, value = line.split("=", 1)
        assert key and key not in items, "Duplicate or empty environment key"
        items[key] = value
    valid = source_tags() | MANUAL_ENV
    unknown = sorted(set(items) - valid)
    assert not unknown, "Unrecognized runtime variable names: " + ", ".join(unknown)
    assert "OC_ENABLE_GUEST_LINKS" not in items
    assert not any(k in items for k in ("IDM_ADMIN_PASSWORD", "ADMIN_PASSWORD"))
    expected = {
        "OC_CONFIG_DIR": "/etc/opencloud",
        "OC_BASE_DATA_PATH": "/var/lib/opencloud",
        "PROXY_HTTP_ADDR": "0.0.0.0:9200",
        "PROXY_TLS": "false",
        "OC_INSECURE": "false",
        "IDM_CREATE_DEMO_USERS": "false",
        "PROXY_ENABLE_BASIC_AUTH": "false",
        "OC_SHARING_PUBLIC_SHARE_MUST_HAVE_PASSWORD": "true",
        "OC_SHARING_PUBLIC_WRITEABLE_SHARE_MUST_HAVE_PASSWORD": "true",
        "OC_PASSWORD_POLICY_DISABLED": "false",
    }
    for key, value in expected.items():
        assert items.get(key) == value, "Unexpected safe default for " + key
    assert items.get("OC_URL", "").startswith("https://")
    assert int(items.get("OC_PASSWORD_POLICY_MIN_CHARACTERS", "0")) >= 12
    assert (ROOT / "ops/BACKUP-RESTORE.md").is_file()
    assert (ROOT / "ops/deploy/compose.yaml").is_file()
    print("PASS: source-declared environment names, sharing policy, runtime secrets isolation and storage paths")

if __name__ == "__main__":
    runtime_contract()
