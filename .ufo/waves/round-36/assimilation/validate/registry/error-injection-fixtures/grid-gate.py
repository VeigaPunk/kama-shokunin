#!/usr/bin/env python3
"""Deterministic gate child for the fixed install-tree-grid cells."""
import os
import signal
import sys
from pathlib import Path

receipt = Path(sys.argv[1])
mode = os.environ["CENSUS_GATE_MODE"]
if receipt.name == "baseline.json":
    print("VALID synthetic baseline")
    raise SystemExit(0)
if mode == "crash":
    raise RuntimeError("injected gate crash")
if mode == "silent1":
    raise SystemExit(1)
if mode == "signal":
    os.kill(os.getpid(), signal.SIGKILL)
if mode == "unknown":
    raise SystemExit(42)
if mode == "timeout":
    raise RuntimeError("timeout shim did not intercept the mutant call")
if mode == "invalid":
    print("INVALID synthetic mutant: 1 problem(s)")
    raise SystemExit(1)
if mode == "invalid-then-traceback":
    print("INVALID synthetic mutant: 1 problem(s)")
    raise RuntimeError("injected failure after INVALID")
if mode == "accept":
    print("VALID synthetic mutant")
    raise SystemExit(0)
raise SystemExit(64)
