#!/usr/bin/env python3
"""Serve one JSON body file on 127.0.0.1:PORT /v1/models; print PORT; run until killed."""
import http.server
import sys

body = open(sys.argv[1], "rb").read()


class H(http.server.BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.0"

    def log_message(self, *a):
        pass

    def do_GET(self):
        if self.path.split("?")[0] != "/v1/models":
            b = b'{"error":"not found"}'
            self.send_response(404)
        else:
            b = body
            self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(b)))
        self.end_headers()
        self.wfile.write(b)


srv = http.server.ThreadingHTTPServer(("127.0.0.1", 0), H)
print(srv.server_address[1], flush=True)
srv.serve_forever()
