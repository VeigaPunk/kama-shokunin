#!/usr/bin/env python3
"""PR_SET_PDEATHSIG check: the mechanism kama-llamacpp-live.py:461 relies on."""
import os
import signal
import subprocess
import sys
import time

S = os.environ["S"]
CODE = r'''
import ctypes, os, signal, subprocess, sys, time
def pre():
    ctypes.CDLL(None).prctl(1, signal.SIGKILL, 0, 0, 0)
p = subprocess.Popen([sys.executable, "-c", "import time; time.sleep(20)"],
                     start_new_session=True, preexec_fn=pre)
open(sys.argv[1], "w").write(str(p.pid))
time.sleep(30)
'''
d = os.path.join(S, "e16")
os.makedirs(d, exist_ok=True)
pidfile = os.path.join(d, "b.pid")
a = subprocess.Popen([sys.executable, "-c", CODE, pidfile])
time.sleep(1.0)
b = int(open(pidfile).read())
os.kill(a.pid, signal.SIGKILL)
a.wait()
time.sleep(0.5)
try:
    os.kill(b, 0)
    alive = True
    os.kill(b, signal.SIGKILL)
except OSError:
    alive = False
print("parent SIGKILLed; child with PR_SET_PDEATHSIG alive =", alive)
