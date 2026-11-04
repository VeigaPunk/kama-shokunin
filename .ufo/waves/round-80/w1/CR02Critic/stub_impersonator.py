#!/usr/bin/env python3
"""Impostor stub: answers every endpoint the counter gates on, but is NOT ollama.
/api/version -> 0.40.11, /api/tags -> nonce model, /v1/models -> data[],
/api/ps -> models[], /api/create -> 200 stream. Process owner is python3."""
import json
import sys
from http.server import BaseHTTPRequestHandler, HTTPServer

PORT = int(sys.argv[1])
NONCE = sys.argv[2] if len(sys.argv) > 2 else "kama-r80-stub"


class H(BaseHTTPRequestHandler):
    def _send(self, code, body):
        raw = json.dumps(body).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)

    def do_GET(self):
        if self.path == "/api/version":
            self._send(200, {"version": "0.40.11"})
        elif self.path == "/api/tags":
            self._send(200, {"models": [{"name": f"{NONCE}:latest", "model": f"{NONCE}:latest"}]})
        elif self.path == "/v1/models":
            self._send(200, {"object": "list",
                             "data": [{"id": f"{NONCE}:latest", "object": "model",
                                       "created": 0, "owned_by": "library"}]})
        elif self.path == "/api/ps":
            self._send(200, {"models": []})
        else:
            self._send(404, {"error": "not found"})

    def do_POST(self):
        if self.path == "/api/create":
            self.send_response(200)
            self.send_header("Content-Type", "application/x-ndjson")
            self.end_headers()
            self.wfile.write(json.dumps({"status": "success"}).encode() + b"\n")
        else:
            self._send(404, {"error": "not found"})

    def log_message(self, *a):
        pass


HTTPServer(("127.0.0.1", PORT), H).serve_forever()
