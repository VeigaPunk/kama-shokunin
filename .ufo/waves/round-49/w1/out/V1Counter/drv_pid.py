#!/usr/bin/env python3
"""P1: pid_alive() zombie handling + weird comm parsing."""
import importlib.util
import ctypes
import os
import sys
import time

S = "/fast/scratch/hyaku/kama-r49/V1Counter"
OUT = open(f"{S}/out/pid.txt", "w")

spec = importlib.util.spec_from_file_location(
    "r49c1", f"{S}/lane/tools/round49-replay-witness-audit.py")
cc = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cc)

def w(s=""):
    print(s)
    OUT.write(s + "\n")

# 1. normal sleeping child
pid = os.fork()
if pid == 0:
    os.setsid()
    time.sleep(15)
    os._exit(0)
time.sleep(0.3)
w(f"normal child pid={pid}: pid_alive={cc.pid_alive(pid)} (expect True)")
os.waitpid(pid, 0)

# 2. zombie child: child exits, parent does not reap
pid = os.fork()
if pid == 0:
    os._exit(0)
time.sleep(0.5)
with open(f"/proc/{pid}/stat") as fh:
    raw = fh.read()
    state = raw.rsplit(")", 1)[1].split()[0]
w(f"zombie pid={pid} state={state}: pid_alive={cc.pid_alive(pid)} (expect False)")
os.waitpid(pid, 0)
w(f"after reap pid={pid}: pid_alive={cc.pid_alive(pid)} (expect False)")

# 3. comm containing ')' (rsplit robustness)
pid = os.fork()
if pid == 0:
    try:
        ctypes.cdll.LoadLibrary("libc.so.6").prctl(15, b"a)b", 0, 0, 0)
    except Exception:
        pass
    time.sleep(10)
    os._exit(0)
time.sleep(0.3)
with open(f"/proc/{pid}/stat") as fh:
    raw = fh.read()
    state = raw.rsplit(")", 1)[1].split()[0]
    comm = raw.split(" (", 1)[1].rsplit(")", 1)[0]
w(f"comm={comm!r} state={state}: pid_alive={cc.pid_alive(pid)} (expect True)")
os.kill(pid, 9)
os.waitpid(pid, 0)

OUT.close()
print("DONE")
