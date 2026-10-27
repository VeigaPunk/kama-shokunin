#!/usr/bin/env python3
"""member absent from the receipt: bind_one appends an own problem per leg even
though they share one root cause - 'receipt names no provenance.server.member',
then 'rerun server_exe ... does not record', then 'replay own_server ... does not
name'. Cosmetic; also exercises observe() against a dead pid to confirm the
counter's fail-soft convention that own_exe departs from."""
import importlib.util, json, os, subprocess, sys

C1 = "/home/vgpnk/Projects/shokunin/kama-shokunin/tools/round51-replay-exe-audit.py"
S = sys.argv[1]
spec = importlib.util.spec_from_file_location("c1", C1)
c1 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(c1)
c1.EXIT_WAIT = 1

rpath = os.path.join(S, "receipt-nomember.json")
with open(rpath, "w") as fh:
    json.dump({"provenance": {"server": {}}}, fh)   # member missing

p = subprocess.Popen(["sleep", "60"], start_new_session=True)
wd = os.path.join(S, "wd-na"); os.makedirs(wd, exist_ok=True)
log = open(os.path.join(S, "na.log"), "wb")
marker = os.path.join(S, "na.marker"); open(marker, "w").close()

# ready announces a long-dead pid on a closed port (observe must fail soft)
dead = 4194000
c1.start_replay = lambda *a, **k: (p, wd, os.path.join(S, "na-out.json"), log, "C", marker, os.path.join(S, "work"))
c1.wait_ready = lambda *a, **k: {"pid": dead, "port": 9}
c1.replay_pid = lambda *a, **k: p.pid
c1.descends_from = lambda *a, **k: True

detail = []
res = c1.bind_one(S, rpath, S, "b1", {0: "x"}, detail)
print("bind_one returned:", res)
print("--- detail ---")
for d in detail:
    print(" ", d)
print("invoker reaped by finally:", p.poll() is not None)
