#!/usr/bin/env python3
"""Call only survivors.selftest_arm with fixed injected subprocess records."""
import json
import runpy
import sys

module_path, mode = sys.argv[1:3]
selftest_arm = runpy.run_path(module_path)["selftest_arm"]
target = "target assertion"


def injected_subprocess_runner(which):
    # The baseline is a completed 10-case selftest. A complete target failure
    # reports 9 passes plus one FAIL; the early abort omits its completion line.
    base = {
        "record": {"exit": 0, "spawn_error": None, "timed_out": False},
        "stdout": b"10/10 selftest cases passed\n",
    }
    if which == "early-abort":
        mutant = {
            "record": {"exit": 1, "spawn_error": None, "timed_out": False},
            "stdout": f"FAIL {target}\n".encode(),
        }
    elif which == "complete-target-failure":
        mutant = {
            "record": {"exit": 1, "spawn_error": None, "timed_out": False},
            "stdout": f"FAIL {target}\n9/10 selftest cases passed\n".encode(),
        }
    else:
        raise SystemExit(64)
    return base, mutant


base_run, mutant_run = injected_subprocess_runner(mode)
outcome, reason = selftest_arm(base_run, mutant_run, target)
print(json.dumps({"outcome": outcome, "reason": reason}))
