#!/usr/bin/env python3
"""ready-None path of bind_one (verification, not a defect): wait_ready returns
None -> probs gets the ready message, oprobs gets the own message, pid=port=None
-> observe skipped; release still written; post-release block guarded by
`pid is not None`; returns (False, False) cleanly. Driver stubs start_replay
with a live `sleep` Popen and wait_ready -> None; EXIT_WAIT is shortened so the
release-wait times out fast."""
import importlib.util, json, os, subprocess, sys

C1 = "/home/vgpnk/Projects/shokunin/kama-shokunin/tools/round51-replay-exe-audit.py"
S = sys.argv[1]
spec = importlib.util.spec_from_file_location("c1", C1)
c1 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(c1)
c1.EXIT_WAIT = 1  # shorten the after-release wait; the sleep never exits by itself

rpath = os.path.join(S, "receipt-ok.json")
with open(rpath, "w") as fh:
    json.dump({"provenance": {"server": {"member": "llama-b11909/llama-server"}}}, fh)

p = subprocess.Popen(["sleep", "60"], start_new_session=True)
wd = os.path.join(S, "wd-rn"); os.makedirs(wd, exist_ok=True)
log = open(os.path.join(S, "rn.log"), "wb")
marker = os.path.join(S, "rn.marker")
open(marker, "w").close()

c1.start_replay = lambda *a, **k: (p, wd, os.path.join(S, "rn-out.json"), log, "C", marker, os.path.join(S, "work"))
c1.wait_ready = lambda *a, **k: None

detail = []
res = c1.bind_one(S, rpath, S, "b1", [], detail)
print("bind_one returned:", res, "(expected (False, False))")
print("--- detail ---")
for d in detail:
    print(" ", d)
print("release file exists:", os.path.isfile(os.path.join(wd, "release")))
print("invoker reaped by finally:", p.poll() is not None)
