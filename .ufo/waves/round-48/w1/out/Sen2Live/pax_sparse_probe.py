#!/usr/bin/env python3
"""PAX-format GNU sparse member: `GNU.sparse.realsize` is decimal, so the
declared member size is not capped by the old GNU 12-byte octal field.
Reads are capped here at 32 GiB so the probe itself terminates."""
import io
import os
import sys
import tarfile
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import probe_archive as P  # noqa: E402

CAP = 32 << 30
for i, pax in enumerate((
    {"GNU.sparse.map": "0,1", "GNU.sparse.size": str(10 ** 15)},
    {"GNU.sparse.map": "0,1", "GNU.sparse.major": "1", "GNU.sparse.minor": "0",
     "GNU.sparse.realsize": str(10 ** 15)},
)):
    p = P.path(f"pax{i}.tgz")
    with tarfile.open(p, "w:gz", format=tarfile.PAX_FORMAT) as tf:
        ti = tarfile.TarInfo(P.MEMBER)
        ti.size = 1
        ti.pax_headers = dict(pax)
        tf.addfile(ti, io.BytesIO(b"A"))
    with tarfile.open(p) as tf:
        info = tf.getmember(P.MEMBER)
        fh = tf.extractfile(info)
        n, t0, eof = 0, time.monotonic(), False
        while n <= CAP:
            chunk = fh.read(1 << 20)
            if not chunk:
                eof = True
                break
            n += len(chunk)
    rate = n / max(time.monotonic() - t0, 1e-9) / 1e9
    print(f"{('0.1' if i == 0 else '1.0')} declared={info.size} archive_bytes={os.path.getsize(p)} "
          f"read={n} eof={eof} seconds={time.monotonic()-t0:.2f} GiB_per_s={rate:.2f}")
