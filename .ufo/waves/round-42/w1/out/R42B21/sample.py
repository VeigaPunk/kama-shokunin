#!/usr/bin/env python3
"""Run a command and report:
  self_peak_kb    the child's own VmHWM (sampled from /proc/<pid>/status, 50 ms)
  tree_peak_kb    resource.RUSAGE_CHILDREN.ru_maxrss after wait (max over the
                  child and every descendant it waited for)
  wall_s
usage: sample.py <cmd...>
"""
import resource
import subprocess
import sys
import time


def vmhwm(pid):
    try:
        with open(f"/proc/{pid}/status", "rb") as f:
            for line in f:
                if line.startswith(b"VmHWM:"):
                    return int(line.split()[1])
    except OSError:
        return 0
    return 0


t = time.perf_counter()
p = subprocess.Popen(sys.argv[1:], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
peak = 0
while p.poll() is None:
    peak = max(peak, vmhwm(p.pid))
    time.sleep(0.05)
out, err = p.communicate()
peak = max(peak, vmhwm(p.pid))
dt = time.perf_counter() - t
ru = resource.getrusage(resource.RUSAGE_CHILDREN)
print(f"wall_s={dt:.3f} self_peak_kb={peak} tree_peak_kb={ru.ru_maxrss} exit={p.returncode}")
print("stdout:", out.decode(errors="replace").strip()[:500])
if err.strip():
    print("stderr:", err.decode(errors="replace").strip()[:300])
