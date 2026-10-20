#!/usr/bin/env python3
"""Replay the loading 503 captured in live/receipt.json through the current and
the frozen probe (stub on 127.0.0.1:0, exact captured status, headers, body).
Prints one JSON line per probe; exit 0 when current=MODEL_LOADING and
frozen=FOREIGN_SERVICE, else 1."""
import http.server, json, pathlib, subprocess, sys, threading

W = pathlib.Path(__file__).resolve().parents[1]
LANE = W.parents[2]
cap = json.loads((W / "live" / "receipt.json").read_text())["loading_503"]
body = cap["body"].encode()


class H(http.server.BaseHTTPRequestHandler):
    def version_string(self):
        return cap["headers"].get("server", "llama.cpp")

    def do_GET(self):
        self.send_response(cap["status"])
        self.send_header("Content-Type", cap["headers"]["content-type"])
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *a):
        pass


srv = http.server.ThreadingHTTPServer(("127.0.0.1", 0), H)
threading.Thread(target=srv.serve_forever, daemon=True).start()
port = srv.server_address[1]
out = {}
for name, probe in (("current", LANE / "tools/kama-probe.sh"),
                    ("frozen", W / "frozen/kama-probe-before.sh")):
    r = subprocess.run(["bash", str(probe), "check", "--port", str(port), "--expect",
                        "kama-stories260k", "--json", "--timeout", "2",
                        "--connect-timeout", "1"], capture_output=True, text=True, timeout=60)
    row = json.loads(r.stdout)["rows"][0]
    out[name] = {"exit": r.returncode, "verdict": row["verdict"], "reason": row["reason"]}
    print(json.dumps({"probe": name, "captured_body_sha256": cap["body_sha256"], **out[name]}))
srv.shutdown()
ok = out["current"]["verdict"] == "MODEL_LOADING" and out["frozen"]["verdict"] == "FOREIGN_SERVICE"
sys.exit(0 if ok else 1)
