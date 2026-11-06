#!/usr/bin/env python3
"""Run the base and M probes against a slow-drip 64 MiB close-delimited answer and print
the bytes the stub handed to the kernel plus the probe's verdict. Tests H2's proxy:
sent <= 16 MiB AND verdict != MODEL_OK, with no body cap in the probe."""
import json
import subprocess
import sys
import threading
import time
import http.server

BIG = 64 << 20
RATE = 1 << 20
CHUNK = 64 << 10


def make_server():
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
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return srv, state


def run(probe, port):
    p = subprocess.run(["bash", probe, "check", "--port", str(port), "--expect", "good",
                        "--timeout", "5", "--connect-timeout", "2", "--json"],
                       capture_output=True, timeout=60)
    return p.returncode, p.stdout


for name in sys.argv[1:]:
    srv, state = make_server()
    rc, out = run(name, srv.server_address[1])
    time.sleep(0.5)
    try:
        doc = json.loads(out)
        row = doc["rows"][0]
        v, r = row["verdict"], row["reason"]
    except Exception:
        v, r = "unparsed", "-"
    print(f"{name} rc={rc} verdict={v} reason={r} sent={state['sent']} "
          f"h2_pass={int(state['sent'] <= (16 << 20) and v != 'MODEL_OK')}")
    srv.shutdown()
    srv.server_close()
