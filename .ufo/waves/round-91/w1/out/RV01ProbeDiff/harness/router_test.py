#!/usr/bin/env python3
"""router_refine + C_SERVED join verdict pairs: base probe vs M probe on stub listeners."""
import json
import os
import subprocess
import threading
import http.server
import socket
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
PROBE_B = HERE.parent / "revs" / "probe-B.sh"
PROBE_M = HERE.parent / "revs" / "probe-M.sh"


class Stub:
    def __init__(self, models_body, props_body):
        routes = {"/v1/models": (200, models_body)}
        if props_body is not None:
            routes["/props"] = (200, props_body)
        stub = self

        class H(http.server.BaseHTTPRequestHandler):
            protocol_version = "HTTP/1.0"

            def log_message(self, *a):
                pass

            def do_GET(self):
                path = self.path.split("?")[0]
                r = routes.get(path)
                if r is None:
                    body = b""
                    self.send_response(404)
                else:
                    body = r[1]
                    self.send_response(r[0])
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)

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


def ent(i, st, failed=None):
    e = {"id": i}
    if st is not None:
        s = {"value": st}
        if failed is not None:
            s["failed"] = failed
        e["status"] = s
    return e


PROPS = json.dumps({"role": "router", "models_autoload": True}).encode()

CELLS = [
    ("wild-mixed", [ent("good", "unloaded", False), ent("other", "loaded")], "*", True),
    ("match-unload-autoload-decoy", [ent("good", "unloaded", False), ent("decoy", "unloaded", False)], "good", True),
    ("good-nostatus-other-loading", [ent("good", None), ent("other", "loading")], "good", True),
    ("exp-empty-norm", [ent("good", "unloaded", False)], ".gguf", True),
    ("sleeping-plus-failed-other", [ent("good", "sleeping"), ent("other", "unloaded", True)], "good", True),
    ("failed-unload", [ent("good", "unloaded", True)], "good", True),
    ("loading", [ent("good", "loading")], "good", True),
    ("downloading", [ent("good", "downloading")], "good", True),
    ("no-status", [ent("good", None)], "good", True),
    ("dup-good-statuses", [ent("good", "unloaded", False), ent("good", "loaded")], "good", True),
    ("slash-path-id", [ent("/m/good.gguf", "unloaded", False)], "good", True),
    ("props-404", [ent("good", "unloaded", False)], "good", False),
    ("served-join-commas", [ent("a,b", None), ent("c", None)], "*", True),
    ("served-join-single", [ent("x", None)], "good", True),
    ("served-join-unicode", [ent("modèle/日本.gguf", None)], "na.me", True),
    ("empty-data", [], "good", True),
    ("numeric-id-entry", [ent("1000", "unloaded", False), ent("1e3", "loaded")], "1e3", True),
]


def run_probe(probe, port, expect):
    env = dict(os.environ, TMPDIR=str(HERE))
    cmd = ["bash", str(probe), "check", "--port", str(port), "--expect", expect,
           "--json", "--timeout", "5", "--connect-timeout", "2"]
    p = subprocess.run(cmd, capture_output=True, timeout=60, env=env, cwd=str(HERE))
    doc = json.loads(p.stdout.decode())
    row = doc["rows"][0]
    return (row["verdict"], row["reason"], row.get("served_model", "-"))


def main() -> int:
    bad = 0
    for name, entries, expect, props in CELLS:
        body = json.dumps({"object": "list", "data": entries}).encode()
        with Stub(body, PROPS if props else None) as s:
            b = run_probe(PROBE_B, s.port, expect)
            m = run_probe(PROBE_M, s.port, expect)
        ok = b == m
        if not ok:
            bad += 1
        print(f"{'CELL_OK ' if ok else 'CELL_DIFF'} {name}\n  B={b}\n  M={m}")
    print(f"ROUTER cells={len(CELLS)} diffs={bad}")
    return 1 if bad else 0


if __name__ == "__main__":
    raise SystemExit(main())
