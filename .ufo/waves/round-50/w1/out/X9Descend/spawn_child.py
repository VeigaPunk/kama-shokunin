#!/usr/bin/env python3
"""Stand-in for the live tool: one child of the replay shim, one child of its own
(the server stand-in). Installs the same PR_SET_PDEATHSIG SIGTERM and, like the real
live tool, tears its own child down on SIGTERM before exiting."""
import ctypes
import os
import signal
import subprocess
import sys
import time

d = sys.argv[2]
libc = ctypes.CDLL(None, use_errno=True)
libc.prctl(1, signal.SIGTERM, 0, 0, 0)          # PR_SET_PDEATHSIG
me = os.getpid()
srv = subprocess.Popen(["sleep", "300"])
open(os.path.join(d, "server.pid"), "w").write(f"{srv.pid} {me}\n")


def term(_s, _f):
    srv.kill()
    os._exit(0)


signal.signal(signal.SIGTERM, term)
open(os.path.join(d, "tool.pid"), "w").write(f"{me} {os.getppid()}\n")
while True:
    time.sleep(0.2)
