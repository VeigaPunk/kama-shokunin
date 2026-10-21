#!/usr/bin/env python3
"""MS-07 fix prototype: bounded shutdown; a stub that never served is exit 2.

Without --serve the stub never calls serve_forever: shutdown() is run on a daemon
thread and joined with a 3 s bound; if still blocked the run is could-not-evaluate
(exit 2), not a hang. With --serve (control) serve_forever runs first and shutdown
returns (exit 0). Transient loopback socket only.
"""
import http.server
import socketserver
import sys
import threading


class Handler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()


server = socketserver.TCPServer(("127.0.0.1", 0), Handler)
if "--serve" in sys.argv[1:]:
    threading.Thread(target=server.serve_forever, daemon=True).start()
stopper = threading.Thread(target=server.shutdown, daemon=True)
stopper.start()
stopper.join(timeout=3)
if stopper.is_alive():
    print("VIOLATION: stub never served; shutdown() still blocked after 3 s "
          "(could-not-evaluate)", file=sys.stderr)
    sys.exit(2)
server.server_close()
print("shutdown returned within 3 s")
sys.exit(0)
