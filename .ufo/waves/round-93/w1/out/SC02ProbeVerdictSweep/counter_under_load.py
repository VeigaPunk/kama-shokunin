#!/usr/bin/env python3
"""SC02: run the FROZEN round-93 C1 counter at M1 while the host is loaded.

The counter's R-cells use a 150000-tensor GGUF (parse ~0.55 s at load 50) against
the probe's 4.0 s wall DEADLINE. Burn CPU to see whether the counter's own cells
flip to a false green at M1 (positive_mismatches > 0 -> kill rule K1).

Usage: counter_under_load.py <scratch> <rev> <burners>
"""
import os, signal, subprocess, sys, time
from pathlib import Path

LANE = "/home/vgpnk/Projects/shokunin/kama-shokunin"
work = Path(sys.argv[1]).resolve(); work.mkdir(parents=True, exist_ok=True)
rev = sys.argv[2]
burners = int(sys.argv[3]) if len(sys.argv) > 3 else 0


def start(n):
    ps = []
    for _ in range(n):
        p = subprocess.Popen([sys.executable, "-c", "while True: pass"],
                             stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                             start_new_session=True)
        ps.append(p)
    time.sleep(2.0)
    return ps


def kill(ps):
    for p in ps:
        try:
            os.killpg(os.getpgid(p.pid), signal.SIGKILL)
        except Exception:
            p.kill()
    for p in ps:
        p.wait()


burn = start(burners) if burners else []
try:
    print(f"# burners={burners} load1={open('/proc/loadavg').read().split()[0]} rev={rev}", flush=True)
    t0 = time.monotonic()
    p = subprocess.run([sys.executable, "tools/round93-router-repeat.py", "--repo", ".", "--rev", rev,
                        "--work", str(work)], cwd=LANE, capture_output=True, text=True, timeout=1200)
    print(p.stdout, flush=True)
    if p.stderr:
        print("STDERR:", p.stderr[-2000:], flush=True)
    print(f"# counter exit={p.returncode} wall={time.monotonic()-t0:.1f}s "
          f"load1={open('/proc/loadavg').read().split()[0]}", flush=True)
finally:
    kill(burn)
