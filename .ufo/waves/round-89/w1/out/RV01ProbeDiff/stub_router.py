#!/usr/bin/env python3
"""Stub llama.cpp router for probe-diff reproducers (RV01ProbeDiff, round 89 w1).

usage: stub_router.py PORT SCENARIO_JSON
Serves GET /v1/models from the scenario's "entries", GET /props from "props"
(defaults to role=router, models_autoload=true), GET /health -> 200 {}.
Never POST: nothing here loads anything.
"""
import json
import sys
from http.server import BaseHTTPRequestHandler, HTTPServer

PORT = int(sys.argv[1])
SCEN = json.load(open(sys.argv[2]))


class H(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def log_message(self, *a):
        pass

    def _json(self, obj, code=200):
        b = json.dumps(obj).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Server", "llama.cpp")
        self.send_header("Content-Length", str(len(b)))
        self.end_headers()
        self.wfile.write(b)

    def do_GET(self):
        if self.path == "/v1/models":
            self._json({"object": "list", "data": SCEN["entries"]})
        elif self.path == "/props":
            self._json(SCEN.get("props", {"role": "router", "models_autoload": True,
                                          "default_generation_settings": {}, "total_slots": 0}))
        elif self.path == "/health":
            self._json({"status": "ok"})
        else:
            self._json({"error": {"message": "not found", "type": "not_found_error", "code": 404}}, 404)

    def do_POST(self):
        # never used by the probe; refuse loudly rather than serve
        self._json({"error": {"message": "stub does not serve completions",
                              "type": "server_error", "code": 500}}, 500)


HTTPServer(("127.0.0.1", PORT), H).serve_forever()
