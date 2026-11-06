#!/usr/bin/env python3
"""Witness harness (MT01RouterMutants, kama r88): serve one crafted /v1/models
body and run a kama-probe.sh copy against it. Local scratch only; loopback only."""
import argparse, http.server, json, socket, subprocess, sys, threading


def free_port():
    s = socket.socket()
    s.bind(("127.0.0.1", 0))
    p = s.getsockname()[1]
    s.close()
    return p


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--probe", required=True)
    ap.add_argument("--expect", required=True)
    ap.add_argument("--body", required=True, help="file with the whole /v1/models JSON")
    a = ap.parse_args()
    raw = open(a.body, "rb").read()

    class H(http.server.BaseHTTPRequestHandler):
        def do_GET(self):
            if self.path.split("?")[0] == "/v1/models":
                out, ct = raw, "application/json; charset=utf-8"
            elif self.path.split("?")[0] == "/health":
                out, ct = b'{"status":"ok"}', "application/json; charset=utf-8"
            else:
                self.send_response(404); self.end_headers(); return
            self.send_response(200)
            self.send_header("Content-Type", ct)
            self.send_header("Content-Length", str(len(out)))
            self.end_headers()
            self.wfile.write(out)

        def version_string(self):
            return "llama.cpp"

        def log_message(self, *x):
            pass

    srv = http.server.ThreadingHTTPServer(("127.0.0.1", 0), H)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    try:
        p = subprocess.run(["bash", a.probe, "check", "--port", str(srv.server_address[1]),
                            "--expect", a.expect, "--json", "--timeout", "3", "--connect-timeout", "1"],
                           capture_output=True, text=True, timeout=60)
    finally:
        srv.shutdown(); srv.server_close()
    try:
        doc = json.loads(p.stdout)
        row = (doc.get("consumers") or doc.get("rows") or doc.get("results") or [])[0]
        v, r = row.get("verdict", "?"), row.get("reason", "?")
    except Exception:
        v, r = "UNPARSEABLE", "exit%d stderr=%r" % (p.returncode, p.stderr[-160:])
    print(json.dumps({"verdict": v, "reason": r, "exit": p.returncode}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
