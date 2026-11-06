#!/usr/bin/env python3
"""round90-reason-capture.py - capture one probe answer per reason code (round-90 C2 receipt producer).

Runs `tools/kama-probe.sh` (bytes at --rev, or --probe-file) as
`check --port <stub> --expect <id> --json --timeout <t> --connect-timeout 1` against one lane-owned
stub per cell on a free 127.0.0.1 port and writes one JSON line per cell:
    {"cell": ..., "reason": ..., "verdict": ..., "exit": ..., "probe_sha256": ...}
sorted by cell. Ports, pids and timings never reach the receipt, so two runs over the same probe
bytes are byte-identical (the closure re-runs this and `cmp`s). The reason/verdict are whatever the
probe printed: the tool never writes an expected value. The C2 counter
(`tools/round90-reason-rows.py`) binds `SKILL.md` rows to these lines.

Usage: round90-reason-capture.py --repo DIR --rev REV --work DIR --out FILE [--probe-file FILE]
Exit: 0 receipt written | 2 could-not-evaluate (bad --rev, a probe answer not parseable).
"""
from __future__ import annotations

import argparse
import hashlib
import http.server
import json
import os
import shutil
import socket
import struct
import subprocess
import sys
import tempfile
import threading
from pathlib import Path


class CannotEvaluate(Exception):
    pass


def free_port() -> int:
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


class Raw:
    """TCP-level stub: mode hang | close | reset | garbage."""

    def __init__(self, mode):
        self.mode = mode
        self.s = socket.socket()
        self.s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.s.bind(("127.0.0.1", 0))
        self.s.listen(16)
        self.port = self.s.getsockname()[1]
        self.held = []
        self.stop = False
        self.t = threading.Thread(target=self.loop, daemon=True)

    def loop(self):
        while not self.stop:
            try:
                c, _ = self.s.accept()
            except OSError:
                return
            try:
                c.settimeout(2)
                try:
                    c.recv(65536)
                except OSError:
                    pass
                if self.mode == "hang":
                    self.held.append(c)
                    continue
                if self.mode == "reset":
                    c.setsockopt(socket.SOL_SOCKET, socket.SO_LINGER, struct.pack("ii", 1, 0))
                elif self.mode == "garbage":
                    c.sendall(b"SSH-2.0-OpenSSH_9.9\r\n")
                c.close()
            except OSError:
                pass

    def __enter__(self):
        self.t.start()
        return self

    def __exit__(self, *a):
        self.stop = True
        for c in self.held:
            c.close()
        self.s.close()


class Http:
    """routes: path -> (code, content-type, body bytes | ('stream', n))"""

    def __init__(self, routes):
        routes = dict(routes)

        class H(http.server.BaseHTTPRequestHandler):
            protocol_version = "HTTP/1.0"

            def log_message(self, *a):
                pass

            def do_GET(self):
                r = routes.get(self.path.split("?")[0], (404, "application/json", b'{"error":"not found"}'))
                code, ct, body = r
                self.send_response(code)
                self.send_header("Content-Type", ct)
                if isinstance(body, bytes):
                    self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                try:
                    if isinstance(body, bytes):
                        self.wfile.write(body)
                    else:
                        self.wfile.write(b'{"data": [{"id": "good"}], "pad": "')
                        chunk = b"x" * 65536
                        for _ in range(body[1] // len(chunk)):
                            self.wfile.write(chunk)
                except OSError:
                    pass

        self.srv = http.server.ThreadingHTTPServer(("127.0.0.1", 0), H)
        self.srv.daemon_threads = True
        self.port = self.srv.server_address[1]
        self.t = threading.Thread(target=self.srv.serve_forever, daemon=True)

    def __enter__(self):
        self.t.start()
        return self

    def __exit__(self, *a):
        self.srv.shutdown()
        self.srv.server_close()


J = "application/json"


def models(*entries):
    return json.dumps({"object": "list", "data": list(entries)}).encode()


def entry(i, status=None, failed=None, args=None):
    e = {"id": i, "object": "model"}
    if status is not None:
        st = {"value": status}
        if failed is not None:
            st["failed"] = failed
        if args is not None:
            st["args"] = args
        e["status"] = st
    return e


def props(autoload):
    return (200, J, json.dumps({"role": "router", "models_autoload": autoload}).encode())


def cells(work: Path):
    """-> list of (cell, kind, spec, expect, timeout)"""
    absent = str(work / "absent-model.gguf")
    notgguf = work / "not-a-model.gguf"
    notgguf.write_bytes(b"this is not a gguf model file\n" * 64)
    exe = sys.executable
    loading = json.dumps({"error": {"message": "Loading model", "type": "unavailable_error", "code": 503}}).encode()
    return [
        ("R-connection-refused", "closed", None, "good", 3),
        ("R-timeout", "raw", "hang", "good", 2),
        ("R-empty-reply", "raw", "close", "good", 3),
        ("R-connection-reset", "raw", "reset", "good", 3),
        ("R-no-http-response", "raw", "garbage", "good", 3),
        ("R-http-401", "http", {"/v1/models": (401, J, b'{"error":"unauthorized"}')}, "good", 3),
        ("R-http-403", "http", {"/v1/models": (403, J, b'{"error":"forbidden"}')}, "good", 3),
        ("R-llamacpp-loading", "http", {"/v1/models": (503, J, loading)}, "good", 3),
        ("R-expected-wildcard", "http", {"/v1/models": (200, J, models(entry("good")))}, "*", 3),
        ("R-matched", "http", {"/v1/models": (200, J, models(entry("good")))}, "good", 3),
        ("R-unresolvable-id", "http", {"/v1/models": (200, J, models({"object": "model"}))}, "good", 3),
        ("R-served-id-mismatch", "http", {"/v1/models": (200, J, models(entry("other")))}, "good", 3),
        ("R-html-non-model", "http", {"/v1/models": (200, "text/html", b"<html><body>hi</body></html>")}, "good", 3),
        ("R-schema-unrecognized", "http", {"/v1/models": (200, J, b'{"status":"ok"}')}, "good", 3),
        ("R-non-model-2xx", "http", {"/v1/models": (200, "text/plain", b"ok\n")}, "good", 3),
        ("R-non-2xx-non-model-http", "http", {"/v1/models": (404, J, b'{"error":"no such route"}')}, "good", 3),
        ("R-router-sleeping", "http", {"/v1/models": (200, J, models(entry("good", "sleeping")))}, "good", 3),
        ("R-router-unloaded-autoload", "http",
         {"/v1/models": (200, J, models(entry("good", "unloaded"))), "/props": props(True)}, "good", 3),
        ("R-router-loading", "http", {"/v1/models": (200, J, models(entry("good", "loading")))}, "good", 3),
        ("R-router-downloading", "http", {"/v1/models": (200, J, models(entry("good", "downloading")))}, "good", 3),
        ("R-router-model-missing", "http",
         {"/v1/models": (200, J, models(entry("good", "unloaded", False, [exe, "--model", absent]))),
          "/props": props(True)}, "good", 3),
        ("R-router-model-invalid", "http",
         {"/v1/models": (200, J, models(entry("good", "unloaded", False, [exe, "--model", str(notgguf)]))),
          "/props": props(True)}, "good", 3),
        ("R-router-unloaded", "http",
         {"/v1/models": (200, J, models(entry("good", "unloaded"))), "/props": props(False)}, "good", 3),
        ("R-body-too-large", "http", {"/v1/models": (200, J, ("stream", 64 << 20))}, "good", 5),
    ]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", type=Path, required=True)
    ap.add_argument("--rev", required=True)
    ap.add_argument("--work", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--probe-file", type=Path)
    a = ap.parse_args()
    rv = subprocess.run(["git", "-C", str(a.repo), "rev-parse", "--verify", a.rev + "^{commit}"],
                        capture_output=True, text=True)
    if rv.returncode != 0:
        print(f"REASON_CAPTURE could-not-evaluate: unresolvable --rev {a.rev}")
        return 2
    rev = rv.stdout.strip()
    a.work.mkdir(parents=True, exist_ok=True)
    work = Path(tempfile.mkdtemp(prefix="r90-reasons-", dir=a.work)).resolve()
    lines = []
    try:
        probe = work / "kama-probe.sh"
        if a.probe_file:
            probe.write_bytes(a.probe_file.read_bytes())
        else:
            probe.write_bytes(subprocess.run(["git", "-C", str(a.repo), "show", f"{rev}:tools/kama-probe.sh"],
                                             capture_output=True, check=True).stdout)
        sha = hashlib.sha256(probe.read_bytes()).hexdigest()
        pcwd = work / "probe-cwd"
        pcwd.mkdir()
        env = dict(os.environ, TMPDIR=str(pcwd))
        for cell, kind, spec, expect, tmo in cells(work):
            if kind == "closed":
                srv, port = None, free_port()
            elif kind == "raw":
                srv = Raw(spec)
            else:
                srv = Http(spec)
            if srv is not None:
                srv.__enter__()
                port = srv.port
            try:
                p = subprocess.run(["bash", str(probe), "check", "--port", str(port), "--expect", expect, "--json",
                                    "--timeout", str(tmo), "--connect-timeout", "1"],
                                   capture_output=True, timeout=120, env=env, cwd=pcwd)
            finally:
                if srv is not None:
                    srv.__exit__()
            try:
                row = json.loads(p.stdout)["rows"][0]
            except Exception:
                raise CannotEvaluate(f"{cell}: probe output unparseable (exit {p.returncode})")
            lines.append({"cell": cell, "reason": row.get("reason"), "verdict": row.get("verdict"),
                          "exit": p.returncode, "probe_sha256": sha})
    except CannotEvaluate as e:
        print(f"REASON_CAPTURE could-not-evaluate: {e}")
        return 2
    finally:
        shutil.rmtree(work, ignore_errors=True)
    lines.sort(key=lambda d: d["cell"])
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text("".join(json.dumps(d, sort_keys=True) + "\n" for d in lines))
    for d in lines:
        print(f"REASON_CAPTURE_CELL {d['cell']} verdict={d['verdict']} reason={d['reason']} exit={d['exit']}")
    print(f"REASON_CAPTURE cells={len(lines)} probe_sha256={sha} rev={rev} out={a.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
