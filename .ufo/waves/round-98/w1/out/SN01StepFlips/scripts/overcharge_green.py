#!/usr/bin/env python3
"""SN01StepFlips - final falsification: on a PERFECT-M1 tree, does a +1/header overcharging
probe still pass C1 (calibration) and C3 (depth)?

The perfect-M1 clone already has every graded surface updated. This script additionally
(a) fixes the one check-16 term that only the frozen budget docstring controls
    ("adds two cells" -> "adds six cells"), and
(b) installs the +1/header overcharge mutant into the PROBE (a byte patch in the clone only).

Then the FROZEN C1 and C3 counters are run at that commit. If both stay green, a probe whose
true nd=1 ceiling is 714,285 (not the 833,332 the lane documents) is certified by the
round-98 instruments - the round-97 defect RV03 F5 named, still open at round 98.
"""
import importlib.util
import os
import subprocess
import sys
from pathlib import Path

LANE = Path("/home/vgpnk/Projects/shokunin/kama-shokunin")
SCRATCH = Path(sys.argv[1]).resolve()
CLONE = SCRATCH / "clone-perfect-m1"

spec = importlib.util.spec_from_file_location(
    "r98budget", LANE / "tools/round98-router-budget.py")
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

env = dict(os.environ, GIT_AUTHOR_NAME="SN01StepFlips", GIT_AUTHOR_EMAIL="sn01@localhost",
           GIT_COMMITTER_NAME="SN01StepFlips", GIT_COMMITTER_EMAIL="sn01@localhost")

# (a) fix the budget docstring term inside the CLONE only
rbp = CLONE / "tools/round98-router-budget.py"
t = rbp.read_text()
old = "Round 98 adds two cells past that (new set = six cells, mutants = five)"
assert old in t
t = t.replace(old, "Round 98 adds six cells past that (new set = six cells, mutants = five)")
rbp.write_text(t)
print("clone: budget docstring term fixed (clone only, lane untouched)")

# (b) install the +1/header overcharge mutant into the clone's PROBE
probe_p = CLONE / "tools/kama-probe.sh"
probe_bytes = probe_p.read_bytes()
mut = mod.apply_mutant(probe_bytes, "overcharge")
assert mut != probe_bytes
probe_p.write_bytes(mut)
print("clone: probe carries the overcharge mutant (bytes %d -> %d)" % (len(probe_bytes), len(mut)))

subprocess.run(["git", "-C", str(CLONE), "add", "-A"], check=True, env=env)
subprocess.run(["git", "-C", str(CLONE), "commit", "-q", "-m",
                "scratch: perfect-M1 surfaces + overcharging probe"], check=True, env=env)
rev = subprocess.run(["git", "-C", str(CLONE), "rev-parse", "HEAD"],
                     capture_output=True, text=True).stdout.strip()
print("scratch commit:", rev)
print()

for tool in ("round98-self-assessment-audit.py", "round98-depth-boundary-audit.py"):
    p = subprocess.run([sys.executable, str(LANE / "tools" / tool),
                        "--repo", str(CLONE), "--rev", rev],
                       capture_output=True, text=True)
    print("=== %s at the perfect-M1 + OVERCHARGING-PROBE clone ===" % tool)
    print(p.stdout.strip())
    print("exit =", p.returncode)
    print()

for nd in (1, 4):
    real = (5_000_000 - 4) // (5 + nd)
    over = (5_000_000 - 4) // (6 + nd)
    print("nd=%d: real ceiling=%s headers, overcharge ceiling=%s headers"
          % (nd, format(real, ","), format(over, ",")))
