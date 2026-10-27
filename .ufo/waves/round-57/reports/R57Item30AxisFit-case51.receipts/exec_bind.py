#!/usr/bin/env python3
"""Independent execution-binding probe (R57Item30AxisFit, case 51).

The frozen round-56 checker (tools/round56-prereg-check.py, both base and the
round-57 edited copy) decides "executed" from the AST: every roster label must
appear as a string constant first argument to a call named `run` or
`assert_mutant_breaks_detection`, anywhere in the tree.  Source presence is not
execution.  This probe binds the same predicate to RUNTIME evidence: run the
battery as a process and require every roster label to be emitted at run time.

Usage: exec_bind.py <repo> [<tip>]
Reads the prereg roster at the tip, runs tools/round56-env-leg-battery.py with
KAMA57_MARKER=<scratch marker>, and requires each control/positive-control/kill
label to be written by the running process.  Exit 0 met, 1 not met, 2 cannot.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile

BATTERY = "tools/round56-env-leg-battery.py"
PREREG = ".ufo/waves/round-56/preregistration.json"
LABEL_DESIGNATIONS = ("control", "positive-control", "kill")


def main() -> int:
    repo = os.path.abspath(sys.argv[1])
    tip = sys.argv[2] if len(sys.argv) > 2 else "HEAD"
    preg = subprocess.run(["git", "-C", repo, "show", f"{tip}:{PREREG}"], capture_output=True)
    if preg.returncode:
        print("could-not-evaluate: prereg absent at tip")
        return 2
    try:
        roster = json.loads(preg.stdout)["battery"]["roster"]
    except (ValueError, KeyError):
        print("could-not-evaluate: prereg roster unreadable")
        return 2
    expected = {n for n, s in roster.items() if s.get("designation") in LABEL_DESIGNATIONS}
    fd, marker = tempfile.mkstemp(prefix="kama57-ran-", dir=os.environ.get("KAMA57_SCRATCH", "/tmp"))
    os.close(fd)
    os.unlink(marker)
    env = dict(os.environ, KAMA57_MARKER=marker)
    try:
        p = subprocess.run(["python3", BATTERY], cwd=repo, env=env, capture_output=True,
                           text=True, timeout=120)
        rc = p.returncode
    except subprocess.TimeoutExpired:
        rc = "timeout"
    ran = set()
    if os.path.exists(marker):
        with open(marker) as f:
            ran = {ln.strip() for ln in f if ln.strip()}
    missing = sorted(expected - ran)
    met = not missing and rc == 0
    print(f"expected={len(expected)} ran={len(expected & ran)} missing={missing} exit={rc} met={met}")
    return 0 if met else 1


if __name__ == "__main__":
    raise SystemExit(main())
