#!/usr/bin/env python3
"""SC01RouterFrontier experiment 4:
 K: no-autoload router, valid unloaded model -> probe verdict + wire answer.
 L: autoload router, valid unloaded model, ?autoload=false -> probe verdict (MODEL_OK
    router-unloaded-autoload) vs the wire answer (400 model is not loaded).
 M: autoload router, unloadable model, ?autoload=false -> wire answer 400, and the
    probe verdict on the same entry.
"""
from __future__ import annotations

import hashlib
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
    models = WORK / "models4"
    models.mkdir(parents=True, exist_ok=True)
    (models / "m1.gguf").write_bytes(MODEL.read_bytes())
    noise = b"".join(hashlib.sha256(b"kama-r89-f4-%d" % i).digest() for i in range(128))
    (models / "badhdr.gguf").write_bytes(b"GGUF" + (3).to_bytes(4, "little") + noise)

    d = WORK / "k"
    d.mkdir(exist_ok=True)
    pk = start(["--no-models-autoload", "--models-max", "1", "--models-dir", str(models)],
               d, d / "router.log")
    rc, verdict, reason, served = probe(pk, "m1", WORK)
    rec("K-probe-noautoload-valid", {"port": pk, "exit": rc, "verdict": verdict,
                                     "reason": reason, "served": served})
    code, txt = http("POST", pk, "/v1/chat/completions",
                     {"model": "m1", "messages": [{"role": "user", "content": "hi"}], "max_tokens": 2})
    rec("K-wire-noautoload-valid", {"port": pk, "http": code, "body": txt[:200]})
    kill_children()

    d = WORK / "l"
    d.mkdir(exist_ok=True)
    pl = start(["--models-max", "1", "--models-dir", str(models)], d, d / "router.log")
    rc, verdict, reason, served = probe(pl, "m1", WORK)
    rec("L-probe-autoload-valid", {"port": pl, "exit": rc, "verdict": verdict,
                                   "reason": reason, "served": served})
    code, txt = http("POST", pl, "/v1/chat/completions?autoload=false",
                     {"model": "m1", "messages": [{"role": "user", "content": "hi"}], "max_tokens": 2})
    rec("L-wire-autoload-false-valid", {"port": pl, "http": code, "body": txt[:200]})
    code, txt = http("POST", pl, "/v1/chat/completions?autoload=false",
                     {"model": "badhdr", "messages": [{"role": "user", "content": "hi"}], "max_tokens": 2})
    rec("L-wire-autoload-false-badhdr", {"port": pl, "http": code, "body": txt[:250]})
    rc, verdict, reason, served = probe(pl, "badhdr", WORK)
    rec("L-probe-badhdr", {"port": pl, "exit": rc, "verdict": verdict, "reason": reason,
                           "served": served})
    code, txt = http("GET", pl, "/v1/models")
    rec("L-models-after", {"port": pl, "http": code, "body": txt[:900]})
    kill_children()
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    finally:
        kill_children()
