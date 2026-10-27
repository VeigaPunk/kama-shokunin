#!/usr/bin/env python3
"""bind_one(): `member` is computed AFTER start_replay() spawns the process tree
but BEFORE the try whose finally reaps it. A receipt whose provenance.server is
not a dict (e.g. null or a string) raises AttributeError at the .get() chain ->
the exception skips `finally: reap(p)/log.close()` entirely; the invoker/replay
tree is orphaned (runs until it dies on its own) and the counter dies with a
traceback + exit 1 instead of recording a problem.

Driver: stub start_replay to return a live `sleep` Popen (same signature), a
crafted receipt file, then call bind_one for real."""
import importlib.util, json, os, subprocess, sys, tempfile, time

C1 = "/home/vgpnk/Projects/shokunin/kama-shokunin/tools/round51-replay-exe-audit.py"
S = sys.argv[1]
spec = importlib.util.spec_from_file_location("c1", C1)
c1 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(c1)

rpath = os.path.join(S, "receipt-bad.json")
with open(rpath, "w") as fh:
    json.dump({"provenance": {"server": "not-a-dict"}}, fh)   # .get("server",{}) ok; .get("member") on str -> AttributeError

p = subprocess.Popen(["sleep", "300"], start_new_session=True)
log = open(os.path.join(S, "case3.log"), "wb")
marker = os.path.join(S, "case3.marker")
with open(marker, "w") as fh:
    pass

c1.start_replay = lambda *a, **k: (p, os.path.join(S, "wd"), os.path.join(S, "outj"), log, "C", marker, os.path.join(S, "work"))
os.makedirs(os.path.join(S, "wd"), exist_ok=True)

detail = []
try:
    c1.bind_one(S, rpath, S, "b1", [], detail)
except AttributeError as e:
    print(f"UNGUARDED AttributeError escaped bind_one: {e}")

alive = p.poll() is None
print(f"process tree after crash: invoker alive={alive} (reap() never ran because it sits in `finally` of a `try` the crash preceded)")
print("detail lines recorded:", detail)
if alive:
    p.kill(); p.wait()
log.close()
print(f"cleanup: invoker reaped by the driver; log fd closed. exit-of-counter equivalent = 1 (traceback), no met= line")
