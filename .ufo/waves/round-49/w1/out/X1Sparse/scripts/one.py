#!/usr/bin/env python3
"""One extras cell in its own process: tag=before|after|fixed, case=key.

usage: one.py --root S --tag T --case KEY
"""
import hashlib
import importlib.util
import json
import os
import sys
import time

args = dict(zip(sys.argv[1::2], sys.argv[2::2]))
ROOT, TAG, CASE = args["--root"], args["--tag"], args["--case"]
A = json.load(open(os.path.join(ROOT, "art", "artifacts.json")))
GOOD, SIZE = A["good_sha"], A["good_size"]
A_ONLY = hashlib.sha256(b"A").hexdigest()

if CASE == "real-b11909-shaped-asset":
    arc, dig, size = A["real_asset"]
    m = A["real_member"]
    fn = (arc, dig, m["name"], m["sha256"], m["size"])
    meta = {"archive_bytes": size, "entries": 62, "member": m["name"],
            "member_sha256": m["sha256"], "member_size": m["size"]}
elif CASE == "pax-size-1e15-payload-16g":
    arc, dig, size = A["paxsize_payload16g"]
    fn = (arc, dig, A["memb"], A_ONLY, SIZE)
    meta = {"archive_bytes": size}
elif CASE == "plain-zeros-archive-512m":
    arc, dig, size = A["zeros512m"]
    fn = (arc, dig, A["memb"], GOOD, SIZE)
    meta = {"archive_bytes": size}
elif CASE == "pax-0.0-sparse-1e15":
    arc, dig, size = A["pax00_1e15"]
    fn = (arc, dig, A["memb"], A_ONLY, SIZE)
    meta = {"archive_bytes": size}
elif CASE in ("member-is-dir", "member-is-fifo"):
    arc, dig, size = A[CASE]
    fn = (arc, dig, A["memb"], GOOD, SIZE)
    meta = {"archive_bytes": size}
elif CASE in ("pax_bad_map", "pax10_nomap"):
    arc, dig, size = A[CASE]
    fn = (arc, dig, A["memb"], GOOD, SIZE)
    meta = {"archive_bytes": size}
else:
    raise SystemExit(f"unknown case {CASE}")

spec = importlib.util.spec_from_file_location(
    "kl", os.path.join(ROOT, TAG, "kama-llamacpp-live.py"))
kl = importlib.util.module_from_spec(spec)
spec.loader.exec_module(kl)

t0 = time.monotonic()
try:
    try:
        kl.verify_archive_member(*fn)
        r = {"outcome": "ok"}
    except TypeError as exc:
        if "positional argument" not in str(exc):
            raise
        kl.verify_archive_member(*fn[:4])
        r = {"outcome": "ok"}
except kl.SetupError as exc:
    r = {"outcome": "refused", "token": exc.code}
except BaseException as exc:  # noqa: BLE001
    r = {"outcome": "uncaught", "exc": f"{type(exc).__name__}: {exc}"}
r.update(case=CASE, tag=TAG, seconds=round(time.monotonic() - t0, 3), **meta)
print(json.dumps(r), flush=True)
