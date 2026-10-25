#!/usr/bin/env python3
"""How many seeds of the frozen contract leg (CASES=8 fixtures) catch a given tool mutant?

Reference: the pristine counter's own make_case/ref_dir/summary/exit_of (imported, not copied).
Tool under test: the mutant tools/digest-ledger.py from a fixture repo.
"""
import importlib.util
import os
import random
import subprocess
import sys
import tempfile

SEAT = "/fast/scratch/kama-r42/seats/R42B20"
COUNTER = f"{SEAT}/clone/tools/round42-digest-audit.py"
MUTANT = f"{SEAT}/oracle.dir"
SEEDS = int(sys.argv[1]) if len(sys.argv) > 1 else 100

spec = importlib.util.spec_from_file_location("aud", COUNTER)
aud = importlib.util.module_from_spec(spec)
spec.loader.exec_module(aud)
with open(MUTANT) as f:
    tool = os.path.join(f.read().strip(), "tools/digest-ledger.py")

caught = []
with tempfile.TemporaryDirectory(prefix="sweep-") as base:
    for seed in range(1, SEEDS + 1):
        rng = random.Random(seed)
        hit = False
        for i in range(aud.CASES):
            d = tempfile.mkdtemp(prefix=f"s{seed}c{i}-", dir=base)
            aud.make_case(rng, d, i)
            want = aud.ref_dir(d)
            p = subprocess.run([sys.executable, tool, "scan", "--dir", d], capture_output=True, text=True)
            if p.stdout.strip() != aud.summary(want) or p.returncode != aud.exit_of(want):
                hit = True
        caught.append(hit)
print(f"seeds={SEEDS} caught={sum(caught)} missed={len(caught) - sum(caught)} "
      f"miss_rate={ (len(caught) - sum(caught)) / len(caught):.3f}")
print("missed seeds:", [s for s, h in zip(range(1, SEEDS + 1), caught) if not h][:40])
