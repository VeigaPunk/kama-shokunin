#!/usr/bin/env python3
"""Held-out cell: an id carrying a lone CR (SN01 F4: '\\r survives into reason/served_model').
Runs a probe in table and --json mode; reports raw control bytes on stdout and JSON parse."""
import json
import subprocess
import sys
import threading
import http.server

DOC = {"object": "list", "data": [{"id": "good", "object": "model"},
                                  {"id": "a\rb", "object": "model"}]}


class H(http.server.BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.0"

    def log_message(self, *a):
        pass

    def do_GET(self):
        body = json.dumps(DOC).encode()
        if self.path.split("?")[0] != "/v1/models":
            body = b'{"error":"nf"}'
            self.send_response(404)
        else:
            self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


srv = http.server.ThreadingHTTPServer(("127.0.0.1", 0), H)
srv.daemon_threads = True
threading.Thread(target=srv.serve_forever, daemon=True).start()
port = srv.server_address[1]

for name in sys.argv[1:]:
    for mode in ("table", "json"):
        cmd = ["bash", name, "check", "--port", str(port), "--expect", "good",
               "--timeout", "5", "--connect-timeout", "2"]
        if mode == "json":
            cmd.append("--json")
        p = subprocess.run(cmd, capture_output=True, timeout=60)
        try:
            doc = json.loads(p.stdout)
            parsed, served = "yes", doc["rows"][0].get("served_model")
        except Exception:
            parsed, served = "no", "-"
        ctl = sorted({b for b in p.stdout if b < 0x20 and b not in (0x09, 0x0a)})
        print(f"{name} mode={mode} rc={p.returncode} json_parsed={parsed} served={served!r} "
              f"raw_ctl_bytes={[hex(b) for b in ctl]}")
srv.shutdown()
srv.server_close()
