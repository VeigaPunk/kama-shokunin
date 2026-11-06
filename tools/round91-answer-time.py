#!/usr/bin/env python3
"""round91-answer-time.py - round-91 C1 (operability) frozen counter.

PREDICATE (frozen: plans/round-91-claims.md section C1):

    `python3 tools/round91-answer-time.py --repo <lane> --rev <R> --work <scratch>` prints
    `ANSWER_TIME cells=12 mismatches=0 positive_mismatches=0 probe=rev ...` and exits 0: on every
    one of the 12 cells below, `tools/kama-probe.sh` (bytes at <R>) run as
    `check --port <stub> --expect <id> --json --timeout 5 --connect-timeout 2` meets the cell's
    frozen pass condition, which always includes "finished within BUDGET = 20 s wall time".

Every cell is a lane-owned stub HTTP server on a free 127.0.0.1 port, started and stopped by this
counter in-process. Every answer body is under the probe's 4 MiB cap (round 90), so the bound
being tested is time, not bytes. A probe run is killed at 120 s; a killed run fails its cell.

Large-answer cells (a listener's legitimate-sized answer must not make the probe slow):
  T1-ids-200k-last     /v1/models lists 200 000 ids `x000000`..`x199999` (compact JSON), then
                       `good`. expect good. pass: verdict MODEL_OK, reason matched, <= BUDGET
  T2-ids-200k-absent   the same 200 000 ids without `good`. expect good.
                       pass: verdict MODEL_MISMATCH, <= BUDGET
  T3-router-80k-last   router shape: 80 000 entries `r00000`.. each with status {"value":"loaded"},
                       then `good` loaded. expect good. pass: verdict MODEL_OK, <= BUDGET
  T4-id-3900k          one id of 3 900 000 `a` bytes (no slash), then `good`. expect good.
                       pass: verdict MODEL_OK, reason matched, <= BUDGET
  T5-id-3800k-slashes  one id of 1 900 000 `a/` pairs ending `/good.gguf` (about 3.8 MB) only.
                       expect good. pass: verdict MODEL_OK, reason matched, <= BUDGET
Positive cells (the id-match rule a real server relies on; a mismatch here is harm):
  P1-plain             ids [`good`], expect good: MODEL_OK matched, <= BUDGET
  P2-path-gguf         ids [`/models/sub/good.gguf`], expect good: MODEL_OK matched
  P3-one-gguf-only     ids [`good.gguf.gguf`], expect `good`: MODEL_MISMATCH (ONE trailing .gguf is
                       stripped from each side, so `good.gguf` != `good`)
  P4-unicode-id        ids ["modele-\u00e8-\u65e5\u672c-\u00fc"] expected verbatim: MODEL_OK matched
  P5-json-specials     ids [`q"b\\s`] expected verbatim: MODEL_OK matched
  P6-mismatch          ids [`other`], expect good: MODEL_MISMATCH (a blanket MODEL_OK is harm)
  P7-wildcard          ids [`good`], expect `*`: MODEL_OK
Every positive cell also has the <= BUDGET condition.

Environment faults (no free port, stub never answers, bad --rev) exit 2.

Usage: round91-answer-time.py --repo DIR --rev REV --work DIR [--probe-file FILE]
Exit: 0 all 12 cells pass | 1 any cell fails | 2 could-not-evaluate.
`probe=rev` is printed only when the probe bytes come from `git show <rev>:tools/kama-probe.sh`;
`--probe-file` (controls) prints `probe=override` and can never meet the predicate.
"""
from __future__ import annotations

import argparse
import hashlib
import http.server
import json
import os
import shutil
import socket
import subprocess
import sys
import tempfile
import threading
import time
from pathlib import Path

CELLS = 12
BUDGET = 20.0
KILL = 120
POSITIVE = ("P1-plain", "P2-path-gguf", "P3-one-gguf-only", "P4-unicode-id", "P5-json-specials",
            "P6-mismatch", "P7-wildcard")
UNI = "modele-\u00e8-\u65e5\u672c-\u00fc"
SPECIAL = 'q"b\\s'
CAP = 4194304


class CannotEvaluate(Exception):
    pass


class Stub:
    """One cell's server. routes: path -> dict(code, body: bytes | ('stream', n), length: bool,
    headers: list[(k, v-bytes)])"""

    def __init__(self, routes):
        self.routes = routes
        self.sent = {}
        stub = self

        class H(http.server.BaseHTTPRequestHandler):
            protocol_version = "HTTP/1.0"

            def log_message(self, *a):
                pass

            def do_GET(self):
                path = self.path.split("?")[0]
                r = stub.routes.get(path)
                if r is None:
                    body = b'{"error":"not found"}'
                    self.send_response(404)
                    self.send_header("Content-Type", "application/json")
                    self.send_header("Content-Length", str(len(body)))
                    self.end_headers()
                    self.wfile.write(body)
                    return
                hdrs = r.get("headers") or [(b"Content-Type", b"application/json")]
                raw = b"HTTP/1.0 %d OK\r\n" % r.get("code", 200)
                raw += b"".join(k + b": " + v + b"\r\n" for k, v in hdrs)
                body = r["body"]
                if isinstance(body, tuple):
                    n, head = body[1], body[2]
                else:
                    n, head = len(body), body
                if r.get("length", True):
                    raw += b"Content-Length: " + str(n).encode() + b"\r\n"
                self.wfile.write(raw + b"\r\n")
                self.wfile.flush()
                sent = 0
                try:
                    if isinstance(body, tuple):
                        # streaming pad: head, then 'x' * (n - len(head) - 3), then '"}\n'
                        tail = b'"}\n'
                        self.connection.sendall(head)
                        sent += len(head)
                        chunk = b"x" * (64 * 1024)
                        left = n - len(head) - len(tail)
                        while left > 0:
                            c = chunk if left >= len(chunk) else chunk[:left]
                            self.connection.sendall(c)
                            sent += len(c)
                            left -= len(c)
                        self.connection.sendall(tail)
                        sent += len(tail)
                    else:
                        self.connection.sendall(body)
                        sent += len(body)
                except (BrokenPipeError, ConnectionResetError, OSError):
                    pass
                stub.sent[path] = stub.sent.get(path, 0) + sent

        self.srv = http.server.ThreadingHTTPServer(("127.0.0.1", 0), H)
        self.srv.daemon_threads = True
        self.port = self.srv.server_address[1]
        self.t = threading.Thread(target=self.srv.serve_forever, daemon=True)

    def __enter__(self):
        self.t.start()
        deadline = time.time() + 10
        while time.time() < deadline:
            try:
                with socket.create_connection(("127.0.0.1", self.port), timeout=1):
                    return self
            except OSError:
                time.sleep(0.05)
        raise CannotEvaluate("stub never accepted")

    def __exit__(self, *a):
        self.srv.shutdown()
        self.srv.server_close()


def jbody(doc) -> bytes:
    b = json.dumps(doc, separators=(",", ":")).encode()
    if len(b) >= CAP:
        raise CannotEvaluate(f"cell body {len(b)} bytes is not under the 4 MiB cap")
    return b


def ids_doc(ids, status=None):
    if status is None:
        return {"object": "list", "data": [{"id": i} for i in ids]}
    return {"object": "list", "data": [{"id": i, "status": {"value": status}} for i in ids]}


def run(probe: Path, port: int, expect: str, env: dict, cwd: Path):
    cmd = ["bash", str(probe), "check", "--port", str(port), "--expect", expect,
           "--timeout", "5", "--connect-timeout", "2", "--json"]
    t0 = time.monotonic()
    try:
        p = subprocess.run(cmd, capture_output=True, timeout=KILL, env=env, cwd=cwd)
    except subprocess.TimeoutExpired:
        return None, b"", time.monotonic() - t0
    return p.returncode, p.stdout, time.monotonic() - t0


def parse_row(out: bytes):
    try:
        doc = json.loads(out.decode("utf-8"))
        return doc["rows"][0]
    except Exception:
        return None


def cells():
    out = []

    def want(expect, verdict, reason=None):
        def chk(R):
            rc, so, dt = R(expect)
            row = parse_row(so)
            v = row.get("verdict") if row else ("killed" if rc is None else f"unparsed(rc={rc})")
            r = row.get("reason") if row else "-"
            ok = row is not None and v == verdict and (reason is None or r == reason) and dt <= BUDGET
            return ok, f"verdict={v} reason={r} seconds={dt:.2f}"
        return chk

    many = [f"x{i:06d}" for i in range(200000)]
    out.append(("T1-ids-200k-last", ids_doc(many + ["good"]), want("good", "MODEL_OK", "matched")))
    out.append(("T2-ids-200k-absent", ids_doc(many), want("good", "MODEL_MISMATCH")))
    out.append(("T3-router-80k-last", ids_doc([f"r{i:05d}" for i in range(80000)] + ["good"], "loaded"),
                want("good", "MODEL_OK")))
    out.append(("T4-id-3900k", ids_doc(["a" * 3900000, "good"]), want("good", "MODEL_OK", "matched")))
    out.append(("T5-id-3800k-slashes", ids_doc(["a/" * 1900000 + "good.gguf"]), want("good", "MODEL_OK", "matched")))
    out.append(("P1-plain", ids_doc(["good"]), want("good", "MODEL_OK", "matched")))
    out.append(("P2-path-gguf", ids_doc(["/models/sub/good.gguf"]), want("good", "MODEL_OK", "matched")))
    out.append(("P3-one-gguf-only", ids_doc(["good.gguf.gguf"]), want("good", "MODEL_MISMATCH")))
    out.append(("P4-unicode-id", ids_doc([UNI]), want(UNI, "MODEL_OK", "matched")))
    out.append(("P5-json-specials", ids_doc([SPECIAL]), want(SPECIAL, "MODEL_OK", "matched")))
    out.append(("P6-mismatch", ids_doc(["other"]), want("good", "MODEL_MISMATCH")))
    out.append(("P7-wildcard", ids_doc(["good"]), want("*", "MODEL_OK")))
    return out


def sha256(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", type=Path, required=True)
    ap.add_argument("--rev", required=True)
    ap.add_argument("--work", type=Path, required=True)
    ap.add_argument("--probe-file", type=Path)
    a = ap.parse_args()
    rows = []
    try:
        rv = subprocess.run(["git", "-C", str(a.repo), "rev-parse", "--verify", a.rev + "^{commit}"],
                            capture_output=True, text=True)
        if rv.returncode != 0:
            raise CannotEvaluate(f"unresolvable --rev {a.rev}")
        rev = rv.stdout.strip()
        a.work.mkdir(parents=True, exist_ok=True)
        work = Path(tempfile.mkdtemp(prefix="r91-time-", dir=a.work)).resolve()
        try:
            probe = work / "kama-probe.sh"
            if a.probe_file:
                probe.write_bytes(a.probe_file.read_bytes())
                mode = "override"
            else:
                probe.write_bytes(subprocess.run(["git", "-C", str(a.repo), "show", f"{rev}:tools/kama-probe.sh"],
                                                 capture_output=True, check=True).stdout)
                mode = "rev"
            probe_sha = sha256(probe)
            pcwd = work / "probe-cwd"
            pcwd.mkdir()
            env = dict(os.environ, TMPDIR=str(pcwd))
            for cid, doc, chk in cells():
                with Stub({"/v1/models": {"body": jbody(doc)}}) as stub:
                    def R(expect, _p=stub.port):
                        return run(probe, _p, expect, env, pcwd)
                    ok, detail = chk(R)
                rows.append((cid, bool(ok), detail))
                print(f"ANSWER_TIME_CELL {cid} ok={int(ok)} {detail}", flush=True)
        finally:
            shutil.rmtree(work, ignore_errors=True)
    except CannotEvaluate as e:
        print(f"ANSWER_TIME could-not-evaluate: {e}")
        return 2
    bad = sum(1 for _, ok, _ in rows if not ok)
    pos = sum(1 for cid, ok, _ in rows if not ok and cid in POSITIVE)
    print(f"ANSWER_TIME cells={len(rows)} mismatches={bad} positive_mismatches={pos} "
          f"probe={mode} probe_sha256={probe_sha} rev={rev}")
    return 0 if bad == 0 and len(rows) == CELLS else 1


if __name__ == "__main__":
    sys.exit(main())
