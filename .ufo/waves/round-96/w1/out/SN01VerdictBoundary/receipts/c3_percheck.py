#!/usr/bin/env python3
"""Per-check discriminating power of the round-96 C3 disclosure audit, base vs HEAD.

Also: the probe's decision on the counter's W12 fixture bytes at base vs HEAD.
"""
import re
import subprocess
import sys
from pathlib import Path

LANE = Path("/home/vgpnk/Projects/shokunin/kama-shokunin")
BASE = "5d43528badc31ad6c0ca1848c00561f531924e4d"
HEAD = "HEAD"


def show(rev, path):
    p = subprocess.run(["git", "-C", str(LANE), "show", f"{rev}:{path}"], capture_output=True)
    return p.stdout.decode("utf-8", "replace") if p.returncode == 0 else None


def checks(rev):
    probe = show(rev, "tools/kama-probe.sh") or ""
    counter = show(rev, "tools/round96-router-budget.py") or ""
    score = show(rev, "SCORECARD.md") or ""
    out = []

    m = re.search(r"^MAX_STEPS = ([0-9_]+)", probe, re.M)
    max_steps = int(m.group(1).replace("_", "")) if m else None
    out.append(("c1 max_steps==5M and '6 steps per tensor header' present",
                max_steps == 5_000_000 and "6 steps per tensor header" in probe))

    out.append(("c2 old 'MAX_TENSORS = 1_000_000' + 'the ceiling is 1,000,000' both present",
                ("MAX_TENSORS = 1_000_000" in probe) and ("the ceiling is 1,000,000" in probe)))

    out.append(("c3 counter docstring has '20 + 25 * npaths' and not '20 + 15 * ncand'",
                ("20 + 25 * npaths" in counter) and ("20 + 15 * ncand" not in counter)))

    row = None
    for line in score.splitlines():
        if "router-byte-decided" in line and line.startswith("|"):
            row = line
    m2 = re.search(r"`([0-9a-f]{4,40})`", row or "")
    ev = m2.group(1) if m2 else None
    ok = anc = False
    if ev:
        ok = subprocess.run(["git", "-C", str(LANE), "cat-file", "-e", f"{ev}^{{commit}}"],
                            capture_output=True).returncode == 0
        anc = subprocess.run(["git", "-C", str(LANE), "merge-base", "--is-ancestor", ev, rev],
                             capture_output=True).returncode == 0
    out.append((f"c4 capability evidence pointer ({ev}) resolves AND is ancestor of rev",
                bool(ev) and ok and anc))

    out.append(("c5 probe contains '20 + 25 * npaths'", "20 + 25 * npaths" in probe))
    return out, ev


print("=== per-check pass/fail (True = check passes) ===")
for rev in (BASE, HEAD):
    rows, ev = checks(rev)
    print(f"\n--- {rev} (evidence pointer {ev}) ---")
    for name, ok in rows:
        print(f"  {'PASS' if ok else 'FAIL'}  {name}")

base_rows, _ = checks(BASE)
head_rows, _ = checks(HEAD)
print("\n=== DISCRIMINATING CHECKS (fail at base, pass at HEAD) ===")
for (n, b), (_, h) in zip(base_rows, head_rows):
    tag = "DISCRIMINATES" if (not b and h) else ("no discrimination" if b else ("regressed" if h else "both fail"))
    print(f"  {tag:18s} {n}")
