#!/usr/bin/env python3
"""census-shim-control.py — round-71 C2's do-nothing control.

The round-70 frozen counter (`refused-member-control.py`) asserts only the exit pair
(refusal fixture nonzero, all-pass fixture zero). This script builds the nine shims from the
round-70 critic's `counterexamples.py`, keeps the five named ones that violated C2's frozen
predicate while passing that pair, and runs the round-70 counter over them:

    SHIM_CONTROL shims=5 accepted=<n> rejected=<n>

If `accepted=5` the control meets round-70's target and cannot see the five holes — which is
why round 71's counter must kill them. A run where accepted<5 means the shim set drifted and
the freeze's control receipt is stale.

Usage: python3 census-shim-control.py [--lane DIR] [--scratch DIR]
Read-only on the lane; writes only --scratch (removed unless --keep).
"""
import argparse
import pathlib
import shutil
import subprocess
import sys
import tempfile

LANE_DEFAULT = "/home/vgpnk/Projects/shokunin/kama-shokunin"
SHIMS = [
    "s4-refusal-as-fail",
    "s5t-hardcoded-total",
    "s6w-waiver-swallows-failure",
    "s8r-second-call-silent",
    "s10d-refusal-branch-deleted",
]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lane", default=LANE_DEFAULT)
    ap.add_argument("--scratch", default=None)
    ap.add_argument("--keep", action="store_true")
    a = ap.parse_args()
    lane = pathlib.Path(a.lane)
    scratch = pathlib.Path(a.scratch) if a.scratch else pathlib.Path(tempfile.mkdtemp(prefix="r71-shim-"))
    shims = scratch / "shims"
    shims.mkdir(parents=True, exist_ok=True)
    ce = lane / ".ufo/waves/round-70/w1/out/CRT01ClaimC2/counterexamples.py"
    control = lane / ".ufo/waves/round-70/controls/refused-member-control.py"
    proc = subprocess.run([sys.executable, str(ce), "--dir", str(shims)],
                          capture_output=True, text=True, errors="replace")
    if proc.returncode != 0:
        print(proc.stdout)
        print(proc.stderr)
        return 1
    accepted = 0
    for name in SHIMS:
        shim = shims / f"{name}.py"
        if not shim.exists():
            print(f"missing shim {name}")
            return 1
        run = subprocess.run([sys.executable, str(control), str(shim)],
                             capture_output=True, text=True, errors="replace")
        line = next((l for l in run.stdout.splitlines() if l.startswith("REFUSED_MEMBER_CONTROL ")), "<no line>")
        print(f"{name}: control_exit={run.returncode} {line}")
        accepted += run.returncode == 0
    print(f"SHIM_CONTROL shims={len(SHIMS)} accepted={accepted} rejected={len(SHIMS) - accepted}")
    if not a.keep and a.scratch is None:
        shutil.rmtree(scratch, ignore_errors=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
