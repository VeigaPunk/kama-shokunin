#!/usr/bin/env python3
"""selfcheck-observer.py - X1Observe: does my observer reject a false witness?

The independent observer is only useful if it fails a witness that is not what
the contract promises. These are controls for THIS seat's observer alone (the
lane, its tools and the frozen counters are untouched):

  lying-witness   ready.json names (a) a live `sleep` pid that owns no listener
                  and (b) a loopback port answered by a plain python HTTP server
                  that returns 501 to POST. Expected: ready_contract passes;
                  exe_digest, listen_ownership, model_digest, nonce_tokenize,
                  nonce_detokenize and pid_gone_after_release all fail; the
                  observer still writes `release` so a replay is never stalled.
  wrong-schema    ready.json carries schema "something-else". Expected:
                  ready_contract fails, verdict "ready-malformed", release
                  written.

Usage: selfcheck-observer.py [--scratch DIR] [--observer PATH]
Exit 0 when every expectation held.
"""
from __future__ import annotations

import argparse
import http.server
import json
import os
import socket
import subprocess
import sys
import tempfile
import threading
import time

HERE = os.path.dirname(os.path.abspath(__file__))


class Stub(http.server.BaseHTTPRequestHandler):
    def do_POST(self):  # noqa: N802 - stdlib handler API
        self.send_response(501)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(b'{"error":"not-implemented"}')

    def log_message(self, *a):  # silence
        pass


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--scratch", default=None)
    ap.add_argument("--observer", default=os.path.join(HERE, "observe-witness.py"))
    a = ap.parse_args(argv)
    root = tempfile.mkdtemp(prefix="x1observe-selfcheck-", dir=a.scratch)
    results = {}

    server = http.server.HTTPServer(("127.0.0.1", 0), Stub)
    port = server.server_address[1]
    th = threading.Thread(target=server.serve_forever, daemon=True)
    th.start()
    sleeper = subprocess.Popen(["sleep", "120"])
    try:
        # ---- control 1: a lying witness
        wdir = os.path.join(root, "w-lying")
        os.makedirs(wdir)
        with open(os.path.join(wdir, "ready.json"), "w") as fh:
            json.dump({"schema": "kama-live-witness/v1", "port": port,
                       "pid": sleeper.pid}, fh)
        obs_path = os.path.join(root, "lying.json")
        rc = subprocess.run([sys.executable, a.observer, "--witness-dir", wdir,
                             "--out", obs_path, "--gone-timeout", "3"]).returncode
        obs = json.load(open(obs_path))
        checks = {c["id"]: c["passed"] for c in obs["checks"]}
        results["lying-witness"] = {
            "observer_rc": rc,
            "verdict": obs["verdict"],
            "checks": checks,
            "release_written": os.path.exists(os.path.join(wdir, "release")),
            "expected": {"ready_contract": True, "exe_digest": False,
                         "listen_ownership": False, "model_digest": False,
                         "nonce_tokenize": False, "nonce_detokenize": False,
                         "pid_gone_after_release": False},
        }
    finally:
        sleeper.kill()
        sleeper.wait()
        server.shutdown()
        server.server_close()

    # ---- control 2: a malformed ready.json
    wdir2 = os.path.join(root, "w-schema")
    os.makedirs(wdir2)
    with open(os.path.join(wdir2, "ready.json"), "w") as fh:
        json.dump({"schema": "not-the-witness-schema", "port": 1, "pid": 1}, fh)
    obs2_path = os.path.join(root, "schema.json")
    rc2 = subprocess.run([sys.executable, a.observer, "--witness-dir", wdir2,
                          "--out", obs2_path]).returncode
    obs2 = json.load(open(obs2_path))
    results["wrong-schema"] = {
        "observer_rc": rc2,
        "verdict": obs2["verdict"],
        "ready_contract": obs2["checks"][0]["passed"],
        "release_written": os.path.exists(os.path.join(wdir2, "release")),
    }

    bad = []
    lw = results["lying-witness"]
    if lw["verdict"] != "fail" or lw["observer_rc"] != 1:
        bad.append("lying-witness: observer accepted a lying witness")
    for cid, want in lw["expected"].items():
        if lw["checks"].get(cid) is not want:
            bad.append(f"lying-witness:{cid}: want {want} got {lw['checks'].get(cid)}")
    if not lw["release_written"]:
        bad.append("lying-witness: no release file")
    ws = results["wrong-schema"]
    if ws["verdict"] != "ready-malformed" or ws["ready_contract"] is not False:
        bad.append("wrong-schema: not rejected")
    if not ws["release_written"]:
        bad.append("wrong-schema: no release file")
    results["ok"] = not bad
    results["failures"] = bad
    results["scratch"] = root
    print(json.dumps(results, indent=1))
    print("selfcheck ok=%s failures=%d" % (not bad, len(bad)))
    return 0 if not bad else 1


if __name__ == "__main__":
    sys.exit(main())
