#!/usr/bin/env python3
"""One-body stub + one probe run. Prints "<label> probe=<name> expect=<e> verdict=... reason=... seconds=...".

Usage: stubrun.py --probe FILE --name NAME --label LABEL --expect E --body FILE
"""
import argparse
import http.server
import json
import socket
import subprocess
import sys
import threading
import time


class H(http.server.BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.0"
    body = b""

    def log_message(self, *a):
        pass

    def do_GET(self):
        path = self.path.split("?")[0]
        if path == "/v1/models":
            b = H.body
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(b)))
            self.end_headers()
            self.wfile.write(b)
        else:
            b = b'{"error":"not found"}'
            self.send_response(404)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(b)))
            self.end_headers()
            self.wfile.write(b)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--probe", required=True)
    ap.add_argument("--name", required=True)
    ap.add_argument("--label", required=True)
    ap.add_argument("--expect", required=True)
    ap.add_argument("--body", required=True)
    a = ap.parse_args()
    H.body = open(a.body, "rb").read()
    srv = http.server.ThreadingHTTPServer(("127.0.0.1", 0), H)
    srv.daemon_threads = True
    port = srv.server_address[1]
    t = threading.Thread(target=srv.serve_forever, daemon=True)
    t.start()
    deadline = time.time() + 10
    while time.time() < deadline:
        try:
            with socket.create_connection(("127.0.0.1", port), timeout=1):
                break
        except OSError:
            time.sleep(0.05)
    cmd = ["bash", a.probe, "check", "--port", str(port), "--expect", a.expect,
           "--timeout", "5", "--connect-timeout", "2", "--json"]
    t0 = time.monotonic()
    p = subprocess.run(cmd, capture_output=True, timeout=120)
    dt = time.monotonic() - t0
    srv.shutdown()
    srv.server_close()
    try:
        row = json.loads(p.stdout.decode())["rows"][0]
        v, r = row.get("verdict"), row.get("reason")
    except Exception:
        v, r = "unparsed", f"rc={p.returncode}"
    print(f"HELD {a.label} probe={a.name} expect={a.expect} verdict={v} reason={r} "
          f"seconds={dt:.2f} rc={p.returncode}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
