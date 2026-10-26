#!/usr/bin/env python3
"""Non-matrix cells (big fixtures, malformed headers, real asset), machine-written
to extras.jsonl so every number in the report has a generated source.

usage: gen_extras.py --root S --out extras.jsonl
"""
import hashlib
import importlib.util
import json
import os
import subprocess
import sys
import time

ROOT = sys.argv[sys.argv.index("--root") + 1]
OUT = sys.argv[sys.argv.index("--out") + 1]
ART = os.path.join(ROOT, "art")
A = json.load(open(os.path.join(ART, "artifacts.json")))
TOOLS = {t: os.path.join(ROOT, t, "kama-llamacpp-live.py") for t in ("before", "after", "fixed")}
rows = []


def call(tag, fn, *args):
    spec = importlib.util.spec_from_file_location("kl_" + tag, TOOLS[tag])
    kl = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(kl)
    t0 = time.monotonic()
    try:
        try:
            kl.verify_archive_member(*fn, *args)
            r = {"outcome": "ok"}
        except TypeError as exc:
            if "positional argument" not in str(exc):
                raise
            kl.verify_archive_member(*(fn[:4] + args))
            r = {"outcome": "ok"}
    except kl.SetupError as exc:
        r = {"outcome": "refused", "token": exc.code}
    except BaseException as exc:  # noqa: BLE001
        r = {"outcome": "uncaught", "exc": f"{type(exc).__name__}: {exc}"}
    r["seconds"] = round(time.monotonic() - t0, 3)
    return r


def emit(case, tag, r, extra=None):
    r.update(case=case, tag=tag)
    if extra:
        r.update(extra)
    rows.append(r)
    print(json.dumps(r), flush=True)


GOOD = A["good_sha"]
SIZE = A["good_size"]
A_ONLY = hashlib.sha256(b"A").hexdigest()

# 1. the real b11909-shaped asset (62 entries, 24.5 MB, member 35ac50fb...)
arc, dig, size = A["real_asset"]
m = A["real_member"]
for tag in ("before", "after", "fixed"):
    emit("real-b11909-shaped-asset", tag,
         call(tag, (arc, dig, m["name"], m["sha256"], m["size"])),
         {"archive_bytes": size, "entries": 62, "member": m["name"],
          "member_sha256": m["sha256"], "member_size": m["size"]})

# 2. PAX `size` 10**15 over a 16 GiB zero payload (75 MB archive): full drain
arc, dig, size = A["paxsize_payload16g"]
for tag in ("before", "after", "fixed"):
    emit("pax-size-1e15-payload-16g", tag,
         call(tag, (arc, dig, A["memb"], A_ONLY, SIZE)), {"archive_bytes": size})

# 3. plain zeros archive, 512 MiB (tarfile sniffs xz before plain tar)
arc, dig, size = A["zeros512m"]
for tag in ("before", "after"):
    emit("plain-zeros-archive-512m", tag,
         call(tag, (arc, dig, A["memb"], GOOD, SIZE)), {"archive_bytes": size})

# 4. PAX 0.0 sparse (GNU.sparse.offset/numbytes + GNU.sparse.size 10**15)
arc, dig, size = A["pax00_1e15"]
for tag in ("before", "after", "fixed"):
    emit("pax-0.0-sparse-1e15", tag,
         call(tag, (arc, dig, A["memb"], A_ONLY, SIZE)), {"archive_bytes": size})

# 5. member entry is a directory / a FIFO
for key in ("member-is-dir", "member-is-fifo"):
    arc, dig, size = A[key]
    for tag in ("before", "after"):
        emit(key, tag, call(tag, (arc, dig, A["memb"], GOOD, SIZE)),
             {"archive_bytes": size})

# 6. malformed GNU sparse pax headers (ValueError out of tarfile)
for key in ("pax_bad_map", "pax10_nomap"):
    arc, dig, size = A[key]
    for tag in ("before", "after", "fixed"):
        emit(key, tag, call(tag, (arc, dig, A["memb"], GOOD, SIZE)),
             {"archive_bytes": size})

with open(OUT, "w") as fh:
    for r in rows:
        fh.write(json.dumps(r) + "\n")
print(f"wrote {OUT} rows={len(rows)}")
