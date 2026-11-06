#!/usr/bin/env python3
"""SC01RouterFrontier experiment 3:
 H: --models-memory-margin + a MISSING model file -> does the entry become failed=true
    (which would disable the C1 probe's file-state rule)?
 I: alias resolution on POST /models/load and POST /models/unload (error messages).
 J: alias request for an unloadable canonical model -> does the 500 message carry the
    canonical id or the requested alias?
"""
from __future__ import annotations

import hashlib
import json
import os
import signal
import sys
import time
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from frontier import (SERVER, MODEL, WORK, PROBE, OUT, CHILDREN, kill_children,  # noqa: E402
                      free_port, http, start, probe, rec)


def main():
    signal.signal(signal.SIGTERM, kill_children)
    signal.signal(signal.SIGINT, kill_children)
    models = WORK / "models3"
    models.mkdir(parents=True, exist_ok=True)
    raw = MODEL.read_bytes()
    (models / "m1.gguf").write_bytes(raw)
    noise = b"".join(hashlib.sha256(b"kama-r89-f3-%d" % i).digest() for i in range(128))
    (models / "badhdr.gguf").write_bytes(b"GGUF" + (3).to_bytes(4, "little") + noise)

    # --- H: margin > 0 with a missing preset path and a bad-header model
    d = WORK / "h"
    d.mkdir(exist_ok=True)
    ini = d / "presets.ini"
    ini.write_text(f"[gone]\nmodel = {d/'gone.gguf'}\n")
    ph = start(["--models-max", "1", "--models-dir", str(models), "--models-preset", str(ini),
                "--models-memory-margin", "512"], d, d / "router.log")
    time.sleep(4)
    code, txt = http("GET", ph, "/v1/models")
    body = json.loads(txt) if code == 200 else {}
    rec("H-models-list", {"port": ph, "http": code,
                          "entries": [{"id": e.get("id"), "status": e.get("status"),
                                       "memory": (e.get("memory") or {}).get("status")}
                                      for e in body.get("data", [])]})
    for expect in ("gone", "badhdr", "m1"):
        rc, verdict, reason, served = probe(ph, expect, WORK)
        rec(f"H-probe-expect-{expect}", {"port": ph, "exit": rc, "verdict": verdict,
                                         "reason": reason, "served": served})
    rec("H-router-log-tail", {"log": (d / "router.log").read_text()[-2500:]})
    kill_children()

    # --- I/J: alias routing on the load/unload endpoints and the 500 message
    d = WORK / "i"
    d.mkdir(exist_ok=True)
    (d / "alias-model.gguf").write_bytes(raw)
    ini = d / "presets.ini"
    ini.write_text(f"[kama-alias-model]\nmodel = {d/'alias-model.gguf'}\nalias = kama-alias-x\n")
    pi = start(["--models-max", "1", "--models-dir", str(models), "--models-preset", str(ini)],
               d, d / "router.log")
    # unload an alias of a listed model that is not running
    code, txt = http("POST", pi, "/models/unload", {"model": "kama-alias-x"})
    rec("I-unload-alias-not-running", {"port": pi, "http": code, "body": txt[:250]})
    # unload an unknown alias
    code, txt = http("POST", pi, "/models/unload", {"model": "no-such-alias"})
    rec("I-unload-unknown-alias", {"port": pi, "http": code, "body": txt[:250]})
    # load an unknown alias
    code, txt = http("POST", pi, "/models/load", {"model": "no-such-alias"})
    rec("I-load-unknown-alias", {"port": pi, "http": code, "body": txt[:250]})
    # load by alias
    code, txt = http("POST", pi, "/models/load", {"model": "kama-alias-x"})
    rec("I-load-by-alias", {"port": pi, "http": code, "body": txt[:250]})
    time.sleep(2)
    code, txt = http("GET", pi, "/v1/models")
    body = json.loads(txt) if code == 200 else {}
    rec("I-models-list-after-load", {"port": pi, "http": code,
                                     "entries": [{"id": e.get("id"), "aliases": e.get("aliases"),
                                                  "status": (e.get("status") or {}).get("value")}
                                                 for e in body.get("data", [])]})
    kill_children()

    # --- J: alias request against an unloadable canonical model
    d = WORK / "j"
    d.mkdir(exist_ok=True)
    (d / "alias-bad.gguf").write_bytes(b"GGUF" + (3).to_bytes(4, "little") + noise)
    ini = d / "presets.ini"
    ini.write_text(f"[canon-bad]\nmodel = {d/'alias-bad.gguf'}\nalias = kama-alias-bad\n")
    pj = start(["--models-max", "1", "--models-dir", str(models), "--models-preset", str(ini)],
               d, d / "router.log")
    code, txt = http("POST", pj, "/v1/chat/completions",
                     {"model": "kama-alias-bad",
                      "messages": [{"role": "user", "content": "hi"}], "max_tokens": 2})
    rec("J-completion-alias-unloadable", {"port": pj, "http": code, "body": txt[:300]})
    rc, verdict, reason, served = probe(pj, "canon-bad", WORK)
    rec("J-probe-expect-canon", {"port": pj, "exit": rc, "verdict": verdict, "reason": reason,
                                 "served": served})
    rc, verdict, reason, served = probe(pj, "kama-alias-bad", WORK)
    rec("J-probe-expect-alias", {"port": pj, "exit": rc, "verdict": verdict, "reason": reason,
                                 "served": served})
    kill_children()
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    finally:
        kill_children()
