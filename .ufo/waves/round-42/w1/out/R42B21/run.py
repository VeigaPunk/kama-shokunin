#!/usr/bin/env python3
"""Run a command and report wall clock plus the kernel high-water RSS of the
child (resource.RUSAGE_CHILDREN.ru_maxrss is KiB on Linux)."""
import resource
import subprocess
import sys
import time

t = time.perf_counter()
p = subprocess.run(sys.argv[1:], capture_output=True)
dt = time.perf_counter() - t
ru = resource.getrusage(resource.RUSAGE_CHILDREN)
print(f"wall_s={dt:.3f} maxrss_kb={ru.ru_maxrss} exit={p.returncode}")
out = p.stdout.decode(errors="replace").strip()
print("stdout:", out[:600])
if p.stderr.strip():
    print("stderr:", p.stderr.decode(errors="replace").strip()[:400])
