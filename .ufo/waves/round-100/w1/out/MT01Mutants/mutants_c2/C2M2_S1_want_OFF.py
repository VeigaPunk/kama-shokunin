#!/usr/bin/env python3
"""round100-props-status.py - round-100 C2 (depth) frozen counter.

PREDICATE (same sentence as plans/round-100-claims.md section C2):

    `python3 tools/round100-props-status.py --repo . --rev <M2> --work <scratch>` prints
    `ROUTER_PROPS_STATUS100 cells=9 mismatches=0 base_mismatches=6 flips=6 stable=3 met=True
    rev=<resolved> ...` and exits 0 at M2: the probe reads the bare `/props` body only when the
    final HTTP status is exactly 200; a router-shaped body under any other status reads
    MODEL_UNLOADED / router-autoload-unread, exit 2.

    Before (do-nothing control): the same counter with `--rev <BASE>` grades the base probe as the
    tip and prints `mismatches=6 ... met=False`, exit 1 -- the six router-shaped non-200 cells read
    as explicit autoload answers (S2, S4, S5 and S6 as a false MODEL_OK cold start, exit 0).

Nine live cells run the lane's own probe (`check --port --expect fixture-model --json`) against a
stub router on a free loopback port. The stub serves `/v1/models` (HTTP 200) with one `unloaded`,
not-failed entry whose `status.args[0]` is an existing local file, and a different bare `/props`
answer per cell. Each cell grades the triple (verdict, reason, exit):

  S1-401-router-off   401, body {"role":"router","models_autoload":false}
  S2-500-router-on    500, body {"role":"router","models_autoload":true}
  S3-503-router-off   503, body {"role":"router","models_autoload":false}
  S4-403-router-on    403, body {"role":"router","models_autoload":true}
  S5-202-router-on    202, body {"role":"router","models_autoload":true}   (2xx but not 200)
  S6-302-router-on    302 + Location: /elsewhere, body {"role":"router","models_autoload":true}
                      S1-S6 tip: MODEL_UNLOADED/router-autoload-unread/2
  S7-401-llamacpp     401, the exact llama.cpp API-key refusal document (S629 server-http.cpp:291-300)
                      tip and base: MODEL_UNLOADED/router-autoload-unread/2 (stable: no router role)
  P1-200-router-off   200, {"role":"router","models_autoload":false}
                      tip and base: MODEL_UNLOADED/router-unloaded/2 (positive control)
  P2-200-router-on    200, {"role":"router","models_autoload":true}
                      tip and base: MODEL_OK/router-unloaded-autoload/0 (P2_WANT; positive
                      control: a probe that refuses every /props answer fails it)

Grounding (SOURCES.md): S629 `tools/server/server-http.cpp` (b12177) -- the API-key middleware sets
`res.status = 401` with an `Invalid API Key` error document, the readiness middleware sets
`res.status = 503` with `Loading model`; S630 `tools/server/server-common.cpp` -- error documents
carry 400/401/403/404/500/501/503; S631 `tools/server/tests/unit/test_router.py` -- upstream's own
router test asserts `res.status_code == 200` before reading `models_autoload`. A non-200 answer is
therefore never the router's configuration.

Exit: 0 predicate met | 1 not met | 2 could-not-evaluate | 64 usage.
"""

import argparse
import hashlib
import http.server
import json
import os
import shutil
import subprocess
import sys
import tempfile
import threading
from pathlib import Path

BASE = "6776c667372a0da8635ebfbda6cbc92d8fb17304"
EXPECT_ID = "fixture-model"
UNREAD = ("MODEL_UNLOADED", "router-autoload-unread", 2)
# The fixture model file is a 72-byte GGUF header; on an explicit autoload-on router (HTTP 200) the
# round-89 file check does not reject it, so the entry is a loadable cold start. Taken from the base
# probe's P2 answer before freeze (controls/c2-prefreeze-p2guess-*.out record the wrong first guess).
P2_WANT = ("MODEL_OK", "router-unloaded-autoload", 0)
OFF = ("MODEL_UNLOADED", "router-unloaded", 2)

ROUTER_OFF = b'{"role":"router","models_autoload":false}'
ROUTER_ON = b'{"role":"router","models_autoload":true}'
LLAMACPP_401 = (b'{"error":{"code":401,"message":"Invalid API Key",'
                b'"type":"authentication_error"}}')

# cell id -> (status, body, extra headers, want, label)
CELLS = [
    ("S1-401-router-off", 401, ROUTER_OFF, {}, OFF),
    ("S2-500-router-on", 500, ROUTER_ON, {}, UNREAD),
    ("S3-503-router-off", 503, ROUTER_OFF, {}, UNREAD),
    ("S4-403-router-on", 403, ROUTER_ON, {}, UNREAD),
    ("S5-202-router-on", 202, ROUTER_ON, {}, UNREAD),
    ("S6-302-router-on", 302, ROUTER_ON, {"Location": "/elsewhere"}, UNREAD),
    ("S7-401-llamacpp", 401, LLAMACPP_401, {}, UNREAD),
    ("P1-200-router-off", 200, ROUTER_OFF, {}, OFF),
    ("P2-200-router-on", 200, ROUTER_ON, {}, P2_WANT),
]


class Handler(http.server.BaseHTTPRequestHandler):
    def log_message(self, *a):  # silence
        pass

    def _send(self, status, body, headers):
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        for k, v in headers.items():
            self.send_header(k, v)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        try:
            self.wfile.write(body)
        except (BrokenPipeError, ConnectionResetError):
            pass

    def do_GET(self):  # noqa: N802
        path = self.path.split("?")[0]
        if path == "/v1/models":
            mf = self.server.model_file
            body = json.dumps({"object": "list", "data": [{
                "id": EXPECT_ID,
                "status": {"value": "unloaded", "args": [mf, "-m", mf]}}]}).encode()
            self._send(200, body, {})
            return
        if path != "/props":
            self._send(404, b"", {})
            return
        status, body, headers = self.server.answer
        self._send(status, body, headers)


class Stub(http.server.ThreadingHTTPServer):
    daemon_threads = True
    allow_reuse_address = True

    def __init__(self, answer, model_file: str):
        super().__init__(("127.0.0.1", 0), Handler)
        self.answer = answer
        self.model_file = model_file


def verdict_reason(probe: Path, port: int, work: Path, timeout: int):
    cmd = ["bash", str(probe), "check", "--port", str(port), "--expect", EXPECT_ID,
           "--id", "r100", "--json"]
    env = dict(os.environ)
    env["TMPDIR"] = str(work)
    p = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, env=env)
    try:
        doc = json.loads(p.stdout)
    except json.JSONDecodeError:
        raise RuntimeError(f"probe printed no JSON (rc={p.returncode}): "
                           f"{p.stdout[:200]!r} {p.stderr[:200]!r}")
    rows = doc.get("rows") or []
    if len(rows) != 1:
        raise RuntimeError(f"probe JSON has {len(rows)} rows, want 1")
    return rows[0].get("verdict"), rows[0].get("reason"), p.returncode


def run_pass(probe: Path, tag: str, work: Path):
    out = {}
    for cid, status, body, headers, _want in CELLS:
        stub = Stub((status, body, headers), str(work / "model.gguf"))
        th = threading.Thread(target=stub.serve_forever, daemon=True)
        th.start()
        try:
            got = verdict_reason(probe, stub.server_address[1], work, timeout=120)
        finally:
            stub.shutdown()
            stub.server_close()
            th.join(timeout=5)
        out[cid] = got
        print(f"ROUTER_PROPS_STATUS100_CELL {tag} {cid} status={status} "
              f"verdict={got[0]} reason={got[1]} exit={got[2]}", flush=True)
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", type=Path, required=True)
    ap.add_argument("--rev", required=True)
    ap.add_argument("--probe-file", type=Path,
                    help="grade a candidate probe file instead of the one at --rev (controls only)")
    ap.add_argument("--work", type=Path, required=True)
    a = ap.parse_args()

    def git(*args):
        p = subprocess.run(["git", "-C", str(a.repo), *args], capture_output=True)
        if p.returncode != 0:
            raise RuntimeError(f"git {' '.join(args)} rc={p.returncode}")
        return p.stdout

    a.work.mkdir(parents=True, exist_ok=True)
    work = Path(tempfile.mkdtemp(prefix="r100-props-status-", dir=a.work)).resolve()
    try:
        rev = git("rev-parse", "--verify", a.rev + "^{commit}").decode().strip()
        base_bytes = git("show", f"{BASE}:tools/kama-probe.sh")
        tip_bytes = (a.probe_file.read_bytes() if a.probe_file
                     else git("show", f"{rev}:tools/kama-probe.sh"))
        (work / "model.gguf").write_bytes(b"GGUF\x03\x00\x00\x00" + b"\x00" * 64)
        base_probe = work / "probe-base.sh"
        tip_probe = work / "probe-tip.sh"
        base_probe.write_bytes(base_bytes)
        tip_probe.write_bytes(tip_bytes)
        base = run_pass(base_probe, "base", work)
        tip = run_pass(tip_probe, "tip", work)
    except (RuntimeError, subprocess.TimeoutExpired, OSError) as e:
        print(f"ROUTER_PROPS_STATUS100 could-not-evaluate: {e}")
        return 2
    finally:
        shutil.rmtree(work, ignore_errors=True)

    mismatches = base_mismatches = flips = stable = 0
    for cid, _status, _body, _headers, want in CELLS:
        got, bgot = tuple(tip[cid]), tuple(base[cid])
        if got != want:
            mismatches += 1
            print(f"ROUTER_PROPS_STATUS100_MISMATCH {cid} want={'/'.join(map(str, want))} "
                  f"got={'/'.join(map(str, got))}")
        if bgot != want:
            base_mismatches += 1
        if got != bgot:
            flips += 1
        else:
            stable += 1
    met = mismatches == 0
    print(f"ROUTER_PROPS_STATUS100 cells={len(CELLS)} mismatches={mismatches} "
          f"base_mismatches={base_mismatches} flips={flips} stable={stable} met={met} "
          f"rev={rev} probe_sha256={hashlib.sha256(tip_bytes).hexdigest()} "
          f"base_sha256={hashlib.sha256(base_bytes).hexdigest()} "
          f"candidate={'yes' if a.probe_file else 'no'}")
    return 0 if met else 1


if __name__ == "__main__":
    sys.exit(main())
