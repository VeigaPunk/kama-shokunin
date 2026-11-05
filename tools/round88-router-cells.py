#!/usr/bin/env python3
"""round88-router-cells.py - kama round-88 C1 (operability) counter.

Grades `tools/kama-probe.sh` at a git revision against llama.cpp router-mode
`/v1/models` status objects (llama.cpp tools/server/README.md router section,
SOURCES S581). The probe bytes executed are `git show <rev>:tools/kama-probe.sh`,
copied into the scratch dir; the worktree copy is never run. `--probe-file`
replaces them for controls only and the summary then says `probe=override`.

Cells: 14 canned stub cells (CANNED) and 3 live cells on a pinned llama-server
b11755 router child started with --no-models-autoload. A live cell's expected
verdict comes from an oracle run right after the probe: a real
POST /v1/chat/completions for the model (200 -> MODEL_OK; 400 "model is not
loaded" -> MODEL_UNLOADED; anything else -> could-not-evaluate).

Output: one `ROUTER_CELL <id> expected=<V> observed=<V> reason=<r> ok=<0|1>` per
cell, then `ROUTER_CELLS cells=17 mismatches=<n> canned=14 live=3
probe=<rev|override> probe_sha256=<hex>`. Exit 0 iff mismatches=0, 1 if
mismatches>0, 2 could-not-evaluate (pinned binary/model absent, oracle
inconclusive, CLI misuse). Scratch lives under --work (default $TMPDIR) and is
removed on exit.
"""
from __future__ import annotations

import argparse
import hashlib
import http.server
import json
import os
from pathlib import Path
import shutil
import socket
import subprocess
import sys
import tempfile
import threading
import time
import urllib.error
import urllib.request

SERVER = Path.home() / ".local/opt/llama-b11755/llama-server"
SERVER_SHA = "b6a31a8e97615a2a1445aeba51e6411e7b02f0a5fa554559347239ee860cd804"
MODEL = Path.home() / ".cache/kama-shokunin/models/stories260K.gguf"
MODEL_SHA = "270cba1bd5109f42d03350f60406024560464db173c0e387d91f0426d3bd256d"
MODEL_ID = "stories260K"


class CannotEvaluate(Exception):
    pass


def entry(mid, status=None):
    e = {"id": mid, "object": "model", "owned_by": "llamacpp"}
    if status is not None:
        e["status"] = status
    return e


ARGS = ["llama-server", "-ctx", "4096"]
# id, expect flag, data[] entries, expected verdict
CANNED = [
    ("C01-loaded", "m1", [entry("m1", {"value": "loaded", "args": ARGS})], "MODEL_OK"),
    ("C02-unloaded", "m1", [entry("m1", {"value": "unloaded"})], "MODEL_UNLOADED"),
    ("C03-loading", "m1", [entry("m1", {"value": "loading", "args": ARGS})], "MODEL_LOADING"),
    ("C04-failed", "m1", [entry("m1", {"value": "unloaded", "args": ARGS, "failed": True, "exit_code": 1})],
     "MODEL_UNLOADED"),
    ("C05-sleeping", "m1", [entry("m1", {"value": "sleeping", "args": ARGS})], "MODEL_UNLOADED"),
    ("C06-downloading", "m1", [entry("m1", {"value": "downloading",
                                             "progress": {"https://h/m1.gguf": {"done": 1, "total": 9}}})],
     "MODEL_LOADING"),
    ("C07-incomplete", "m1", [entry("m1", {"value": "incomplete", "args": []})], "MODEL_UNLOADED"),
    ("C08-single-model", "m1", [entry("m1")], "MODEL_OK"),
    ("C09-expected-loaded-other-unloaded", "m1",
     [entry("m2", {"value": "unloaded"}), entry("m1", {"value": "loaded", "args": ARGS})], "MODEL_OK"),
    ("C10-expected-unloaded-other-loaded", "m1",
     [entry("m1", {"value": "unloaded"}), entry("m2", {"value": "loaded", "args": ARGS})], "MODEL_UNLOADED"),
    ("C11-expected-absent", "m9", [entry("m1", {"value": "loaded", "args": ARGS})], "MODEL_MISMATCH"),
    ("C12-wildcard-none-loaded", "*",
     [entry("m1", {"value": "unloaded"}), entry("m2", {"value": "sleeping"})], "MODEL_UNLOADED"),
    ("C13-wildcard-one-loaded", "*",
     [entry("m1", {"value": "unloaded"}), entry("m2", {"value": "loaded", "args": ARGS})], "MODEL_OK"),
    ("C14-unknown-value", "m1", [entry("m1", {"value": "warming"})], "MODEL_UNLOADED"),
]


def sha256(path: Path) -> str:
    with path.open("rb") as f:
        return hashlib.file_digest(f, "sha256").hexdigest()


def free_port() -> int:
    s = socket.socket()
    s.bind(("127.0.0.1", 0))
    p = s.getsockname()[1]
    s.close()
    return p


def stub(body: dict):
    raw = json.dumps({"object": "list", "data": body}).encode()

    class H(http.server.BaseHTTPRequestHandler):
        def do_GET(self):
            if self.path.split("?")[0] == "/v1/models":
                out, ct = raw, "application/json; charset=utf-8"
            elif self.path.split("?")[0] == "/health":
                out, ct = b'{"status":"ok"}', "application/json; charset=utf-8"
            else:
                self.send_response(404)
                self.end_headers()
                return
            self.send_response(200)
            self.send_header("Content-Type", ct)
            self.send_header("Content-Length", str(len(out)))
            self.end_headers()
            self.wfile.write(out)

        def version_string(self):
            return "llama.cpp"

        def log_message(self, *a):
            pass

    srv = http.server.ThreadingHTTPServer(("127.0.0.1", 0), H)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return srv


def run_probe(probe: Path, port: int, expect: str, env: dict):
    p = subprocess.run(["bash", str(probe), "check", "--port", str(port), "--expect", expect, "--json",
                        "--timeout", "3", "--connect-timeout", "1"],
                       capture_output=True, text=True, timeout=60, env=env)
    try:
        doc = json.loads(p.stdout)
        row = (doc.get("consumers") or doc.get("rows") or doc.get("results") or [])[0]
        return row.get("verdict", "?"), row.get("reason", "?")
    except Exception:
        return "UNPARSEABLE", f"exit{p.returncode}"


def http_json(method: str, url: str, body=None, timeout=10):
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(url, data=data, method=method,
                                 headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, r.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode("utf-8", "replace")


def status_of(port: int) -> str:
    _, txt = http_json("GET", f"http://127.0.0.1:{port}/v1/models")
    for e in json.loads(txt).get("data", []):
        if e.get("id") == MODEL_ID:
            return (e.get("status") or {}).get("value", "")
    return ""


def wait_status(port: int, want: str, secs: float = 60) -> None:
    end = time.time() + secs
    while time.time() < end:
        try:
            if status_of(port) == want:
                return
        except Exception:
            pass
        time.sleep(0.25)
    raise CannotEvaluate(f"router never reported status {want}")


def oracle(port: int) -> str:
    code, txt = http_json("POST", f"http://127.0.0.1:{port}/v1/chat/completions",
                          {"model": MODEL_ID, "messages": [{"role": "user", "content": "hi"}], "max_tokens": 2},
                          timeout=30)
    if code == 200:
        return "MODEL_OK"
    if code == 400 and "model is not loaded" in txt:
        return "MODEL_UNLOADED"
    raise CannotEvaluate(f"oracle inconclusive http={code} body={txt[:120]!r}")


def live_cells(probe: Path, work: Path, env: dict):
    for path, want in ((SERVER, SERVER_SHA), (MODEL, MODEL_SHA)):
        if not path.is_file():
            raise CannotEvaluate(f"pinned prerequisite absent: {path} (run tools/fetch-pinned-model.py)")
        if sha256(path) != want:
            raise CannotEvaluate(f"pinned prerequisite sha256 mismatch: {path}")
    models = work / "models"
    models.mkdir()
    shutil.copyfile(MODEL, models / f"{MODEL_ID}.gguf")
    port = free_port()
    log = (work / "router.log").open("w")
    child = subprocess.Popen([str(SERVER), "--models-dir", str(models), "--no-models-autoload",
                              "--models-max", "1", "--host", "127.0.0.1", "--port", str(port)],
                             stdout=log, stderr=subprocess.STDOUT, cwd=work, start_new_session=True)
    out = []
    try:
        wait_status(port, "unloaded", 30)
        steps = [("L01-router-unloaded", None),
                 ("L02-router-loaded", ("/models/load", "loaded")),
                 ("L03-router-unloaded-again", ("/models/unload", "unloaded"))]
        for cid, act in steps:
            if act:
                code, txt = http_json("POST", f"http://127.0.0.1:{port}{act[0]}", {"model": MODEL_ID})
                if code != 200:
                    raise CannotEvaluate(f"{act[0]} http={code} {txt[:120]!r}")
                wait_status(port, act[1])
            got, reason = run_probe(probe, port, MODEL_ID, env)
            exp = oracle(port)
            out.append((cid, exp, got, reason))
    finally:
        try:
            os.killpg(child.pid, 15)
        except ProcessLookupError:
            pass
        try:
            child.wait(timeout=15)
        except subprocess.TimeoutExpired:
            os.killpg(child.pid, 9)
            child.wait()
        log.close()
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--repo", type=Path, default=Path("."))
    ap.add_argument("--rev", required=True)
    ap.add_argument("--work", type=Path, default=None, help="scratch parent (default $TMPDIR)")
    ap.add_argument("--probe-file", type=Path, default=None, help="controls only: run these bytes instead")
    a = ap.parse_args()
    parent = a.work or Path(tempfile.gettempdir())
    parent.mkdir(parents=True, exist_ok=True)
    work = Path(tempfile.mkdtemp(prefix="router-cells-", dir=parent))
    try:
        probe = work / "kama-probe.sh"
        if a.probe_file:
            shutil.copyfile(a.probe_file, probe)
            label = "override"
        else:
            r = subprocess.run(["git", "-C", str(a.repo), "show", f"{a.rev}:tools/kama-probe.sh"],
                               capture_output=True)
            if r.returncode != 0:
                print(f"ROUTER_CELLS could-not-evaluate: git show {a.rev}:tools/kama-probe.sh failed")
                return 2
            probe.write_bytes(r.stdout)
            label = "rev"
        env = dict(os.environ, TMPDIR=str(work))
        rows = []
        for cid, expect, data, exp in CANNED:
            srv = stub(data)
            try:
                got, reason = run_probe(probe, srv.server_address[1], expect, env)
            finally:
                srv.shutdown()
                srv.server_close()
            rows.append((cid, exp, got, reason))
        try:
            rows += live_cells(probe, work, env)
        except CannotEvaluate as e:
            for cid, exp, got, reason in rows:
                print(f"ROUTER_CELL {cid} expected={exp} observed={got} reason={reason} ok={int(exp == got)}")
            print(f"ROUTER_CELLS could-not-evaluate: {e}")
            return 2
        bad = 0
        for cid, exp, got, reason in rows:
            ok = exp == got
            bad += not ok
            print(f"ROUTER_CELL {cid} expected={exp} observed={got} reason={reason} ok={int(ok)}")
        live = sum(1 for r in rows if r[0].startswith("L"))
        print(f"ROUTER_CELLS cells={len(rows)} mismatches={bad} canned={len(CANNED)} live={live} "
              f"probe={label} probe_sha256={sha256(probe)}")
        return 0 if bad == 0 else 1
    finally:
        shutil.rmtree(work, ignore_errors=True)


if __name__ == "__main__":
    sys.exit(main())
