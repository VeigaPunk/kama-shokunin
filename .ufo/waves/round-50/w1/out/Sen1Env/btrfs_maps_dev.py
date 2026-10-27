#!/usr/bin/env python3
"""Minimal reproducer: /proc/<pid>/maps `dev` for a mapped file vs stat()'s st_dev.

Reads a file, mmaps it, then compares the `dev` and `inode` fields of that file's line in
/proc/self/maps against os.stat(path). On the fleet host's btrfs subvolume mount (/home,
subvol /@home) the two devs differ while the inode matches, which is exactly the pair
kama-llamacpp-live.py:711 and round50-replay-bind-audit.py:333 compare for equality.

  python3 btrfs_maps_dev.py PATH [PATH ...]
"""
import mmap
import os
import sys


def probe(path):
    with open(path, "rb") as fh:
        mm = mmap.mmap(fh.fileno(), 0, prot=mmap.PROT_READ)
        try:
            st = os.stat(path)
            rows = [ln for ln in open("/proc/self/maps") if ln.rstrip().endswith(path)]
            f = rows[0].split() if rows else []
            dev = f[3] if f else None
            ino = f[4] if f else None
        finally:
            mm.close()
    sdev = "%02x:%02x" % (os.major(st.st_dev), os.minor(st.st_dev))
    verdict = "equal" if (dev == sdev and ino == str(st.st_ino)) else "DIFFER"
    print(f"{path}\n  stat dev {sdev} ino {st.st_ino} | maps dev {dev} ino {ino} | {verdict}")
    return dev == sdev and ino == str(st.st_ino)


if __name__ == "__main__":
    ok = all([probe(p) for p in sys.argv[1:]])
    sys.exit(0 if ok else 1)
