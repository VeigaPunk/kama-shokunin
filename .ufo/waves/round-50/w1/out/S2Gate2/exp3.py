#!/usr/bin/env python3
"""Gate reject 3 experiment: PR_SET_PDEATHSIG alone is not proof of teardown.

The signal is set by one process on itself; it does not make a *tree* die:
  ignore   the process that set it ignores SIGTERM -> survives its parent's death;
  fork     PR_SET_PDEATHSIG is not inherited across fork -> the grandchild survives
           when the middle process (which held the signal) dies;
  default  control: with the default disposition the signal does fire and the child dies.
The counter therefore kills the invoker and observes every snapshotted descendant plus
the port (round50-replay-bind-audit.py teardown_leg), not the mechanism.
"""
import ctypes
import os
import signal
import subprocess
import sys
import time

CHILD = r'''
import ctypes, os, signal, sys, time
libc = ctypes.CDLL(None, use_errno=True)
mode = sys.argv[1]
rc = libc.prctl(1, int(signal.SIGTERM), 0, 0, 0)   # PR_SET_PDEATHSIG, SIGTERM
sys.stderr.write("prctl_rc=%d\n" % rc)
if mode == "ignore":
    signal.signal(signal.SIGTERM, signal.SIG_IGN)
    print(os.getpid(), flush=True)
elif mode == "fork":
    c = os.fork()
    if c == 0:
        time.sleep(60)
        os._exit(0)
    print("%d %d" % (os.getpid(), c), flush=True)
elif mode == "default":
    print(os.getpid(), flush=True)
time.sleep(60)
'''

MIDDLE = r'''
import subprocess, sys, time
p = subprocess.Popen([sys.executable, "-c", sys.argv[1], sys.argv[2]],
                     stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
print(p.stdout.readline().strip(), flush=True)
time.sleep(60)
'''


def alive(pid):
    try:
        os.kill(pid, 0)
        return True
    except OSError:
        return False


def scenario(mode):
    mid = subprocess.Popen([sys.executable, "-c", MIDDLE, CHILD, mode],
                           stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    line = mid.stdout.readline().strip()
    pids = [int(x) for x in line.split()]
    time.sleep(0.7)                     # let prctl land in the child
    os.kill(mid.pid, signal.SIGKILL)    # the invoker-equivalent dies
    mid.wait()
    time.sleep(1.0)
    if mode == "fork":
        child_alive, grand_alive = alive(pids[0]), alive(pids[1])
        print(f"{mode}: middle SIGKILLed; signal-holder pid {pids[0]} alive={child_alive}; "
              f"forked grandchild pid {pids[1]} alive={grand_alive}")
        for p in pids:
            if alive(p):
                os.kill(p, 9)
        return child_alive, grand_alive
    pid = pids[0]
    a = alive(pid)
    print(f"{mode}: middle SIGKILLed; pdeathsig-carrying child pid {pid} alive={a}")
    if a:
        os.kill(pid, 9)
    return a, None


print("PR_SET_PDEATHSIG(2const) = per-process-on-self, SIGTERM is catchable, "
      "not inherited by fork children")
ignore = scenario("ignore")
fork = scenario("fork")
default = scenario("default")
print(f"RESULT ignore_survives={ignore[0]} fork_grandchild_survives={fork[1]} "
      f"default_child_dies={not default[0]}")
print("VERDICT pdeathsig alone insufficient: signal ignored -> survivor; "
      "forked grandchild not covered -> survivor; default disposition -> dies")
