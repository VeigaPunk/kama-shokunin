#!/usr/bin/env python3
"""round89-router-signatures.py - capture the llama.cpp router's error answers on lane-owned
children of the pinned current release (b12177) into a JSON-lines receipt.

Each line: {"server_sha256", "build", "endpoint", "case", "http", "body"}. Calls (child A default
autoload, child B --no-models-autoload; both --models-max 1, private --models-dir holding a valid
stories260K copy `m1` and an unloadable `badhdr`):
  B POST /v1/chat/completions model=m1 (unloaded)        B POST /models/unload model=m1 (not running)
  A POST /v1/chat/completions model=badhdr (unloadable)  B POST /models/unload model=nope
  A POST /v1/chat/completions model=nope                 B POST /models/load model=nope
  A POST /v1/chat/completions without a model field      B POST /models/load model=m1 twice
The receipt is evidence for the round-89 C2 SKILL rows (`tools/round89-signature-rows.py`).
Children are killed by process group on every exit path.

Usage: round89-router-signatures.py --out FILE --work DIR [--server PATH]
Exit: 0 receipt written | 2 could-not-evaluate (prerequisite absent/mismatched, child failure).
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import shutil
import signal
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("uc", HERE / "round89-unloadable-cells.py")
uc = importlib.util.module_from_spec(spec)
spec.loader.exec_module(uc)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--work", type=Path, required=True)
    ap.add_argument("--server", type=Path, default=uc.SERVER)
    a = ap.parse_args()
    signal.signal(signal.SIGTERM, uc.on_signal)
    signal.signal(signal.SIGINT, uc.on_signal)
    lines = []
    try:
        for path, want in ((a.server, uc.SERVER_PIN), (uc.MODEL, uc.MODEL_SHA)):
            if not path.is_file() or uc.sha256(path) != want:
                raise uc.CannotEvaluate(f"prerequisite absent or mismatched: {path}")
        ver = subprocess.run([str(a.server), "--version"], capture_output=True, text=True, timeout=30)
        build = next((l.strip() for l in (ver.stdout + ver.stderr).splitlines() if l.startswith("version:")), "?")
        a.work.mkdir(parents=True, exist_ok=True)
        work = Path(tempfile.mkdtemp(prefix="r89-signatures-", dir=a.work)).resolve()
        try:
            models = work / "models"
            models.mkdir()
            shutil.copyfile(uc.MODEL, models / "m1.gguf")
            noise = b"".join(hashlib.sha256(b"kama-r89-%d" % i).digest() for i in range(128))
            (models / "badhdr.gguf").write_bytes(b"GGUF" + (3).to_bytes(4, "little") + noise)

            def call(port, child, case, endpoint, body):
                code, txt = uc.http("POST", port, endpoint, body)
                lines.append({"server_sha256": uc.SERVER_PIN, "build": build, "child": child, "case": case,
                              "endpoint": "POST " + endpoint, "request": body, "http": code, "body": txt})

            pa = uc.start(a.server, ["--models-max", "1", "--models-dir", str(models)], work,
                          work / "a.log", str(work))
            chat = "/v1/chat/completions"
            msg = [{"role": "user", "content": "hi"}]
            call(pa, "A-autoload", "unloadable-file", chat, {"model": "badhdr", "messages": msg, "max_tokens": 2})
            call(pa, "A-autoload", "unknown-id", chat, {"model": "nope", "messages": msg, "max_tokens": 2})
            call(pa, "A-autoload", "missing-model-field", chat, {"messages": msg, "max_tokens": 2})
            uc.kill_children()
            pb = uc.start(a.server, ["--no-models-autoload", "--models-max", "1", "--models-dir", str(models)],
                          work, work / "b.log", str(work))
            call(pb, "B-no-autoload", "unloaded", chat, {"model": "m1", "messages": msg, "max_tokens": 2})
            call(pb, "B-no-autoload", "unload-not-running", "/models/unload", {"model": "m1"})
            call(pb, "B-no-autoload", "unload-unknown-id", "/models/unload", {"model": "nope"})
            call(pb, "B-no-autoload", "load-unknown-id", "/models/load", {"model": "nope"})
            call(pb, "B-no-autoload", "load-first", "/models/load", {"model": "m1"})
            uc.wait_status(pb, "m1", "loaded")
            call(pb, "B-no-autoload", "load-already-running", "/models/load", {"model": "m1"})
            uc.kill_children()
        finally:
            uc.kill_children()
            shutil.rmtree(work, ignore_errors=True)
    except uc.CannotEvaluate as e:
        print(f"ROUTER_SIGNATURES could-not-evaluate: {e}")
        return 2
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text("".join(json.dumps(l, sort_keys=True) + "\n" for l in lines))
    print(f"ROUTER_SIGNATURES calls={len(lines)} build={build!r} out={a.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
