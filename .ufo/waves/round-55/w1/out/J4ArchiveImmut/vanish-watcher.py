#!/usr/bin/env python3
"""Same-uid watcher: unlink the counter's own archive reference as soon as it
appears in the scratch root, i.e. vanish it BETWEEN the counter's download write
and its Archive() read.  Proves the fail-closed direction (never green)."""
import glob
import os
import sys
import time

root, log = sys.argv[1], sys.argv[2]
deadline = time.monotonic() + float(sys.argv[3])
hits = []
while time.monotonic() < deadline:
    for p in glob.glob(os.path.join(root, "r53c1-*", "counter-archive.tar.gz")):
        try:
            sz = os.path.getsize(p)
            os.unlink(p)
            hits.append((p, sz, os.path.exists(p)))
            with open(log, "a") as fh:
                fh.write(f"unlinked size={sz} exists_after={os.path.exists(p)} {p}\n")
        except OSError as exc:
            with open(log, "a") as fh:
                fh.write(f"unlink failed {exc!r} {p}\n")
    time.sleep(0.001)
with open(log, "a") as fh:
    fh.write(f"watcher done, hits={len(hits)}\n")
