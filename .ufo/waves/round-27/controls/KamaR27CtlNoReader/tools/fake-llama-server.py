#!/usr/bin/env python3
"""Control probe: a fake `llama-server` that answers like the pinned one.

It is NOT llama-server. It answers every baseline route 200 and every request
body that carries a marker key "m" with HTTP 400 and a JSON error whose message
is the signature the control wants. Marker -> signature map is read from
/tmp/kama-r27-noreader/wanted.json so the mapping survives the counter's
clean_env() (which strips every variable except PATH/HOME/LANG).

Used only by the mutant counter copy and by the PYTHONPATH environment probe.
"""
import json
import os
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

WANTED_FILE = "/tmp/kama-r27-noreader/wanted.json"


def load_wanted():
    try:
        with open(WANTED_FILE, "r", encoding="utf-8") as f:
            doc = json.load(f)
        return doc if isinstance(doc, dict) else {}
    except Exception:
        return {}


def main():
    args = sys.argv[1:]
    if "--help" in args or "-h" in args:
        print("fake llama-server (control probe) --help\nusage: fake-llama-server [options]")
        return 0
    if "--version" in args:
        print("fake llama-server (control probe) version 0")
        return 0
    port = 8080
    for i, a in enumerate(args):
        if a == "--port" and i + 1 < len(args):
            port = int(args[i + 1])
        elif a.startswith("--port="):
            port = int(a.split("=", 1)[1])
    wanted = load_wanted()

    class Handler(BaseHTTPRequestHandler):
        protocol_version = "HTTP/1.1"

        def log_message(self, fmt, *a):
            pass

        def _send(self, code, obj):
            raw = json.dumps(obj).encode()
            self.send_response(code)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(raw)))
            self.end_headers()
            self.wfile.write(raw)

        def do_GET(self):
            self._send(200, {"status": "ok", "fake": True})

        def do_POST(self):
            n = int(self.headers.get("Content-Length") or 0)
            raw = self.rfile.read(n) if n else b""
            try:
                body = json.loads(raw.decode("utf-8")) if raw else {}
            except Exception:
                body = {}
            marker = body.get("m") if isinstance(body, dict) else None
            if isinstance(marker, str) and marker in wanted:
                self._send(400, {"error": {"message": wanted[marker],
                                           "type": "invalid_request_error"}})
            else:
                self._send(200, {"status": "ok", "fake": True})

    srv = ThreadingHTTPServer(("127.0.0.1", port), Handler)
    srv.serve_forever()
    return 0


if __name__ == "__main__":
    sys.exit(main())
