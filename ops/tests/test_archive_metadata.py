#!/usr/bin/env python3
"""Exercise metadata-preserving GNU tar backup using disposable synthetic files.

This is NOT a backup of a GoreeCloud instance and is NOT an off-host restore.
"""
from pathlib import Path
import hashlib
import os
import subprocess
import tempfile

def execute(*args, cwd):
    subprocess.run(args, cwd=cwd, check=True, stdout=subprocess.DEVNULL)

def test():
    with tempfile.TemporaryDirectory(prefix="gc-drive-metadata-test-") as scratch:
        root=Path(scratch)
        source=root/"source"
        restored=root/"restore"
        source.mkdir(mode=0o700)
        restored.mkdir(mode=0o700)
        (source/"config").mkdir(mode=0o700)
        (source/"data").mkdir(mode=0o700)
        item=source/"data"/"fixture.bin"
        item.write_bytes(b"synthetic GoreeCloud Drive restoration fixture\x00\xff")
        item.chmod(0o640)
        attribute=b"synthetic-xattr-metadata"
        os.setxattr(item,"user.goreecloud_backup_test",attribute)
        (source/"config"/"settings.example").write_text("synthetic=true\n",encoding="utf-8")
        archive=root/"fixture.tar"
        execute("tar","--format=pax","--xattrs","--xattrs-include=user.*","--acls",
                "-cf",str(archive),"-C",str(source),"config","data",cwd=root)
        execute("tar","--xattrs","--xattrs-include=user.*","--acls",
                "-xf",str(archive),"-C",str(restored),cwd=root)
        back=restored/"data"/"fixture.bin"
        assert hashlib.sha256(back.read_bytes()).digest()==hashlib.sha256(item.read_bytes()).digest()
        assert os.getxattr(back,"user.goreecloud_backup_test")==attribute
        assert (back.stat().st_mode & 0o777)==0o640
        assert (restored/"config"/"settings.example").read_text()=="synthetic=true\n"
    print("PASS: synthetic backup/restore preserved content, user xattr and file mode")
if __name__=="__main__":
    test()
