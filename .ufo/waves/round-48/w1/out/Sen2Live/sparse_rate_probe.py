#!/usr/bin/env python3
"""Throughput of the real verify_archive_member loop (read + SHA-256) on a
GNU sparse member, which is the number that decides the DoS budget."""
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import probe_archive as P  # noqa: E402

for real in (1 << 30, 4 << 30):
    a, s = P.sparse_archive(f"rate-{real}.tgz", real)
    t0 = time.monotonic()
    try:
        P.kl.verify_archive_member(a, s, P.MEMBER, P.sha(b"nope"))
        tok = "verified"
    except P.kl.SetupError as exc:
        tok = exc.code
    dt = time.monotonic() - t0
    print(f"declared={real} archive_bytes={os.path.getsize(a)} seconds={dt:.3f} "
          f"GB_per_s={real/dt/1e9:.2f} -> a 10**15 declared member takes "
          f"{10**15/(real/dt)/3600:.0f} h ({tok})")
