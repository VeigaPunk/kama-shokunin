#!/usr/bin/env python3
"""Plain HTTP stub answering {"data":[...],"object":"list"} on /v1/models only.
Everything else 404 — exactly the 'model-API listener' the seat asks about."""
import json
import sys
from http.server import BaseHTTPRequestHandler, HTTPServer

PORT = int(sys.argv[1])
MODEL_ID = sys.argv[2] if len(sys.argv) > 2 else "kama-r80-stub:latest"


class H(BaseHTTPRequestHandler):
    def _send(self, code, body):
        raw = json.dumps(body).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)

    def do_GET(self):
        if self.path == "/v1/models":
            self._send(200, {"object": "list",
                             "data": [{"id": MODEL_ID, "object": "model",
                                       "created": 0, "owned_by": "stub"}]})
        else:
            self._send(404, {"error": {"message": "not found", "type": "api_error",
                                       "code": 404}})

    def do_POST(self):
        self._send(404, {"error": {"message": "not found", "type": "api_error",
                                   "code": 404}})

    def log_message(self, *a):
        pass


HTTPServer(("127.0.0.1", PORT), H).serve_forever()
