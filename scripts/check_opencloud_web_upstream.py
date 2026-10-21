#!/usr/bin/env python3
"""Read-only drift/security watch for the pinned GoreeCloud Drive AGPL web client."""
import sys
from pathlib import Path
from check_opencloud_upstream import main

BASELINE = Path(__file__).resolve().parents[1] / "docs" / "WEB-CLIENT-WATCH.json"

if __name__ == "__main__":
    sys.exit(main(BASELINE, "opencloud-eu/web"))
