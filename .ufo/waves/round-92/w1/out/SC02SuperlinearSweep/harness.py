#!/usr/bin/env python3
"""SC02SuperlinearSweep harness: lane-owned stub servers on free loopback ports + probe runner.

Never touches 127.0.0.1:1234. GET only. All artefacts under the seat scratch dir.
"""
from __future__ import annotations

import http.server
import json
import os
import socket
import subprocess
import threading
import time
from pathlib import Path

CAP = 4194304
KILL = 120


class Stub:
    """routes: path -> body bytes (200 application/json); anything else 404."""

    def __init__(self, routes, port=0):
        self.routes = routes
        stub = self

        class H(http.server.BaseHTTPRequestHandler):
            protocol_version = "HTTP/1.0"

            def log_message(self, *a):
                pass

            def do_GET(self):
                body = stub.routes.get(self.path.split("?")[0])
                code = 200
                if body is None:
                    body, code = b'{"error":"not found"}', 404
                self.send_response(code)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                try:
                    self.wfile.write(body)
                except OSError:
                    pass

        self.srv = http.server.ThreadingHTTPServer(("127.0.0.1", port), H)
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
        raise RuntimeError("stub never accepted")

    def __exit__(self, *a):
        self.srv.shutdown()
        self.srv.server_close()


def jbody(doc) -> bytes:
    b = json.dumps(doc, separators=(",", ":")).encode()
    assert len(b) < CAP, f"body {len(b)} >= 4 MiB cap"
    return b


def ids_doc(ids):
    return {"object": "list", "data": [{"id": i} for i in ids]}


def router_doc(entries):
    """entries: (id, status, failed|None, args|None)"""
    data = []
    for i, st, failed, args in entries:
        s = {"value": st}
        if failed is not None:
            s["failed"] = failed
        if args is not None:
            s["args"] = args
        data.append({"id": i, "status": s})
    return {"object": "list", "data": data}


class Runner:
    def __init__(self, work: Path, probe_bytes: bytes, tag: str):
        self.work = work
        self.probe = work / f"probe-{tag}.sh"
        self.work.mkdir(parents=True, exist_ok=True)
        self.probe.write_bytes(probe_bytes)
        self.cwd = work / f"cwd-{tag}"
        self.cwd.mkdir(exist_ok=True)
        self.env = dict(os.environ, TMPDIR=str(self.cwd))

    def run(self, args, kill=KILL):
        t0 = time.monotonic()
        try:
            p = subprocess.run(["bash", str(self.probe)] + args, capture_output=True,
                               timeout=kill, env=self.env, cwd=self.cwd)
        except subprocess.TimeoutExpired:
            return None, b"", b"", time.monotonic() - t0
        return p.returncode, p.stdout, p.stderr, time.monotonic() - t0

    def check(self, port, expect, kill=KILL):
        return self.run(["check", "--port", str(port), "--expect", expect, "--timeout", "5",
                         "--connect-timeout", "2", "--json"], kill=kill)

    def snapshot(self, port, expect, kill=KILL):
        d = self.work / "snap"
        if d.exists():
            for p in sorted(d.rglob("*"), reverse=True):
                if p.is_file():
                    p.unlink()
                elif p.is_dir():
                    p.rmdir()
        else:
            d.mkdir(parents=True)
        pin = d / "pin.txt"
        pin.write_text(f"http://127.0.0.1:{port}/v1\n")
        reg = d / "registry.tsv"
        reg.write_text("id\tconsumer_path\tjson_pointer_or_grep\tdeclared_baseurl\texpected_model_id\tnotes\n"
                       f"cell\t{pin}\tgrep:http://[^ ]+\thttp://127.0.0.1:{port}/v1\t{expect}\tr92\n")
        hist = d / "history"
        rc, so, se, dt = self.run(["snapshot", "--json", "--registry", str(reg), "--history", str(hist),
                                   "--timeout", "5", "--connect-timeout", "2"], kill=kill)
        latest = hist / "latest.tsv"
        tsv = latest.read_bytes() if latest.exists() else None
        return rc, so, se, dt, tsv


def loadavg():
    try:
        return open("/proc/loadavg").read().split()[:3]
    except OSError:
        return ["?", "?", "?"]


def uptime_str():
    return "load " + " ".join(loadavg())
