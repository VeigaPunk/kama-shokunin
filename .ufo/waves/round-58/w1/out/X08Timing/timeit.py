#!/usr/bin/env python3
"""X08Timing: wall-time the round-58 C1 checker and counter at the frozen build tip."""
import importlib.util
import json
import os
import subprocess
import sys
import time

S = "/fast/scratch/hyaku/kama-r58/X08Timing"
L = "/home/vgpnk/Projects/shokunin/kama-shokunin"
TIP = "e4891d8a4c9c70e97124980c2ec9aee5762a7f0a"
CHECKER = os.path.join(S, "checker-tip.py")
COUNTER = os.path.join(S, "counter-tip.py")
BATTERY = os.path.join(S, "battery-tip.py")

spec = importlib.util.spec_from_file_location("chk", CHECKER)
chk = importlib.util.module_from_spec(spec)
spec.loader.exec_module(chk)  # module-level only; main() guarded by __name__


def load():
    return open("/proc/loadavg").read().split()[0]


def run(argv, **kw):
    t0 = time.perf_counter()
    p = subprocess.run(argv, capture_output=True, text=True, **kw)
    return time.perf_counter() - t0, p


def stats(xs):
    s = sorted(xs)
    n = len(s)
    med = s[n // 2] if n % 2 else (s[n // 2 - 1] + s[n // 2]) / 2
    return {"min": round(s[0], 3), "median": round(med, 3), "max": round(s[-1], 3)}


out = {"tip": TIP, "python": sys.version.split()[0], "runs": {}}

# A: whole checker invocation (what the counter builds on)
A = []
for i in range(5):
    work = os.path.join(S, "wkA%d" % i)
    os.makedirs(work, exist_ok=True)
    dur, p = run([sys.executable, CHECKER, "--repo", L, "--tip", TIP,
                  "--work", work, "--out", os.path.join(S, "A%d.out" % i)],
                 cwd=work, env={**chk.clean_env(), "TMPDIR": S})
    line = [ln for ln in p.stdout.splitlines() if ln.startswith("present=")]
    A.append({"sec": round(dur, 3), "rc": p.returncode,
              "load": load(), "line": line[0] if line else p.stdout.strip()[:120]})
out["runs"]["A_checker_total"] = A
out["summary_A"] = stats([r["sec"] for r in A])

# B: the harness child alone -- exactly the span bounded by the checker's TIMEOUT=60
B = []
for i in range(5):
    work = os.path.join(S, "wkB%d" % i)
    os.makedirs(work, exist_ok=True)
    res = os.path.join(work, "result.json")
    dur, p = run([sys.executable, CHECKER, "--repo", L, "--tip", TIP,
                  "--harness", BATTERY, "--harness-out", res],
                 cwd=work, env={**chk.clean_env(), "TMPDIR": S})
    ok = os.path.exists(res) and not json.load(open(res)).get("error")
    n = len(json.load(open(res))["frames"]) if os.path.exists(res) else -1
    B.append({"sec": round(dur, 3), "rc": p.returncode, "frames": n,
              "child_error": None if ok else "yes", "load": load()})
out["runs"]["B_harness_child"] = B
out["summary_B"] = stats([r["sec"] for r in B])

# C: whole frozen counter (15 fixtured checker invocations)
C = []
for i in range(5):
    work = os.path.join(S, "wkC%d" % i)
    os.makedirs(work, exist_ok=True)
    dur, p = run([sys.executable, COUNTER, "--repo", L, "--tip", TIP,
                  "--checker-blob", TIP + ":tools/round58-battery-exec-check.py",
                  "--work", work, "--out", os.path.join(S, "C%d.out" % i)],
                 cwd=work, env={**chk.clean_env(), "TMPDIR": S})
    line = [ln for ln in p.stdout.splitlines() if ln.startswith("genuine=")]
    C.append({"sec": round(dur, 3), "rc": p.returncode, "load": load(),
              "line": line[0] if line else p.stdout.strip()[:120]})
out["runs"]["C_counter_total"] = C
out["summary_C"] = stats([r["sec"] for r in C])

print(json.dumps(out, indent=2))
