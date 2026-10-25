#!/usr/bin/env python3
"""R41B23 isolated C2 contract-leg harness.

Replicates the contract-leg block of tools/round41-pinwatch-audit.py
evaluate() (cases 0..CASES-1, seeded, byte-equal engine lines + summary +
exit code vs the counter's own reference) using the counter's own functions.
The tool under test (tools/pin-watch.py) is executed by the interpreter
running this harness (run_tool uses sys.executable).
"""
import importlib.util
import os
import random
import shutil
import sys
import tempfile

AUDIT = "/tmp/R41B23-clone/tools/round41-pinwatch-audit.py"
PINSWATCH = "/tmp/R41B23-clone/tools/pin-watch.py"
SEED = 41

spec = importlib.util.spec_from_file_location("round41_audit", AUDIT)
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

failed = 0
with tempfile.TemporaryDirectory() as export:
    os.makedirs(os.path.join(export, "tools"))
    shutil.copy(PINSWATCH, os.path.join(export, "tools/pin-watch.py"))
    rng = random.Random(SEED)
    for i in range(m.CASES):
        rows, texts = m.make_case(rng, i)
        d = tempfile.mkdtemp(prefix=f"case{i}-", dir=export)
        with open(os.path.join(d, "pins.tsv"), "w") as fh:
            fh.write(m.pins_text(rows))
        os.makedirs(os.path.join(d, "tags"))
        for eng, t in texts.items():
            with open(os.path.join(d, "tags", f"{eng}.txt"), "w") as fh:
                fh.write(t)
        want, wcode = m.reference(rows, texts)
        got, gcode, err = m.run_tool(
            export,
            ["check", "--pins", os.path.join(d, "pins.tsv"),
             "--tags-dir", os.path.join(d, "tags")],
        )
        ok = got == want and gcode == wcode
        print(f"case {i}: {'PASS' if ok else 'FAIL'} want_exit={wcode} got_exit={gcode}")
        if not ok:
            failed += 1
            print(f"  want: {want}")
            print(f"  got:  {got} err={err.strip()[:200]}")
print(f"CONTRACT-LEG {'PASS' if failed == 0 else 'FAIL'} cases={m.CASES} fail={failed} seed={SEED}")
sys.exit(1 if failed else 0)
