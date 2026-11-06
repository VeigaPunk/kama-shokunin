#!/usr/bin/env python3
"""RV01ProbeDiff reproducer: canned llama.cpp router stub for kama-probe.sh verdict checks.

Usage: stub_router.py SCENARIO PROBE_PATH [SUBCOMMAND_ARGS...]

Starts a loopback HTTP stub serving the scenario's GET /v1/models body
(plus GET /health -> {"status":"ok"}), runs the probe once with the given
subcommand args (--port/--expect are filled in), prints stdout/stderr and the
true exit code, then tears the stub down. Never touches 127.0.0.1:1234.
"""
from __future__ import annotations

import http.server
import json
import subprocess
import sys
import threading


def entry(mid, status=None):
    e = {"id": mid, "object": "model", "owned_by": "llamacpp"}
    if status is not None:
        e["status"] = status
    return e


SCENARIOS = {
    # name -> (data[] body, expect flag)
    "exact-unloaded": ([entry("m1", {"value": "unloaded"})], "m1"),
    "exact-unloaded-failed": ([entry("m1", {"value": "unloaded", "failed": True})], "m1"),
    "exact-loading": ([entry("m1", {"value": "loading"})], "m1"),
    "gguf-alias": ([entry("/models/stories260K.gguf", {"value": "unloaded"})], "stories260K"),
    "multi-loaded-wins": ([entry("m1", {"value": "unloaded"}),
                           entry("m1.gguf", {"value": "loaded"})], "m1"),
    "multi-loading-beats-unloaded": ([entry("m1", {"value": "unloaded"}),
                                      entry("m1", {"value": "loading"})], "m1"),
    "multi-statusless-wins": ([entry("m1", {"value": "unloaded"}), entry("m2")], "m1"),
    "wild-unloaded": ([entry("a", {"value": "sleeping"}), entry("b", {"value": "unloaded"})], "*"),
    "wild-mixed-statusless": ([entry("a", {"value": "unloaded"}), entry("b")], "*"),
    "wild-no-status": ([entry("a"), entry("b")], "*"),
    "dash-expect": ([entry("a", {"value": "unloaded"})], "-"),
    "empty-expect": ([entry("a", {"value": "unloaded"})], ""),
    "status-no-value": ([entry("m1", {})], "m1"),
    "value-not-string": ([entry("m1", {"value": 7})], "m1"),
    "expected-absent": ([entry("m1", {"value": "loaded"})], "m9"),
    "empty-data": ([], "m1"),
    # pathological: id with an embedded newline corrupts the probe's TSV framing
    "id-newline-loaded": ([entry("m1\nzzz", {"value": "loaded"})], "m1"),
    "empty-value-string": ([entry("m1", {"value": ""})], "m1"),
}


class Stub(http.server.BaseHTTPRequestHandler):
    body = b""
    hits = []

    def do_GET(self):
        path = self.path.split("?")[0]
        if path == "/v1/models":
            out, ct = self.body, "application/json; charset=utf-8"
        elif path == "/health":
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


def main() -> int:
    name, probe = sys.argv[1], sys.argv[2]
    extra = sys.argv[3:]
    data, expect = SCENARIOS[name]
    Stub.body = json.dumps({"object": "list", "data": data}).encode()
    srv = http.server.ThreadingHTTPServer(("127.0.0.1", 0), Stub)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    port = srv.server_address[1]
    args = ["bash", probe] + extra + ["--port", str(port), "--expect", expect,
                                      "--timeout", "3", "--connect-timeout", "1"]
    print(f"### scenario={name} expect={expect!r} cmd={' '.join(args[2:])}")
    try:
        p = subprocess.run(args, capture_output=True, text=True, timeout=60)
        out = p.stdout.strip()
        print(out[:2000])
        err = p.stderr.strip()
        if err:
            print(f"[stderr] {err[-600:]}")
        print(f"[exit {p.returncode}]")
        rc = p.returncode
    finally:
        srv.shutdown()
        srv.server_close()
    return rc


if __name__ == "__main__":
    sys.exit(main())
