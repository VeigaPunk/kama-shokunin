#!/usr/bin/env python3
"""MS-07 mechanism (round-16 M3): a stub that never calls serve_forever.

shutdown() waits on an event that only serve_forever sets, so it never returns.
Transient loopback socket, closed by process exit; no persistent server.
Expected: `timeout 5 python3 hang_stub.py` exits 124 (killed by timeout).
"""
import http.server
import socketserver


class Handler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()


server = socketserver.TCPServer(("127.0.0.1", 0), Handler)
print("stub bound on 127.0.0.1; calling shutdown() without serve_forever", flush=True)
server.shutdown()
print("shutdown returned")
