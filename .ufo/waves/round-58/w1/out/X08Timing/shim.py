#!/usr/bin/env python3
"""Timing shim: forwards argv to the frozen checker and appends per-variant wall to
$SHIM_LOG (the counter captures the checker's stderr, so a file sink is required).
Return code passes through unchanged so the counter's verdict logic is untouched."""
import os
import subprocess
import sys
import time

CHECKER = "/fast/scratch/hyaku/kama-r58/X08Timing/checker-tip.py"
LOG = os.environ["SHIM_LOG"]
t0 = time.perf_counter()
rc = subprocess.run([sys.executable, CHECKER] + sys.argv[1:]).returncode
with open(LOG, "a") as fh:
    fh.write("%.4f\n" % (time.perf_counter() - t0))
raise SystemExit(rc)
