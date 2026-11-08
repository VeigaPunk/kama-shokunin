#!/usr/bin/env python3
"""round99-autoload-states.py - round-99 C3 (depth) frozen counter.

PREDICATE (same sentence as plans/round-99-claims.md section C3):

    `python3 tools/round99-autoload-states.py --repo . --rev <M3> --work <scratch>`
    prints `AUTOLOAD_STATES99 cells=8 mismatches=0 base_mismatches=7 flips=7 stable=1 met=True
    rev=<resolved> probe_sha256=<sha>` and exits 0 at M3 (the amendment-1 commit).

    Before (do-nothing control): `--rev 439fdb3d` (the same counter against the base probe)
    prints `mismatches=7 base_mismatches=7 flips=0 stable=8 met=False` and exits 1 — the seven
    unread `/props` cells read `router-unloaded`, as if autoload had answered "off".

The eight live cells run the lane's own probe against a stub router on a free loopback port. Each
stub serves `/v1/models` with one `unloaded`, not-failed entry whose `status.args[0]` is an existing
local file, and a different `/props` answer per cell. Each cell grades (verdict, reason, exit):

  U1-slow-props          valid autoload-true body after a 6.5 s delay (probe default --timeout 5)
  U2-oversize-props      a 4.5 MiB body (over the probe's 4 MiB cap)
  U3-nonjson-props       an HTML body (not JSON)
  U4-nonrouter-props     `{"status":"ok"}`: valid JSON, no router role, no autoload field
  U5-field-absent        `{"role":"router"}`: a router document with no models_autoload field
  U6-field-nonboolean    `{"role":"router","models_autoload":"false"}`: a string, not a boolean
  U7-wrong-role          `{"role":"worker","models_autoload":false}`: a non-router document
                         U1-U7 tip MODEL_UNLOADED/router-autoload-unread exit 2;
                         base MODEL_UNLOADED/router-unloaded exit 2
  P1-autoload-off        `{"role":"router","models_autoload":false}`: an explicit off
                         tip and base MODEL_UNLOADED/router-unloaded exit 2 (positive control:
                         a blanket rename of every unread-or-off answer fails this cell)

Grounding (SOURCES.md): S624 `tools/server/server-models.cpp:2030` builds the bare `/props` body
with `{"models_autoload", params.models_autoload}`; S625 `common/common.h:705` defaults the field
to `true`, so an "off" answer is an explicit `--no-models-autoload` state, never an absence. A
reader that could not read the answer therefore has no evidence of "off" and must say so.

Exit: 0 predicate met | 1 not met | 2 could-not-evaluate | 64 usage.
"""

import argparse
import hashlib
import os
import http.server
import json
import re
import shutil
import socket
import subprocess
import sys
import tempfile
import threading
import time
from pathlib import Path

BASE = "439fdb3d41b55e5b9e6d7c480d17f2c428bae978"
EXPECT_ID = "fixture-model"
UNREAD = ("MODEL_UNLOADED", "router-autoload-unread", 2)
OFF = ("MODEL_UNLOADED", "router-unloaded", 2)
SLOW_DELAY = 6.5


class Handler(http.server.BaseHTTPRequestHandler):
    scenario = "off"

    def log_message(self, *a):  # noqa: D401 - silence
        pass

    def do_GET(self):  # noqa: N802
        if self.path.split("?")[0] == "/v1/models":
            body = json.dumps({
                "object": "list",
                "data": [{"id": EXPECT_ID,
                          "status": {"value": "unloaded",
                                     "args": [self.server.model_file, "-m", self.server.model_file]}}],
            }).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return
        if self.path.split("?")[0] != "/props":
            self.send_response(404)
            self.send_header("Content-Length", "0")
            self.end_headers()
            return
        if self.scenario == "slow":
            time.sleep(SLOW_DELAY)
            body = b'{"role":"router","models_autoload":true}'
            ctype = "application/json"
        elif self.scenario == "oversize":
            body = b'{"role":"router","models_autoload":true,"pad":"' + b"x" * (4_500_000) + b'"}'
            ctype = "application/json"
        elif self.scenario == "nonjson":
            body = b"<html><body>props not here</body></html>"
            ctype = "text/html"
        elif self.scenario == "nonrouter":
            body = b'{"status":"ok"}'
            ctype = "application/json"
        elif self.scenario == "roleonly":
            body = b'{"role":"router"}'
            ctype = "application/json"
        elif self.scenario == "strfalse":
            body = b'{"role":"router","models_autoload":"false"}'
            ctype = "application/json"
        elif self.scenario == "wrongrole":
            body = b'{"role":"worker","models_autoload":false}'
            ctype = "application/json"
        else:  # off
            body = b'{"role":"router","models_autoload":false}'
            ctype = "application/json"
        self.send_response(200)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        try:
            self.wfile.write(body)
        except (BrokenPipeError, ConnectionResetError):
            pass


class Stub(http.server.ThreadingHTTPServer):
    daemon_threads = True
    allow_reuse_address = True

    def __init__(self, scenario: str, model_file: str):
        super().__init__(("127.0.0.1", 0), Handler)
        self.scenario = scenario
        self.model_file = model_file

    def handler_scenario(self):
        h = Handler
        h.scenario = self.scenario
        return h


def verdict_reason(probe: Path, port: int, work: Path, timeout: int):
    cmd = ["bash", str(probe), "check", "--port", str(port), "--expect", EXPECT_ID,
           "--id", "r99", "--json"]
    env = dict(os.environ)
    env["TMPDIR"] = str(work)   # keep the probe's own mktemp files under the counter's scratch
    p = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, env=env)
    text = p.stdout
    try:
        doc = json.loads(text)
    except json.JSONDecodeError:
        raise RuntimeError(f"probe printed no JSON (rc={p.returncode}): {text[:200]!r} {p.stderr[:200]!r}")
    rows = doc.get("rows") or []
    if not rows:
        raise RuntimeError("probe JSON has no rows")
    row = rows[0]
    return row.get("verdict"), row.get("reason"), p.returncode


CELLS = [("U1-slow-props", "slow", UNREAD, "MODEL_UNLOADED/router-autoload-unread/2"),
         ("U2-oversize-props", "oversize", UNREAD, "MODEL_UNLOADED/router-autoload-unread/2"),
         ("U3-nonjson-props", "nonjson", UNREAD, "MODEL_UNLOADED/router-autoload-unread/2"),
         ("U4-nonrouter-props", "nonrouter", UNREAD, "MODEL_UNLOADED/router-autoload-unread/2"),
         ("U5-field-absent", "roleonly", UNREAD, "MODEL_UNLOADED/router-autoload-unread/2"),
         ("U6-field-nonboolean", "strfalse", UNREAD, "MODEL_UNLOADED/router-autoload-unread/2"),
         ("U7-wrong-role", "wrongrole", UNREAD, "MODEL_UNLOADED/router-autoload-unread/2"),
         ("P1-autoload-off", "off", OFF, "MODEL_UNLOADED/router-unloaded/2")]


def run_pass(probe: Path, tag: str, work: Path):
    out = {}
    for cid, scenario, _want, _label in CELLS:
        stub = Stub(scenario, str(work / "model.gguf"))
        stub.RequestHandlerClass = stub.handler_scenario()
        th = threading.Thread(target=stub.serve_forever, daemon=True)
        th.start()
        port = stub.server_address[1]
        try:
            got = verdict_reason(probe, port, work, timeout=300)
        finally:
            stub.shutdown()
            stub.server_close()
            th.join(timeout=5)
        out[cid] = got
        print(f"AUTOLOAD_STATES99_CELL {tag} {cid} scenario={scenario} "
              f"verdict={got[0]} reason={got[1]} exit={got[2]}", flush=True)
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", type=Path, required=True)
    ap.add_argument("--rev", required=True)
    ap.add_argument("--probe-file", type=Path,
                    help="grade a candidate probe instead of the file at --rev (freeze control only)")
    ap.add_argument("--work", type=Path, required=True)
    a = ap.parse_args()

    def git(*args):
        p = subprocess.run(["git", "-C", str(a.repo), *args], capture_output=True)
        if p.returncode != 0:
            raise RuntimeError(f"git {' '.join(args)} rc={p.returncode}")
        return p.stdout

    a.work.mkdir(parents=True, exist_ok=True)
    work = Path(tempfile.mkdtemp(prefix="r99-autoload-", dir=a.work)).resolve()
    try:
        rev = git("rev-parse", "--verify", a.rev + "^{commit}").decode().strip()
        base_bytes = git("show", f"{BASE}:tools/kama-probe.sh")
        tip_bytes = a.probe_file.read_bytes() if a.probe_file else git("show", f"{rev}:tools/kama-probe.sh")
        (work / "model.gguf").write_bytes(b"GGUF\x03\x00\x00\x00" + b"\x00" * 64)
        base_probe = work / "probe-base.sh"
        tip_probe = work / "probe-tip.sh"
        base_probe.write_bytes(base_bytes)
        tip_probe.write_bytes(tip_bytes)
        base = run_pass(base_probe, "base", work)
        tip = run_pass(tip_probe, "tip", work)
    except (RuntimeError, subprocess.TimeoutExpired) as e:
        shutil.rmtree(work, ignore_errors=True)
        print(f"AUTOLOAD_STATES99 could-not-evaluate: {e}")
        return 2
    finally:
        shutil.rmtree(work, ignore_errors=True)

    mismatches = 0
    base_mismatches = 0
    flips = 0
    stable = 0
    for cid, _scenario, want, label in CELLS:
        got = tuple(tip[cid])
        if got != want:
            mismatches += 1
            print(f"AUTOLOAD_STATES99_MISMATCH {cid} want={label} "
                  f"got={got[0]}/{got[1]}/{got[2]}")
        bgot = tuple(base[cid])
        if bgot != want:
            base_mismatches += 1
        if got != bgot:
            flips += 1
        else:
            stable += 1
    met = mismatches == 0
    print(f"AUTOLOAD_STATES99 cells={len(CELLS)} mismatches={mismatches} "
          f"base_mismatches={base_mismatches} flips={flips} stable={stable} met={met} "
          f"rev={rev} probe_sha256={hashlib.sha256(tip_bytes).hexdigest()} "
          f"base_sha256={hashlib.sha256(base_bytes).hexdigest()} "
          f"candidate={'yes' if a.probe_file else 'no'}")
    return 0 if met else 1


if __name__ == "__main__":
    sys.exit(main())
