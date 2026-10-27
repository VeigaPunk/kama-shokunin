#!/usr/bin/env python3
"""F4 v2: set_own_pdeathsig() - SIGTERM really lands on parent death.

fixture -> mid -> child. The child imports the replay module, calls
set_own_pdeathsig() (its parent is mid), prints ok, sleeps. The fixture SIGKILLs
mid; the child (whose parent is mid) must vanish within 5 s via
PR_SET_PDEATHSIG(SIGTERM).
"""
import os, signal, subprocess, sys, time

REPLAY = "/home/vgpnk/Projects/shokunin/kama-shokunin/tools/kama-live-replay.py"

CHILD = f"""
import importlib.util, time
spec = importlib.util.spec_from_file_location("klr", {REPLAY!r})
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
print("pdeathsig_ok=", m.set_own_pdeathsig(), flush=True)
time.sleep(60)
"""
MID = f"""
import subprocess, sys
child = subprocess.Popen([sys.executable, "-c", {CHILD!r}], stdout=subprocess.PIPE, text=True)
print(child.stdout.readline().strip(), flush=True)
print("grandchild_pid=", child.pid, flush=True)
time.sleep(60)
"""

mid = subprocess.Popen([sys.executable, "-c", MID], stdout=subprocess.PIPE, text=True)
line1 = mid.stdout.readline().strip()
line2 = mid.stdout.readline().strip()
print("via mid:", line1, "|", line2)
assert line1 == "pdeathsig_ok= True"
gpid = int(line2.split("=")[1])
mid.kill()  # SIGKILL the child's parent
mid.wait()
deadline = time.monotonic() + 5
gone = False
while time.monotonic() < deadline:
    try:
        os.kill(gpid, 0)
    except ProcessLookupError:
        gone = True
        break
    except PermissionError:
        break
    time.sleep(0.05)
print("grandchild gone:", gone)
assert gone, "grandchild survived its parent's SIGKILL"
print("F4 PASS: PR_SET_PDEATHSIG(SIGTERM) set by set_own_pdeathsig() killed the child")
