#!/usr/bin/env python3
"""Fake live tool for replay host-safety probes (scratch only).

Modes via KAMA_FAKE_MODE:
  match  - write a v4 receipt whose digests/checks match the original
  sleep  - spawn a grandchild 'sleep 30' (no pdeathsig) and sleep
Records argv/env to KAMA_SEN2_RECORD.
"""
import hashlib
import json
import os
import subprocess
import sys
import time


def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as fh:
        for c in iter(lambda: fh.read(1 << 20), b""):
            h.update(c)
    return h.hexdigest()


a = sys.argv
g = lambda n, d=None: a[a.index(n) + 1] if n in a else d  # noqa: E731
out, server, model = g("--out"), g("--server"), g("--model")
record = os.environ.get("KAMA_SEN2_RECORD")
mode = os.environ.get("KAMA_FAKE_MODE", "match")
kid = None
if mode == "sleep":
    kid = subprocess.Popen(["sleep", "30"]).pid
rec = {
    "schema": "kama-llamacpp-live/v4", "outcome": "pass",
    "alias": g("--alias"), "ctx": int(g("--ctx", "256")), "threads": int(g("--threads", "1")),
    "server": {"sha256": sha(server), "realpath": os.path.realpath(server)},
    "model": {"sha256": sha(model), "path": os.path.realpath(model)},
    "checks": [{"id": "health_ready", "passed": True, "evaluated": True}],
    "provenance": {"server": {"asset_url": g("--server-asset-url"),
                              "asset_sha256": g("--server-asset-sha256"),
                              "member": g("--server-member")},
                   "model": {"url": g("--model-url"), "sha256": g("--model-sha256")}},
    "env": {k: os.environ.get(k) for k in ("TMPDIR", "HOME", "KAMA_SEN2_SENTINEL",
                                           "LD_PRELOAD", "PYTHONPATH")},
    "argv": a[1:], "cwd": os.getcwd(), "pid": os.getpid(), "grandchild": kid,
}
if record:
    with open(record, "w") as fh:
        json.dump(rec, fh, indent=1)
if mode == "sleep":
    time.sleep(30)
with open(out, "w") as fh:
    json.dump(rec, fh)
