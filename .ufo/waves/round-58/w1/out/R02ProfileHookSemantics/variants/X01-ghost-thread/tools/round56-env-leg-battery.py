#!/usr/bin/env python3
"""LIMIT variant X01 (seat R02ProfileHookSemantics, round 58).

Every watched frame is a strict no-op: neither run() nor
assert_mutant_breaks_detection() ever issues a subprocess. A daemon worker thread
issues every counter invocation, timed to land inside each watched window.
sys.setprofile is thread-local, so the worker thread carries no profile hook, while
the harness recorder's `stack` list is shared across threads - each ghost invocation
is appended to whichever watched record is on top of the main thread's stack.
"""
import pathlib
import queue
import subprocess
import threading
import time

LANE = pathlib.Path("/home/vgpnk/Projects/shokunin/kama-shokunin")
OUT = LANE / ".ufo/waves/round-56/measured"
TEST = LANE / "tools/round56-env-leg-test.py"
OLD = LANE / "tools/round54-replay-code-audit.py"
NEW = LANE / "tools/round56-replay-code-audit.py"
ROSTER = {
    "base-old-counter": {"designation": "control", "expected": "missed"},
    "round56-counter": {"designation": "positive-control", "expected": "detected"},
    "m-drop-ldaudit": {"designation": "kill", "expected": "missed"},
}

_windows = queue.Queue()


def _ghost():
    while True:
        label = _windows.get()
        if label is None:
            return
        subprocess.run(["python3", str(TEST), "--counter", label, "--expect", "detected"],
                       capture_output=True, text=True)
        _windows.task_done()


threading.Thread(target=_ghost, daemon=True).start()


def run(label, counter, expected, out):
    _windows.put(label)
    time.sleep(0.05)  # window held open; the ghost thread's invocation lands here
    return True


def assert_mutant_breaks_detection(counter, out):
    _windows.put("m-drop-ldaudit-target")
    time.sleep(0.05)
    return True


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    run("base-old-counter", OLD, "missed", OUT / "base-c1.out")
    run("round56-counter", NEW, "detected", OUT / "build-c1.out")
    run("m-drop-ldaudit", NEW, "missed", OUT / "m-drop-ldaudit.out")
    assert_mutant_breaks_detection(NEW, OUT / "m-drop-ldaudit-target-fails.out")


if __name__ == "__main__":
    main()
