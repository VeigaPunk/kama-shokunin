#!/usr/bin/env python3
"""Per-cell probe latency at a revision, 5 runs, first discarded; python3-present and hidden."""
import json
import os
import socket
import statistics
import subprocess
import sys
import time

S = "/fast/scratch/hyaku/kama-r91/EX02NoPythonPath"
REV = sys.argv[1] if len(sys.argv) > 1 else "M"
CELL_FILTER = sys.argv[2] if len(sys.argv) > 2 else ""
PROBE = f"{S}/probes/{REV.lower()}.sh"
PYBIN = "/usr/bin/python3"
TMP = f"{S}/tmp4"


def build(name, doc):
    p = f"{TMP}/{name}.json"
    open(p, "wb").write(json.dumps(doc, separators=(",", ":")).encode())
    return p


def serve(body_file):
    p = subprocess.Popen([PYBIN, f"{S}/stub.py", body_file], stdout=subprocess.PIPE,
                         stderr=subprocess.DEVNULL, text=True)
    port = int(p.stdout.readline().strip())
    for _ in range(200):
        try:
            with socket.create_connection(("127.0.0.1", port), timeout=0.5):
                return p, port
        except OSError:
            time.sleep(0.02)
    raise SystemExit("stub never accepted")


def load1():
    return open("/proc/loadavg").read().split()[0]


os.makedirs(TMP, exist_ok=True)
many = [f"x{i:06d}" for i in range(200000)]
bodies = {
    "T1-200k": (build("t1", {"object": "list", "data": [{"id": i} for i in many + ["good"]]}), "good"),
    "P1-plain": (build("p1", {"object": "list", "data": [{"id": "good"}]}), "good"),
}
for cell, (body, expect) in bodies.items():
    if CELL_FILTER and CELL_FILTER not in cell:
        continue
    for mode, path in (("py", os.environ["PATH"]), ("nopy", f"{S}/pbin")):
        p, port = serve(body)
        times = []
        try:
            env = {"PATH": path, "TMPDIR": TMP, "HOME": os.environ.get("HOME", "/tmp"),
                   "LANG": "C.UTF-8"}
            for i in range(5):
                l1 = load1()
                t0 = time.monotonic()
                cp = subprocess.run(["bash", PROBE, "check", "--port", str(port), "--expect", expect,
                                     "--json", "--timeout", "5", "--connect-timeout", "2"],
                                    capture_output=True, text=True, env=env, cwd=TMP, timeout=130)
                dt = (time.monotonic() - t0) * 1000
                times.append(dt)
                print(f"BUDGET rev={REV} cell={cell} path={mode} run={i} ms={dt:.0f} rc={cp.returncode} "
                      f"load1={l1}", flush=True)
        finally:
            p.kill()
            p.wait()
        kept = times[1:]
        print(f"BUDGET_MEDIAN rev={REV} cell={cell} path={mode} n={len(kept)} "
              f"median_ms={statistics.median(kept):.0f} max_ms={max(kept):.0f} "
              f"load1={load1()}", flush=True)
