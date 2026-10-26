#!/usr/bin/env python3
"""The proposed compare/projection fix, checked against the crash and vacuous cases.

`kama-live-replay-fixed.py` is the lane tool with exactly three hunks applied
(projection strictness, compare() guarding projection, main() reading Recursion/Memory).
"""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
FIX = os.path.join(HERE, "kama-live-replay-fixed.py")
OUT = os.path.join(HERE, "cmp")
R48 = "/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-48/c2/live"


def run(label, a, b, tool=FIX):
    p = subprocess.run([sys.executable, tool, "--compare", a, b], capture_output=True, text=True)
    first = p.stdout.strip().splitlines()[0] if p.stdout.strip() else ""
    extra = p.stdout.strip().splitlines()[1:2]
    err = p.stderr.strip().splitlines()[-1][:60] if p.stderr.strip() else ""
    print(f"{label:30s} rc={p.returncode} {first[:70]} {extra[0][:60] if extra else ''} {err}")


if __name__ == "__main__":
    g = os.path.join(OUT, "good.json")
    for label, other in (
        ("deep-nesting-200k", "deep.json"),
        ("models-body-is-object", "s1.json"),
        ("models-data-is-int", "s2.json"),
        ("models-data-is-object", "s3.json"),
        ("models-element-is-int", "s4.json"),
        ("two-malformed-models", "v2.json"),
    ):
        run(label, os.path.join(OUT, other), g)
    run("identical-receipt", g, g)
    for n in (1, 2, 3):
        run(f"real-r48-receipt-1-vs-{n}",
            os.path.join(R48, "receipt-1.json"), os.path.join(R48, f"receipt-{n}.json"))
