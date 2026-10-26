#!/usr/bin/env python3
"""One measurement cell: import verify_archive_member from a byte copy of the
lane tool, run one crafted case, report the token and the wall seconds.

Instrumentation: hashlib.sha256 is wrapped by a delegating counter (the real
hash does the work) so we can report bytes actually hashed, per hash object:
object #1 is the archive digest, object #2 the member digest. Counts are
checkpointed to a file every 128 MiB so a killed cell still shows a lower bound.

usage: cell.py --tool-dir D --case NAME --art A --server-size {none|good} [--fifo]
"""
import argparse
import hashlib
import importlib.util
import json
import os
import sys
import time

ap = argparse.ArgumentParser()
ap.add_argument("--tool-dir", required=True)
ap.add_argument("--case", required=True)
ap.add_argument("--art", required=True)
ap.add_argument("--server-size", default="good")
ap.add_argument("--progress", default=None)
a = ap.parse_args()

art = json.load(open(os.path.join(a.art, "artifacts.json")))
MEMBER = art["memb"]
GOOD_SHA = art["good_sha"]
GOOD_SIZE = art["good_size"]
DECOY_SHA = hashlib.sha256(b"decoy\n").hexdigest()

# digests of the fixtures the cell itself needs, computed before patching
own = {}

spec = importlib.util.spec_from_file_location(
    "kl", os.path.join(a.tool_dir, "kama-llamacpp-live.py"))
kl = importlib.util.module_from_spec(spec)
spec.loader.exec_module(kl)

REAL = hashlib.sha256
COUNT = {"arc": 0, "mem": 0}
NOBJ = {"n": 0}
ARMED = {"on": False}


def checkpoint():
    if not a.progress:
        return
    with open(a.progress, "w") as fh:
        json.dump(COUNT, fh)


class Counting:
    def __init__(self, inner, label):
        self._h = inner
        self._label = label

    def note(self, data):
        if ARMED["on"] and data:
            n = COUNT[self._label]
            COUNT[self._label] = n + len(data)
            if (COUNT[self._label] >> 27) != (n >> 27):
                checkpoint()

    def update(self, data):
        self.note(data)
        return self._h.update(data)

    def hexdigest(self):
        return self._h.hexdigest()

    def digest(self):
        return self._h.digest()

    def copy(self):
        return Counting(self._h.copy(), self._label)


def patched(*args, **kwargs):
    if ARMED["on"]:
        NOBJ["n"] += 1
        label = "arc" if NOBJ["n"] == 1 else "mem"
    else:
        label = "off"
    c = Counting(REAL(*args, **kwargs), label)
    if args or kwargs.get("data") or kwargs.get("string"):
        c.note(args[0] if args else kwargs.get("data") or kwargs.get("string"))
    return c


hashlib.sha256 = patched

# ---- case table: (archive, asset_sha, server_sha, server_size) -------------
def A(key):
    return art[key][0]


def D(key):
    return art[key][1]


size_good = GOOD_SIZE if a.server_size == "good" else None

cases = {
    "regular-ok": (A("regular"), D("regular"), GOOD_SHA),
    "regular-wrong-member-digest": (A("regular"), D("regular"), "0" * 64),
    "member-symlink": (A("symlink"), D("symlink"), GOOD_SHA),
    "member-dir": (A("dir"), D("dir"), GOOD_SHA),
    "member-absent": (A("absent"), D("absent"), GOOD_SHA),
    "dup-good-first-good-digest": (A("dup_good_first"), D("dup_good_first"), GOOD_SHA),
    "dup-good-first-decoy-digest": (A("dup_good_first"), D("dup_good_first"), DECOY_SHA),
    "dup-decoy-first-good-digest": (A("dup_decoy_first"), D("dup_decoy_first"), GOOD_SHA),
    "gnu-old-sparse-1g": (A("gnu_old_1g"), D("gnu_old_1g"),
                          hashlib.sha256(b"A").hexdigest()),
    "gnu-old-sparse-8g": (A("gnu_old_8g"), D("gnu_old_8g"),
                          hashlib.sha256(b"A").hexdigest()),
    "pax-0.1-sparse-1e15": (A("pax01_1e15"), D("pax01_1e15"),
                            hashlib.sha256(b"A").hexdigest()),
    "pax-1.0-sparse-1e15": (A("pax10_1e15"), D("pax10_1e15"),
                            hashlib.sha256(b"A").hexdigest()),
    "tar-index-20k-entries": (A("many20k"), D("many20k"), GOOD_SHA),
    "gz-decompresses-zero-blocks-8g": (A("zeros8g"), D("zeros8g"), GOOD_SHA),
    "pax-size-1e15-payload-4g": (A("paxsize_payload4g"), D("paxsize_payload4g"),
                                 hashlib.sha256(b"A").hexdigest()),
    "archive-2gib-sparse-file": (A("archive_2g"), D("archive_2g"), GOOD_SHA),
    "fifo-path": (os.path.join(a.art, "probe.fifo"), "0" * 64, GOOD_SHA),
    "device-path-dev-zero": ("/dev/zero", "0" * 64, GOOD_SHA),
}
arc, asset, server = cases[a.case]
if a.case == "fifo-path" and not os.path.exists(arc):
    os.mkfifo(arc)

t0 = time.monotonic()
ARMED["on"] = True
try:
    try:
        got = kl.verify_archive_member(arc, asset, MEMBER, server, size_good)
        nargs = 5
    except TypeError as exc:
        if "positional argument" not in str(exc):
            raise
        got = kl.verify_archive_member(arc, asset, MEMBER, server)
        nargs = 4
    out = {"outcome": "ok", "result": got}
except kl.SetupError as exc:
    out = {"outcome": "refused", "token": exc.code}
except BaseException as exc:  # noqa: BLE001
    out = {"outcome": "uncaught", "exc": f"{type(exc).__name__}: {exc}"}
ARMED["on"] = False
dt = time.monotonic() - t0
out.update(case=a.case, seconds=round(dt, 3), hashed_archive=COUNT["arc"],
           hashed_member=COUNT["mem"],
           archive_bytes=os.path.getsize(arc)
           if os.path.isfile(arc) and not os.path.islink(arc) else None,
           rss_hwm_kb=int(open("/proc/self/status").read().split("VmHWM:")[1].split()[0]))
out["nargs"] = locals().get("nargs")
checkpoint()
print(json.dumps(out), flush=True)
