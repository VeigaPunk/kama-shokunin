#!/usr/bin/env python3
"""Is the sparse read bounded by the *declared* size, and is the extracted file
sparse on disk? (64 GiB keeps the probe to ~8 s.)"""
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

DECL = 64 << 30
p = P.path("pax64.tgz")
with tarfile.open(p, "w:gz", format=tarfile.PAX_FORMAT) as tf:
    ti = tarfile.TarInfo(P.MEMBER)
    ti.size = 1
    ti.pax_headers = {"GNU.sparse.map": "0,1", "GNU.sparse.size": str(DECL)}
    tf.addfile(ti, io.BytesIO(b"A"))
t0, n, eof = time.monotonic(), 0, False
with tarfile.open(p) as tf:
    fh = tf.extractfile(tf.getmember(P.MEMBER))
    while True:
        chunk = fh.read(1 << 20)
        if not chunk:
            eof = True
            break
        n += len(chunk)
dt = time.monotonic() - t0
print(f"declared={DECL} archive_bytes={os.path.getsize(p)} read={n} eof={eof} "
      f"seconds={dt:.2f} GiB_per_s={n/dt/1e9:.2f} -> 10^15 B would take {10**15/(n/dt)/3600:.0f} h")

# extraction result on this filesystem
p2 = P.path("xb.tgz")
with tarfile.open(p2, "w:gz", format=tarfile.PAX_FORMAT) as tf:
    ti = tarfile.TarInfo(P.MEMBER)
    ti.size = 1
    ti.pax_headers = {"GNU.sparse.map": "0,1", "GNU.sparse.size": str(1 << 30)}
    tf.addfile(ti, io.BytesIO(b"A"))
tree = P.path("xb-tree")
shutil.rmtree(tree, ignore_errors=True)
os.makedirs(tree)
kr.extract(p2, tree)
st = os.stat(os.path.join(tree, P.MEMBER))
print(f"extracted apparent={st.st_size} allocated={st.st_blocks * 512} "
      f"sparse_on_this_fs={st.st_blocks * 512 < st.st_size}")
shutil.rmtree(tree, ignore_errors=True)
