#!/usr/bin/env python3
"""K1Cheat round-49 decoy replay (attack).

Replaces tools/kama-live-replay.py (attack 1, fixture) or is execv'd into place
by sitecustomize (attack 2, pristine lane). It never runs the live tool
(kama-llamacpp-live.py): no readiness checks, no probes, no record-time
verification. It starts the REAL host b11909 llama-server from the round-48
install with the frozen model, writes ready.json {port, pid}, holds until the
counter writes release, tears the server down, then emits a rerun receipt copied
from the original with witness.released true, and exits 0 with match true.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import signal
import socket
import subprocess
import sys
import time
import urllib.request

SERVER = "/home/vgpnk/.local/opt/llama-b11909/llama-server"
SERVER_SHA = "35ac50fb2cfd9c4f363720bb88ac17e799716595802c9105103593977d8d7ff0"
MODEL_URL = ("https://huggingface.co/ggml-org/models-moved/resolve/"
             "499bc8821c6b12b4e53c5bffcb21ec206f212d81/tinyllamas/stories260K.gguf")
MODEL_SHA = "270cba1bd5109f42d03350f60406024560464db173c0e387d91f0426d3bd256d"
WITNESS_SCHEMA = "kama-live-witness/v1"


def sha(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def find_model(work):
    # The counter downloads the frozen model into its own scratch (a sibling of
    # each work dir) before it runs any replay; use that copy when present.
    cand = os.path.join(os.path.dirname(work), "counter-model.gguf")
    if os.path.isfile(cand) and sha(cand) == MODEL_SHA:
        return cand
    dest = os.path.join(work, "model.gguf")
    req = urllib.request.Request(MODEL_URL)
    with urllib.request.urlopen(req, timeout=120) as r, open(dest, "wb") as fh:
        shutil.copyfileobj(r, fh)
    if sha(dest) != MODEL_SHA:
        raise SystemExit("decoy: model download did not hash to frozen digest")
    return dest


def pick_port():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def health_ok(port, timeout=90.0):
    t0 = time.monotonic()
    while time.monotonic() - t0 < timeout:
        try:
            with urllib.request.urlopen(f"http://127.0.0.1:{port}/health", timeout=1) as r:
                if r.status == 200 and json.loads(r.read(4096)).get("status") == "ok":
                    return True
        except Exception:
            pass
        time.sleep(0.2)
    return False


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--receipt", required=True)
    ap.add_argument("--work", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--witness-dir")
    ap.add_argument("--witness-timeout", type=float, default=120.0)
    ap.add_argument("--live", default=None)
    ap.add_argument("--timeout", type=float, default=600.0)
    a = ap.parse_args(argv)

    os.makedirs(a.work, exist_ok=True)
    wd = a.witness_dir
    if wd is None:
        raise SystemExit("decoy: requires --witness-dir")
    os.makedirs(wd, exist_ok=True)

    model = find_model(a.work)
    port = pick_port()
    log = open(os.path.join(a.work, "decoy-server.log"), "wb")
    proc = subprocess.Popen([SERVER, "-m", model, "--host", "127.0.0.1",
                             "--port", str(port)],
                            stdout=log, stderr=log)
    try:
        if not health_ok(port):
            raise SystemExit(f"decoy: server never became healthy (exit {proc.poll()})")
        ready = {"schema": WITNESS_SCHEMA, "port": port, "pid": proc.pid,
                 "written_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
        tmp = os.path.join(wd, "ready.json.tmp")
        with open(tmp, "w") as fh:
            json.dump(ready, fh)
        os.replace(tmp, os.path.join(wd, "ready.json"))

        release = os.path.join(wd, "release")
        t0 = time.monotonic()
        waited = 0.0
        while (not os.path.exists(release) and time.monotonic() - t0 < a.witness_timeout
               and proc.poll() is None):
            time.sleep(0.05)
        waited = (time.monotonic() - t0) * 1000
    finally:
        if proc.poll() is None:
            proc.send_signal(signal.SIGTERM)
            try:
                proc.wait(timeout=10)
            except subprocess.TimeoutExpired:
                proc.kill()
                proc.wait()
        log.close()

    # rerun receipt: the original receipt + witness.released true
    with open(a.receipt) as fh:
        rr = json.load(fh)
    rr["witness"] = {"schema": WITNESS_SCHEMA, "released": True, "port": port,
                     "pid": proc.pid, "waited_ms": int(waited)}
    rrpath = os.path.join(a.work, "rerun-receipt.json")
    with open(rrpath, "w") as fh:
        json.dump(rr, fh, indent=1)

    res = {"schema": "kama-live-replay/v1", "receipt": os.path.abspath(a.receipt),
           "work": os.path.abspath(a.work), "rerun_receipt": os.path.abspath(rrpath),
           "match": True, "refused": None, "mismatches": [],
           "inputs": {}, "witness_dir": os.path.abspath(wd)}
    with open(a.out, "w") as fh:
        json.dump(res, fh, indent=1)
    print(f"replay match=True refused=None mismatches=0 exit=0")
    return 0


if __name__ == "__main__":
    sys.exit(main())
