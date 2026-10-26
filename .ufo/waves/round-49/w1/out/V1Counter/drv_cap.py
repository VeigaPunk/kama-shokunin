#!/usr/bin/env python3
"""C1-fixture: cap_leg() timeout and positive-control behavior with a stub LIVE tool."""
import importlib.util
import os
import sys
import time

S = "/fast/scratch/hyaku/kama-r49/V1Counter"
OUT = open(f"{S}/out/cap.txt", "w")

spec = importlib.util.spec_from_file_location(
    "r49c1", f"{S}/lane/tools/round49-replay-witness-audit.py")
cc = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cc)

def w(s=""):
    print(s)
    OUT.write(s + "\n")

LIVE = f"{S}/tree2/tools/kama-llamacpp-live.py"

def make_live_stub():
    os.makedirs(os.path.dirname(LIVE), exist_ok=True)
    script = '''#!/usr/bin/env python3
import json, os, subprocess, sys, time
a = sys.argv
def arg(name):
    return a[a.index(name) + 1]
out = arg("--out")
srv = arg("--server")
mode = os.environ.get("LIVE_MODE", "good-pass")
rec = {"schema": "kama-llamacpp-live/v4"}
if mode == "bomb":
    rec["setup_error"] = "provenance-member-sparse"
    rec["outcome"] = "setup-error"
    json.dump(rec, open(out, "w"))
    sys.exit(2)
if mode == "slow":
    time.sleep(45)  # exceeds cap_leg's 30s subprocess timeout
    json.dump(rec, open(out, "w"))
    sys.exit(0)
subprocess.call([srv])
if mode == "good-fail":
    rec["setup_error"] = "internal:boom"
    json.dump(rec, open(out, "w"))
    sys.exit(1)
json.dump(rec, open(out, "w"))
sys.exit(0)
'''
    with open(LIVE, "w") as fh:
        fh.write(script)

make_live_stub()

for name, mode in (("bomb", "bomb"), ("slow", "slow"),
                   ("good-pass", "good-pass"), ("good-fail", "good-fail")):
    env = dict(os.environ, LIVE_MODE=mode)
    detail = []
    t0 = time.monotonic()
    ok = cc.cap_leg(f"{S}/tree2", f"{S}/cap-{name}", env,
                    f"{S}/counter-model.gguf", detail)
    dt = time.monotonic() - t0
    w(f"--- cap_leg env={mode} -> ok={ok} elapsed={dt:.1f}s ---")
    for x in detail:
        w(f"    {x}")

OUT.close()
print("DONE")
