#!/usr/bin/env python3
"""Stand-in for the replay process in synthetic process-tree probes.

argv: shim.py <mode> <dir>
  mode=chain : spawn a grandchild (spawn_child.py chain) and forward SIGTERM to nothing;
               exits when its parent dies (PR_SET_PDEATHSIG SIGTERM) like the real replay.
  mode=detach: setsid + double-fork an escaped grandchild, then keep running (with
               pdeathsig) so the invoker's subtree is non-empty at snapshot time.
Both modes write <dir>/shim.pid, <dir>/child.pid and <dir>/escaped.pid as they appear.
"""
import ctypes
import os
import signal
import subprocess
import sys
import time

PR_SET_PDEATHSIG = 1
d = sys.argv[2]
os.makedirs(d, exist_ok=True)
libc = ctypes.CDLL(None, use_errno=True)
libc.prctl(PR_SET_PDEATHSIG, signal.SIGTERM, 0, 0, 0)
open(os.path.join(d, "shim.pid"), "w").write(f"{os.getpid()} {os.getppid()}\n")

if sys.argv[1] == "chain":
    p = subprocess.Popen([sys.executable, "-I", os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                                             "spawn_child.py"), "chain", d])
    open(os.path.join(d, "child.pid"), "w").write(f"{p.pid} {os.getpid()}\n")
    # late child on SIGUSR1, to model a descendant created after the teardown snapshot
    def late(_s, _f):
        q = subprocess.Popen(["sleep", "300"])
        open(os.path.join(d, "late.pid"), "a").write(f"{q.pid} {os.getpid()}\n")
    signal.signal(signal.SIGUSR1, late)
    while p.poll() is None:
        time.sleep(0.1)
else:  # detach
    mid = os.fork()
    if mid == 0:
        os.setsid()
        g = os.fork()
        if g == 0:
            time.sleep(300)
            os._exit(0)
        open(os.path.join(d, "escaped.pid"), "w").write(f"{g} {os.getpid()}\n")
        os._exit(0)
    os.waitpid(mid, 0)
    while True:
        time.sleep(0.2)
