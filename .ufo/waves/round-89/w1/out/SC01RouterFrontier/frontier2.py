#!/usr/bin/env python3
"""SC01RouterFrontier experiment 2: alias entry file-state, alias vs canonical body,
per-request autoload on a no-autoload router, margin on a no-autoload router."""
from __future__ import annotations

import json
import os
import signal
import socket
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from frontier import (SERVER, MODEL, WORK, PROBE, OUT, CHILDREN, kill_children,  # noqa: E402
                      free_port, http, start, probe, rec)


def main():
    signal.signal(signal.SIGTERM, kill_children)
    signal.signal(signal.SIGINT, kill_children)
    WORK.mkdir(parents=True, exist_ok=True)
    models = WORK / "models2"
    models.mkdir(exist_ok=True)
    raw = MODEL.read_bytes()
    (models / "m1.gguf").write_bytes(raw)

    # --- E: preset alias entry, then delete its model file -> probe on canonical id
    d = WORK / "e"
    d.mkdir(exist_ok=True)
    (d / "alias-model.gguf").write_bytes(raw)
    ini = d / "presets.ini"
    ini.write_text(f"[kama-alias-model]\nmodel = {d/'alias-model.gguf'}\nalias = kama-alias-x\n")
    pe = start(["--models-max", "1", "--models-dir", str(models), "--models-preset", str(ini)],
               d, d / "router.log")
    code, txt = http("GET", pe, "/v1/models")
    rec("E-models-list-full", {"port": pe, "http": code, "body": json.loads(txt) if code == 200 else txt[:400]})
    (d / "alias-model.gguf").unlink()
    code, txt = http("GET", pe, "/v1/models")
    rec("E-models-list-after-delete", {"port": pe, "http": code,
                                       "body": json.loads(txt) if code == 200 else txt[:400]})
    for expect in ("kama-alias-model", "kama-alias-x"):
        rc, verdict, reason, served = probe(pe, expect, WORK)
        rec(f"E-probe-expect-{expect}", {"port": pe, "exit": rc, "verdict": verdict,
                                         "reason": reason, "served": served})
    # completion with the alias on a deleted model file
    code, txt = http("POST", pe, "/v1/chat/completions",
                     {"model": "kama-alias-x", "messages": [{"role": "user", "content": "hi"}], "max_tokens": 2})
    rec("E-completion-alias-deleted-file", {"port": pe, "http": code, "body": txt[:300]})
    kill_children()

    # --- F: no-autoload router: ?autoload=false vs default for a valid unloaded model
    d = WORK / "f"
    d.mkdir(exist_ok=True)
    pf = start(["--no-models-autoload", "--models-max", "1", "--models-dir", str(models)],
               d, d / "router.log")
    for label, path, mid in (("F-m1-default", "/v1/chat/completions", "m1"),
                             ("F-m1-autoload-false", "/v1/chat/completions?autoload=false", "m1"),
                             ("F-m1-autoload-true", "/v1/chat/completions?autoload=true", "m1")):
        code, txt = http("POST", pf, path,
                         {"model": mid, "messages": [{"role": "user", "content": "hi"}], "max_tokens": 2})
        rec(label, {"port": pf, "http": code, "body": txt[:250]})
    kill_children()

    # --- G: memory margin on a no-autoload router + margin>0 with an unloadable entry
    d = WORK / "g"
    d.mkdir(exist_ok=True)
    noise = b"".join(hashlib_sha(b"kama-r89-frontier-%d" % i) for i in range(128))
    (models / "badhdr.gguf").write_bytes(b"GGUF" + (3).to_bytes(4, "little") + noise)
    pg = start(["--models-max", "1", "--models-dir", str(models), "--models-memory-margin", "1024"],
               d, d / "router.log")
    time.sleep(3)
    code, txt = http("GET", pg, "/v1/models")
    rec("G-models-list-margin", {"port": pg, "http": code,
                                 "body": json.loads(txt) if code == 200 else txt[:400]})
    code, txt = http("POST", pg, "/v1/chat/completions",
                     {"model": "m1", "messages": [{"role": "user", "content": "hi"}], "max_tokens": 2})
    rec("G-completion-margin", {"port": pg, "http": code, "body": txt[:200]})
    code, txt = http("GET", pg, "/v1/models")
    rec("G-models-list-margin-after", {"port": pg, "http": code,
                                       "body": json.loads(txt) if code == 200 else txt[:400]})
    rec("G-router-log", {"log": (d / "router.log").read_text()[-3000:]})
    kill_children()
    return 0


def hashlib_sha(x):
    import hashlib
    return hashlib.sha256(x).digest()


if __name__ == "__main__":
    try:
        sys.exit(main())
    finally:
        kill_children()
