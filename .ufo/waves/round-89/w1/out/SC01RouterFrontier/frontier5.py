#!/usr/bin/env python3
"""SC01RouterFrontier experiment 5: alias for a models-dir model via a matching preset
section (the README's "If the key corresponds to an existing model" form), and the
probe verdict for that alias."""
from __future__ import annotations

import os
import signal
import sys
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from frontier import (MODEL, WORK, PROBE, OUT, CHILDREN, kill_children,  # noqa: E402
                      http, start, probe, rec)


def main():
    signal.signal(signal.SIGTERM, kill_children)
    signal.signal(signal.SIGINT, kill_children)
    models = WORK / "models5"
    models.mkdir(parents=True, exist_ok=True)
    (models / "m1.gguf").write_bytes(MODEL.read_bytes())
    d = WORK / "n"
    d.mkdir(exist_ok=True)
    ini = d / "presets.ini"
    ini.write_text("[m1]\nalias = kama-alias-y\n")
    pn = start(["--models-max", "1", "--models-dir", str(models), "--models-preset", str(ini)],
               d, d / "router.log")
    code, txt = http("GET", pn, "/v1/models")
    rec("N-models-list", {"port": pn, "http": code, "body": txt[:900]})
    code, txt = http("POST", pn, "/v1/chat/completions",
                     {"model": "kama-alias-y",
                      "messages": [{"role": "user", "content": "hi"}], "max_tokens": 2})
    rec("N-completion-alias", {"port": pn, "http": code, "body": txt[:250]})
    rc, verdict, reason, served = probe(pn, "kama-alias-y", WORK)
    rec("N-probe-expect-alias", {"port": pn, "exit": rc, "verdict": verdict, "reason": reason,
                                 "served": served})
    rc, verdict, reason, served = probe(pn, "m1", WORK)
    rec("N-probe-expect-canonical", {"port": pn, "exit": rc, "verdict": verdict,
                                     "reason": reason, "served": served})
    kill_children()
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    finally:
        kill_children()
