#!/usr/bin/env python3
"""SC01RouterFrontier live recon: aliases, --models-memory-margin, ?autoload=false.

Read-only against the lane repo; all children are lane-owned llama-server instances
started on free loopback ports and killed by process group.
"""
from __future__ import annotations

import hashlib
import json
import os
import shutil
import signal
import socket
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

SERVER = Path.home() / ".local/opt/llama-b12177/llama-server"
MODEL = Path.home() / ".cache/kama-shokunin/models/stories260K.gguf"
WORK = Path(os.environ["FRONTIER_WORK"])
PROBE = Path(os.environ["FRONTIER_PROBE"])
OUT = Path(os.environ["FRONTIER_OUT"])

CHILDREN: list[subprocess.Popen] = []


def kill_children(*_a):
    for p in CHILDREN:
        if p.poll() is None:
            try:
                os.killpg(p.pid, signal.SIGTERM)
                p.wait(timeout=15)
            except Exception:
                try:
                    os.killpg(p.pid, signal.SIGKILL)
                    p.wait(timeout=5)
                except Exception:
                    pass
    CHILDREN.clear()


def on_signal(signum, _frame):
    kill_children()
    sys.exit(128 + signum)


def free_port() -> int:
    s = socket.socket()
    s.bind(("127.0.0.1", 0))
    p = s.getsockname()[1]
    s.close()
    return p


def http(method: str, port: int, path: str, body=None, timeout=120):
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(f"http://127.0.0.1:{port}{path}", data=data, method=method,
                                 headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, r.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode("utf-8", "replace")
    except Exception as e:
        return 0, f"CLIENT-ERROR {type(e).__name__}: {e}"


def start(args, cwd, log):
    port = free_port()
    p = subprocess.Popen([str(SERVER), "--host", "127.0.0.1", "--port", str(port)] + args,
                         stdout=log.open("w"), stderr=subprocess.STDOUT, cwd=cwd,
                         start_new_session=True)
    CHILDREN.append(p)
    for _ in range(240):
        if p.poll() is not None:
            raise RuntimeError(f"child exited rc={p.returncode}; log={log}")
        code, _ = http("GET", port, "/v1/models", timeout=5)
        if code == 200:
            return port
        time.sleep(0.25)
    raise RuntimeError("child never answered GET /v1/models")


def probe(port, expect, cwd):
    p = subprocess.run(["bash", str(PROBE), "check", "--port", str(port), "--expect", expect, "--json",
                        "--timeout", "5", "--connect-timeout", "2"],
                       capture_output=True, text=True, timeout=180, cwd=cwd)
    try:
        doc = json.loads(p.stdout)
        row = (doc.get("consumers") or doc.get("rows") or doc.get("results") or [])[0]
        return p.returncode, row.get("verdict"), row.get("reason"), row.get("served_model")
    except Exception as e:
        return p.returncode, "UNPARSEABLE", f"{e}: {p.stdout[:200]}", ""


def rec(label, obj):
    OUT.mkdir(parents=True, exist_ok=True)
    with (OUT / "frontier.jsonl").open("a") as f:
        f.write(json.dumps({"label": label, **obj}) + "\n")
    print(f"--- {label}: {json.dumps(obj)}")


def main():
    signal.signal(signal.SIGTERM, on_signal)
    signal.signal(signal.SIGINT, on_signal)
    WORK.mkdir(parents=True, exist_ok=True)
    raw = MODEL.read_bytes()
    models = WORK / "models"
    models.mkdir(exist_ok=True)
    (models / "m1.gguf").write_bytes(raw)
    noise = b"".join(hashlib.sha256(b"kama-r89-frontier-%d" % i).digest() for i in range(128))
    (models / "badhdr.gguf").write_bytes(b"GGUF" + (3).to_bytes(4, "little") + noise)

    # ---------------- child A: alias via preset key ----------------
    d = WORK / "a"
    d.mkdir(exist_ok=True)
    ini = d / "presets.ini"
    ini.write_text(f"[kama-alias-model]\nmodel = {models/'m1.gguf'}\nalias = kama-alias-x\n")
    pa = start(["--models-max", "1", "--models-dir", str(models), "--models-preset", str(ini)],
               d, d / "router.log")
    code, txt = http("GET", pa, "/v1/models")
    entries = json.loads(txt).get("data", []) if code == 200 else []
    rec("A-models-list", {"port": pa, "http": code,
                          "entries": [{"id": e.get("id"), "aliases": e.get("aliases"),
                                       "status": (e.get("status") or {}).get("value"),
                                       "source": e.get("source")} for e in entries]})
    # completion with the alias
    for mid in ("kama-alias-x", "kama-alias-model"):
        code, txt = http("POST", pa, "/v1/chat/completions",
                         {"model": mid, "messages": [{"role": "user", "content": "hi"}], "max_tokens": 2})
        rec(f"A-completion-{mid}", {"port": pa, "http": code, "body": txt[:300]})
    # probe verdicts
    for expect in ("kama-alias-x", "kama-alias-model"):
        rc, verdict, reason, served = probe(pa, expect, WORK)
        rec(f"A-probe-expect-{expect}", {"port": pa, "exit": rc, "verdict": verdict,
                                         "reason": reason, "served": served})
    # props
    code, txt = http("GET", pa, "/props")
    rec("A-props", {"port": pa, "http": code, "body": txt[:400]})
    kill_children()

    # ---------------- child B: --alias on the command line ----------------
    d = WORK / "b"
    d.mkdir(exist_ok=True)
    pb = start(["--models-max", "1", "--models-dir", str(models), "--alias", "kama-alias-cli"],
               d, d / "router.log")
    code, txt = http("GET", pb, "/v1/models")
    entries = json.loads(txt).get("data", []) if code == 200 else []
    rec("B-models-list", {"port": pb, "http": code,
                          "entries": [{"id": e.get("id"), "aliases": e.get("aliases"),
                                       "status": (e.get("status") or {}).get("value")} for e in entries]})
    for mid in ("kama-alias-cli", "m1"):
        code, txt = http("POST", pb, "/v1/chat/completions",
                         {"model": mid, "messages": [{"role": "user", "content": "hi"}], "max_tokens": 2})
        rec(f"B-completion-{mid}", {"port": pb, "http": code, "body": txt[:300]})
    rc, verdict, reason, served = probe(pb, "kama-alias-cli", WORK)
    rec("B-probe-expect-kama-alias-cli", {"port": pb, "exit": rc, "verdict": verdict,
                                          "reason": reason, "served": served})
    kill_children()

    # ---------------- child C: ?autoload=false on a completion ----------------
    d = WORK / "c"
    d.mkdir(exist_ok=True)
    pc = start(["--models-max", "1", "--models-dir", str(models)], d, d / "router.log")
    code, txt = http("GET", pc, "/v1/models")
    entries = json.loads(txt).get("data", []) if code == 200 else []
    rec("C-models-list", {"port": pc, "http": code,
                          "entries": [{"id": e.get("id"), "aliases": e.get("aliases"),
                                       "status": (e.get("status") or {}).get("value")} for e in entries]})
    # C1: unloadable model, autoload on (default) -> 500 failed to load
    code, txt = http("POST", pc, "/v1/chat/completions",
                     {"model": "badhdr", "messages": [{"role": "user", "content": "hi"}], "max_tokens": 2})
    rec("C-completion-badhdr-default", {"port": pc, "http": code, "body": txt[:300]})
    # C2: unloadable model, per-request ?autoload=false
    code, txt = http("POST", pc, "/v1/chat/completions?autoload=false",
                     {"model": "badhdr", "messages": [{"role": "user", "content": "hi"}], "max_tokens": 2})
    rec("C-completion-badhdr-autoload-false", {"port": pc, "http": code, "body": txt[:300]})
    # C3: valid but unloaded model, per-request ?autoload=false
    code, txt = http("POST", pc, "/v1/chat/completions?autoload=false",
                     {"model": "m1", "messages": [{"role": "user", "content": "hi"}], "max_tokens": 2})
    rec("C-completion-m1-autoload-false", {"port": pc, "http": code, "body": txt[:300]})
    # C4: valid but unloaded model, default autoload -> 200
    code, txt = http("POST", pc, "/v1/chat/completions",
                     {"model": "m1", "messages": [{"role": "user", "content": "hi"}], "max_tokens": 2})
    rec("C-completion-m1-default", {"port": pc, "http": code, "body": txt[:300]})
    # C5: now m1 is loaded; ?autoload=false on a loaded model
    code, txt = http("POST", pc, "/v1/chat/completions?autoload=false",
                     {"model": "m1", "messages": [{"role": "user", "content": "hi"}], "max_tokens": 2})
    rec("C-completion-m1-loaded-autoload-false", {"port": pc, "http": code, "body": txt[:300]})
    # C6: ?autoload=false with an unknown id
    code, txt = http("POST", pc, "/v1/chat/completions?autoload=false",
                     {"model": "no-such-model", "messages": [{"role": "user", "content": "hi"}], "max_tokens": 2})
    rec("C-completion-unknown-autoload-false", {"port": pc, "http": code, "body": txt[:300]})
    # probe verdicts on this child (m1 loaded now, badhdr unloaded-failed?)
    for expect in ("m1", "badhdr"):
        rc, verdict, reason, served = probe(pc, expect, WORK)
        rec(f"C-probe-expect-{expect}", {"port": pc, "exit": rc, "verdict": verdict,
                                         "reason": reason, "served": served})
    code, txt = http("GET", pc, "/v1/models")
    entries = json.loads(txt).get("data", []) if code == 200 else []
    rec("C-models-list-after", {"port": pc, "http": code,
                                "entries": [{"id": e.get("id"), "status": e.get("status")} for e in entries]})
    kill_children()

    # ---------------- child D: --models-memory-margin on this build ----------------
    d = WORK / "d"
    d.mkdir(exist_ok=True)
    t0 = time.time()
    pd = start(["--models-max", "1", "--models-dir", str(models), "--models-memory-margin", "512"],
               d, d / "router.log")
    t1 = time.time()
    code, txt = http("GET", pd, "/v1/models")
    entries = json.loads(txt).get("data", []) if code == 200 else []
    rec("D-models-list-margin", {"port": pd, "http": code, "startup_s": round(t1 - t0, 2),
                                  "entries": [{"id": e.get("id"), "status": (e.get("status") or {}).get("value"),
                                               "memory": e.get("memory")} for e in entries]})
    time.sleep(5)
    code, txt = http("GET", pd, "/v1/models")
    entries = json.loads(txt).get("data", []) if code == 200 else []
    rec("D-models-list-margin-after-5s", {"port": pd, "http": code,
                                          "entries": [{"id": e.get("id"), "status": (e.get("status") or {}).get("value"),
                                                       "memory": e.get("memory")} for e in entries]})
    code, txt = http("POST", pd, "/v1/chat/completions",
                     {"model": "m1", "messages": [{"role": "user", "content": "hi"}], "max_tokens": 2})
    rec("D-completion-margin", {"port": pd, "http": code, "body": txt[:200]})
    code, txt = http("GET", pd, "/props")
    rec("D-props-margin", {"port": pd, "http": code, "body": txt[:400]})
    kill_children()
    # router log tail
    rec("D-router-log", {"log": (d / "router.log").read_text()[-4000:]})
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    finally:
        kill_children()
