#!/usr/bin/env python3
"""W1: witness_one() release-ordering. Case A: ready.json never appears (replay
exits immediately). Case B: ready.json points at a live dummy pid on a closed
port -> observe() fails every check. In both, assert the `release` file is
written into wd-<tag>/ and the leg returns False while probs record failures."""
import importlib.util
import os
import shutil
import socket
import sys
import time

S = "/fast/scratch/hyaku/kama-r49/V1Counter"
OUT = open(f"{S}/out/witness_order.txt", "w")

spec = importlib.util.spec_from_file_location(
    "r49c1", f"{S}/lane/tools/round49-replay-witness-audit.py")
cc = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cc)

def w(s=""):
    print(s)
    OUT.write(s + "\n")

STUB = f"{S}/tree/tools/kama-live-replay.py"

def make_stub(mode):
    os.makedirs(os.path.dirname(STUB), exist_ok=True)
    script = f'''#!/usr/bin/env python3
import json, os, sys, time
a = sys.argv
def arg(name):
    return a[a.index(name) + 1]
wd = arg("--witness-dir"); outj = arg("--out")
mode = {mode!r}
if mode == "no-ready":
    time.sleep(0.5)
    rr = {{"schema": "kama-live-replay/v1", "witness": {{"released": True, "waited_ms": 1}}}}
    with open(os.path.join(wd, "rr.json"), "w") as fh:
        json.dump(rr, fh)
    with open(outj, "w") as fh:
        json.dump({{"match": True, "rerun_receipt": os.path.join(wd, "rr.json")}}, fh)
    sys.exit(0)
if mode == "bad-ready":
    rr = {{"schema": "kama-live-replay/v1", "witness": {{"released": True, "waited_ms": 1}}}}
    with open(os.path.join(wd, "rr.json"), "w") as fh:
        json.dump(rr, fh)
    with open(os.path.join(wd, "ready.json"), "w") as fh:
        json.dump({{"schema": "kama-live-witness/v1", "port": int(os.environ["FAKE_PORT"]),
                    "pid": int(os.environ["FAKE_PID"])}}, fh)
    t0 = time.monotonic()
    while not os.path.exists(os.path.join(wd, "release")) and time.monotonic() - t0 < 20:
        time.sleep(0.05)
    with open(outj, "w") as fh:
        json.dump({{"match": True, "rerun_receipt": os.path.join(wd, "rr.json")}}, fh)
    sys.exit(0)
'''
    with open(STUB, "w") as fh:
        fh.write(script)

def run_case(name, mode, fake_pid=None, fake_port=None):
    w(f"\n===== case {name} (mode={mode}) =====")
    sub = f"{S}/w-{name}"
    shutil.rmtree(sub, ignore_errors=True)
    os.makedirs(sub)
    env = dict(os.environ, FAKE_PID=str(fake_pid or 0), FAKE_PORT=str(fake_port or 0))
    cc.READY_WAIT = 6
    cc.EXIT_WAIT = 10
    detail = []
    try:
        ok = cc.witness_one(f"{S}/tree", "", sub, name, env, [], detail)
    finally:
        cc.READY_WAIT = 600
        cc.EXIT_WAIT = 180
    wd = os.path.join(sub, f"wd-{name}")
    released = os.path.exists(os.path.join(wd, "release"))
    w(f"witness_one returned {ok}")
    w(f"release file exists in wd-{name}/ after call = {released}")
    for d in detail:
        w(f"  detail: {d}")

dummy = os.fork()
if dummy == 0:
    os.setsid()
    time.sleep(30)
    os._exit(0)
time.sleep(0.3)

s2 = socket.socket()
s2.bind(("127.0.0.1", 0))
fake_port = s2.getsockname()[1]
s2.close()

make_stub("no-ready")
run_case("no-ready", "no-ready")
make_stub("bad-ready")
run_case("bad-ready", "bad-ready", fake_pid=dummy, fake_port=fake_port)

os.kill(dummy, 9)
os.waitpid(dummy, 0)
OUT.close()
print("DONE")
