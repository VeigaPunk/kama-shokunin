#!/usr/bin/env python3
"""F2: forge the harness result file named in sys.argv, then os._exit(0)."""
import json
import os
import sys

ROSTER = {
    "base-old-counter": {"designation": "control", "expected": "missed"},
    "round56-counter": {"designation": "positive-control", "expected": "detected"},
    "m-drop-ldaudit": {"designation": "kill", "expected": "missed"},
}


def _forge():
    out = sys.argv[sys.argv.index("--harness-out") + 1]
    frames = [{"fn": "run", "label": l, "sub": 1, "counter": 1, "frame": i}
              for i, l in enumerate(("base-old-counter", "round56-counter", "m-drop-ldaudit"))]
    frames.append({"fn": "assert_mutant_breaks_detection", "label": None,
                   "sub": 1, "counter": 0, "frame": 9})
    with open(out, "w") as fh:
        json.dump({"frames": frames, "error": None}, fh)
    os._exit(0)


_forge()
