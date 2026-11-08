#!/usr/bin/env python3
"""plaincall_harness.py - round-99 amendment-1 control (wave evidence, not a lane instrument).

The C3 counter's eight cells all run `kama-probe.sh check`, where `eval_rows || exit_code=$?`
keeps `set -e` from aborting on a nonzero helper return. The plain-call subcommands
(`listeners`, `consumers`) do not have that guard, so a `router_autoload` call outside a
condition aborts them on an unread or explicit-off answer (SC01Recon receipt
`out/SC01Recon/10-c3-probe-plain-call-regression.out`). This harness reproduces that path without
touching a host service: it patches the `listeners)` dispatch line of a scratch probe copy to a
plain `classify "$KAMA_TEST_PORT" ""`, then runs it against a loopback stub for three scenarios.

Usage: python3 plaincall_harness.py --probe <probe.sh> --work <dir> [--label base|candidate]
Prints one line per scenario: PLAINCALL <label> <scenario> verdict=... reason=... rc=...
Exit 0 when every scenario exits 0 and prints the base-expected verdict/reason.
"""
import argparse
import http.server
import json
import re
import shutil
import subprocess
import sys
import tempfile
import threading
from pathlib import Path

EXPECT = {"nonrouter": ("MODEL_UNLOADED", "router-unloaded"),
          "off": ("MODEL_UNLOADED", "router-unloaded"),
          "on": ("MODEL_OK", "router-unloaded-autoload")}


class H(http.server.BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def do_GET(self):
        if self.path.split("?")[0] == "/v1/models":
            body = json.dumps({"object": "list", "data": [
                {"id": "fixture-model", "status": {"value": "unloaded",
                 "args": [self.server.modelfile, "-m", self.server.modelfile]}}]}).encode()
            ctype = "application/json"
        elif self.path.split("?")[0] == "/props":
            sc = self.server.scenario
            if sc == "on":
                body = b'{"role":"router","models_autoload":true}'
            elif sc == "off":
                body = b'{"role":"router","models_autoload":false}'
            else:
                body = b'{"status":"ok"}'
            ctype = "application/json"
        else:
            self.send_response(404); self.send_header("Content-Length", "0"); self.end_headers(); return
        self.send_response(200)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


class S(http.server.ThreadingHTTPServer):
    daemon_threads = True
    allow_reuse_address = True

    def __init__(self, scenario, modelfile):
        super().__init__(("127.0.0.1", 0), H)
        self.scenario = scenario
        self.modelfile = modelfile


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--probe", type=Path, required=True)
    ap.add_argument("--label", required=True)
    ap.add_argument("--work", type=Path, required=True)
    a = ap.parse_args()
    a.work.mkdir(parents=True, exist_ok=True)
    work = Path(tempfile.mkdtemp(prefix="plaincall-", dir=a.work)).resolve()
    try:
        src = a.probe.read_text()
        patched = src.replace(
            "    listeners) load_listeners; cmd_listeners ;;",
            '    listeners) classify "$KAMA_TEST_PORT" ""; '
            'printf \'PLAIN_CALL verdict=%s reason=%s\\n\' "$C_VERDICT" "$C_REASON"; exit 0 ;;')
        if patched == src:
            print(f"PLAINCALL {a.label} could-not-evaluate: listeners branch not found")
            return 2
        probe = work / "probe.sh"
        probe.write_text(patched)
        (work / "model.gguf").write_bytes(b"GGUF\x03\x00\x00\x00" + b"\x00" * 64)
        failures = 0
        for sc in ("nonrouter", "off", "on"):
            srv = S(sc, str(work / "model.gguf"))
            th = threading.Thread(target=srv.serve_forever, daemon=True)
            th.start()
            port = srv.server_address[1]
            try:
                env = {"KAMA_TEST_PORT": str(port), "PATH": "/usr/local/bin:/usr/bin:/bin",
                       "HOME": str(work), "TMPDIR": str(work)}
                p = subprocess.run(["bash", str(probe), "listeners"], capture_output=True,
                                   text=True, timeout=120, env=env)
            finally:
                srv.shutdown(); srv.server_close(); th.join(timeout=5)
            m = re.search(r"^PLAIN_CALL verdict=(\S+) reason=(\S+)$", p.stdout, re.M)
            verdict, reason = (m.group(1), m.group(2)) if m else ("-", "-")
            want = EXPECT[sc]
            if a.label == "candidate" and sc == "nonrouter":
                want = ("MODEL_UNLOADED", "router-autoload-unread")
            ok = p.returncode == 0 and (verdict, reason) == want
            failures += 0 if ok else 1
            print(f"PLAINCALL {a.label} {sc} verdict={verdict} reason={reason} "
                  f"rc={p.returncode} want={want[0]}/{want[1]} ok={int(ok)}")
        return 0 if failures == 0 else 1
    finally:
        shutil.rmtree(work, ignore_errors=True)


if __name__ == "__main__":
    sys.exit(main())
