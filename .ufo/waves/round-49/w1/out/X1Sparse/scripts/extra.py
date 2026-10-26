#!/usr/bin/env python3
"""Extra cells: the real b11909-shaped asset (positive control), the scaled PAX
size bomb, and the sub-cap plain-zeros archive (tarfile's xzopen sniff).

usage: extra.py --tool-dir D --case {real_asset,paxsize_payload16g,zeros512m}
"""
import argparse
import hashlib
import importlib.util
import json
import os
import time

ap = argparse.ArgumentParser()
ap.add_argument("--tool-dir", required=True)
ap.add_argument("--art", required=True)
ap.add_argument("--case", required=True)
a = ap.parse_args()
art = json.load(open(os.path.join(a.art, "artifacts.json")))
spec = importlib.util.spec_from_file_location(
    "kl", os.path.join(a.tool_dir, "kama-llamacpp-live.py"))
kl = importlib.util.module_from_spec(spec)
spec.loader.exec_module(kl)

if a.case == "real_asset":
    arc, dig, size = art["real_asset"]
    member, server, ssize = (art["real_member"]["name"],
                             art["real_member"]["sha256"],
                             art["real_member"]["size"])
else:
    arc, dig, size = art[a.case]
    member, server, ssize = art["memb"], hashlib.sha256(b"A").hexdigest(), art["good_size"]

t0 = time.monotonic()
cpu0 = time.process_time()
try:
    try:
        got = kl.verify_archive_member(arc, dig, member, server, ssize)
        nargs = 5
    except TypeError as exc:
        if "positional argument" not in str(exc):
            raise
        got = kl.verify_archive_member(arc, dig, member, server)
        nargs = 4
    out = {"outcome": "ok", "result": got}
except kl.SetupError as exc:
    out = {"outcome": "refused", "token": exc.code}
except BaseException as exc:  # noqa: BLE001
    out = {"outcome": "uncaught", "exc": f"{type(exc).__name__}: {exc}"}
out.update(case=a.case, seconds=round(time.monotonic() - t0, 3),
           cpu_s=round(time.process_time() - cpu0, 3), archive_bytes=size,
           nargs=locals().get("nargs"))
print(json.dumps(out), flush=True)
