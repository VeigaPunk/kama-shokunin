#!/usr/bin/env python3
"""r90 EX02 held-out cell: a router entry whose status.args[0] is not an absolute file.

tools/kama-probe.sh file_state() returns "-" without opening any path when
args[0] is not an absolute existing file (kama-probe.sh:695). SKILL.md:1802
documents "path relative ... unchanged (router-unloaded-autoload)" as a known
false green. This cell measures it on base and M with a missing model file:

  A  args[0]="--model" (not absolute) + --model /nonexistent/...  -> documented false green
  B  args[0]=<absolute server binary> + the same missing --model  -> router-model-missing
  C  args[0]="--model" + a valid 1.8 GB gguf                      -> MODEL_OK (control)

Each stub also answers GET /props {"role":"router","models_autoload":true}.
GET only; no POST, no load/unload. Prints one line per (stub, probe).
"""
import http.server
import json
import os
import socket
import subprocess
import sys
import threading
from pathlib import Path

OUT = Path(__file__).resolve().parent
PROBES = {"base": Path(os.environ["BASE_PROBE"]), "M": Path(os.environ["M_PROBE"])}
SERVER = "/home/vgpnk/src/llama.cpp/build/bin/llama-server"
MISSING = "/nonexistent/kama-r90/missing-model.gguf"
VALID = "/home/vgpnk/.cache/kama-shokunin/models/stories260K.gguf"
CELLS = {
    "A-relative-args0-missing": ["--model", MISSING],
    "B-absolute-args0-missing": [SERVER, "--model", MISSING],
    "C-relative-args0-valid": ["--model", VALID],
}
ENV = dict(os.environ)
ENV["TMPDIR"] = os.environ["LAT_TMPDIR"]
Path(ENV["TMPDIR"]).mkdir(parents=True, exist_ok=True)


def handler_for(args):
    class H(http.server.BaseHTTPRequestHandler):
        def log_message(self, *a):
            pass

        def do_GET(self):
            if self.path == "/v1/models":
                body = json.dumps({"data": [
                    {"id": "cell-model", "status": {"value": "unloaded", "args": args}}]}).encode()
                ct = "application/json"
            elif self.path == "/props":
                body = b'{"role":"router","models_autoload":true}'
                ct = "application/json"
            elif self.path == "/health":
                body = b'{"status":"ok"}'
                ct = "application/json"
            else:
                self.send_response(404)
                self.send_header("Content-Length", "0")
                self.end_headers()
                return
            self.send_response(200)
            self.send_header("Content-Type", ct)
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
    return H


def serve(args):
    s = socket.socket()
    s.bind(("127.0.0.1", 0))
    port = s.getsockname()[1]
    s.close()
    srv = http.server.ThreadingHTTPServer(("127.0.0.1", port), handler_for(args))
    srv.daemon_threads = True
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return srv, port


def main():
    rc = 0
    for cell, args in CELLS.items():
        srv, port = serve(args)
        try:
            for pname, probe in PROBES.items():
                cp = subprocess.run(["bash", str(probe), "check", "--port", str(port),
                                     "--expect", "*", "--json"],
                                    capture_output=True, text=True, env=ENV, cwd=str(OUT))
                verdict = reason = "?"
                try:
                    row = json.loads(cp.stdout)["rows"][0]
                    verdict, reason = row.get("verdict", "?"), row.get("reason", "?")
                except Exception:
                    pass
                print(f"CELL {cell:34s} probe={pname:4s} exit={cp.returncode} "
                      f"verdict={verdict} reason={reason}")
        finally:
            srv.shutdown()
            srv.server_close()
    return rc


if __name__ == "__main__":
    sys.exit(main())
