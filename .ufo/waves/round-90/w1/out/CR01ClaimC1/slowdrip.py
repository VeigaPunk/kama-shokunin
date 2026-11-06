#!/usr/bin/env python3
"""Slow-drip 64 MiB close-delimited /v1/models answer. Prints the port, then the bytes
handed to the kernel once the client goes away. Used to test whether the C1 H2 proxy
(`sent <= 16 MiB`) can be satisfied by --max-time alone, with no body cap."""
import http.server
import json
import socket
import sys
import threading
import time

BIG = 64 << 20
RATE = 1 << 20  # bytes/s
CHUNK = 64 << 10
state = {"sent": 0}


class H(http.server.BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.0"

    def log_message(self, *a):
        pass

    def do_GET(self):
        path = self.path.split("?")[0]
        if path == "/v1/models":
            head = (json.dumps({"object": "list", "data": [{"id": "good", "object": "model"}],
                                "pad": ""})[:-2]).encode() + b'", "x": "'
            raw = (b"HTTP/1.0 200 OK\r\nContent-Type: application/json\r\n\r\n" + head)
            self.wfile.write(raw)
            self.wfile.flush()
            sent = len(head)
            body = b"x" * CHUNK
            left = BIG - len(head) - 3
            try:
                while left > 0:
                    c = body if left >= CHUNK else body[:left]
                    self.connection.sendall(c)
                    sent += len(c)
                    left -= len(c)
                    state["sent"] = sent
                    time.sleep(CHUNK / RATE)
                self.connection.sendall(b'"}\n')
                state["sent"] = sent + 3
            except (BrokenPipeError, ConnectionResetError, OSError):
                state["sent"] = sent
            return
        body = b'{"error":"not found"}'
        self.send_response(404)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


srv = http.server.ThreadingHTTPServer(("127.0.0.1", 0), H)
srv.daemon_threads = True
print(srv.server_address[1], flush=True)
t = threading.Thread(target=srv.serve_forever, daemon=True)
t.start()
try:
    while True:
        time.sleep(0.2)
except KeyboardInterrupt:
    pass
