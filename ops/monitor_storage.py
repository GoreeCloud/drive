#!/usr/bin/env python3
"""Read-only GoreeCloud Drive storage headroom check.

Linux/POSIX only. Does not install a scheduler, enforce quotas or touch files.
Exit 0 = within configured thresholds; exit 2 = below threshold; exit 3 = error.
"""
import argparse
import json
import os
from pathlib import Path
import shutil
import sys

def evaluate(total, free, inode_total, inode_free, min_gib, min_percent, inode_min_percent):
    gib = 1024 ** 3
    disk_free_percent = (free / total * 100) if total else 0
    inode_free_percent = (inode_free / inode_total * 100) if inode_total else None
    findings = []
    if free < min_gib * gib:
        findings.append("disk_free_below_absolute_limit")
    if disk_free_percent < min_percent:
        findings.append("disk_free_below_percent_limit")
    if inode_free_percent is not None and inode_free_percent < inode_min_percent:
        findings.append("inode_free_below_percent_limit")
    return dict(free_gib=round(free / gib, 2),
                total_gib=round(total / gib, 2),
                free_percent=round(disk_free_percent, 1),
                inode_free_percent=round(inode_free_percent, 1) if inode_free_percent is not None else None,
                status="CRITICAL" if findings else "PASS",
                findings=findings)

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--path", required=True, help="Directory to check; must exist")
    p.add_argument("--min-gib", type=float, default=20.0)
    p.add_argument("--min-percent", type=float, default=20.0)
    p.add_argument("--min-inode-percent", type=float, default=10.0)
    args=p.parse_args()
    if min(args.min_gib,args.min_percent,args.min_inode_percent) < 0:
        p.error("thresholds cannot be negative")
    if args.min_percent > 100 or args.min_inode_percent > 100:
        p.error("percentage thresholds cannot exceed 100")
    target=Path(args.path).resolve()
    if not target.is_dir():
        print("ERROR: Storage target is not a directory",file=sys.stderr)
        return 3
    try:
        usage=shutil.disk_usage(target)
        fs=os.statvfs(target)
        result=evaluate(usage.total,usage.free,fs.f_files,fs.f_favail,args.min_gib,args.min_percent,args.min_inode_percent)
        result["shares_root_device"]=target.stat().st_dev == Path("/").stat().st_dev
        if result["shares_root_device"]:
            result["warning"]="Target shares system-disk filesystem: quotas and alerting unverified"
        print(json.dumps(result,sort_keys=True))
        return 2 if result["status"] == "CRITICAL" else 0
    except OSError:
        print("ERROR: Could not read filesystem statistics",file=sys.stderr)
        return 3

if __name__=="__main__":
    raise SystemExit(main())
