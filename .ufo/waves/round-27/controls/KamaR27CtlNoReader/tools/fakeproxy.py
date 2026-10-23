#!/usr/bin/env python3
"""http_proxy decoy for the frozen counter's environment probe.

Answers every absolute-URI request with 502 and records the request line, so
the report can show whether the counter's own HTTP client honoured the proxy
environment variable.
"""
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

LOG = "/tmp/kama-r27-noreader/proxy-decoy-hit.log"


class Handler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def log_message(self, fmt, *a):
        pass

    def _rec(self):
        with open(LOG, "a", encoding="utf-8") as f:
            f.write(f"{self.command} {self.path}\n")

    def _send(self):
        self._rec()
        raw = b"proxy decoy"
        self.send_response(502)
        self.send_header("Content-Length", str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)

    do_GET = _send
    do_POST = _send
    do_CONNECT = _send


if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 47700
    ThreadingHTTPServer(("127.0.0.1", port), Handler).serve_forever()
