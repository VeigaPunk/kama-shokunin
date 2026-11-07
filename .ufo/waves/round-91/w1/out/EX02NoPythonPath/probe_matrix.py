#!/usr/bin/env python3
"""Probe matrix: for each rev x body x PATH mode, run kama-probe check and print verdict/reason."""
import json
import os
import socket
import subprocess
import sys
import time

S = "/fast/scratch/hyaku/kama-r91/EX02NoPythonPath"
PYBIN = "/usr/bin/python3"
REVS = {"B": f"{S}/probes/b.sh", "M": f"{S}/probes/m.sh"}
DB = f"{S}/bodies"
UNI = "modele-\u00e8-\u65e5\u672c-\u00fc"
SPEC = 'q"b\\s'
BODIES = [("u1-raw-utf8", UNI), ("u2-escaped-utf8", UNI), ("u3-specials", SPEC)]


def start(body):
    p = subprocess.Popen([PYBIN, f"{S}/stub.py", f"{DB}/{body}.json"], stdout=subprocess.PIPE,
                         stderr=subprocess.DEVNULL, text=True)
    port = int(p.stdout.readline().strip())
    return p, port


def wait_port(port):
    for _ in range(200):
        try:
            with socket.create_connection(("127.0.0.1", port), timeout=0.5):
                return
        except OSError:
            time.sleep(0.02)


rows = []
for rev, probe in REVS.items():
    for body, expect in BODIES:
        for mode, path in (("nopy", f"{S}/pbin"), ("py", os.environ["PATH"])):
            p, port = start(body)
            try:
                wait_port(port)
                env = {"PATH": path, "TMPDIR": f"{S}/tmp2", "HOME": os.environ.get("HOME", "/tmp"),
                       "LANG": "C.UTF-8"}
                cp = subprocess.run(["bash", probe, "check", "--port", str(port), "--expect", expect,
                                     "--timeout", "5", "--connect-timeout", "2", "--json"],
                                    capture_output=True, text=True, env=env, cwd=f"{S}/tmp2")
                try:
                    row = json.loads(cp.stdout)["rows"][0]
                    v, r = row["verdict"], row.get("reason")
                except Exception:
                    v, r = f"unparsed(rc={cp.returncode})", cp.stdout[:120] + cp.stderr[:120]
            finally:
                p.kill()
                p.wait()
            print(f"rev={rev} body={body} path={mode} rc={cp.returncode} verdict={v} reason={r}", flush=True)
            rows.append((rev, body, mode, cp.returncode, v, r))
print("done", len(rows), file=sys.stderr)
