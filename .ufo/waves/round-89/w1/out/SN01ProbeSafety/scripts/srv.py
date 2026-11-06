#!/usr/bin/env python3
"""Hostile loopback stub for the kama probe: serves a fixed /v1/models body and a
router /props. Logs one line per request so we can prove what the probe asked for."""
import json, os, sys, time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

BODY = sys.argv[2]
PROPS = sys.argv[3] if len(sys.argv) > 3 else ""
LOG = sys.argv[4] if len(sys.argv) > 4 else ""
CHUNK = int(os.environ.get("SRV_CHUNK", "0"))     # >0: stream body in CHUNK-byte pieces
DELAY = float(os.environ.get("SRV_DELAY", "0"))
HDR = os.environ.get("SRV_HDR", "")


def log(msg):
    if LOG:
        with open(LOG, "a") as f:
            f.write(msg + "\n")


class H(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def log_message(self, *a):
        pass

    def do_GET(self):
        log("%.6f %s" % (time.time(), self.path))
        if self.path == "/props":
            data = open(PROPS, "rb").read() if PROPS else b'{"role":"router","models_autoload":true}'
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)
            return
        if self.path.startswith("/v1/models"):
            data = open(BODY, "rb").read()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            if HDR:
                self.send_header("Server", HDR)
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            if DELAY:
                time.sleep(DELAY)
            if CHUNK:
                for i in range(0, len(data), CHUNK):
                    self.wfile.write(data[i:i + CHUNK])
                    self.wfile.flush()
            else:
                self.wfile.write(data)
            return
        if self.path in ("/health", "/"):
            data = b'{"status":"ok"}'
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)
            return
        self.send_response(404)
        self.send_header("Content-Length", "0")
        self.end_headers()


srv = ThreadingHTTPServer(("127.0.0.1", int(sys.argv[1])), H)
srv.daemon_threads = True
srv.serve_forever()
