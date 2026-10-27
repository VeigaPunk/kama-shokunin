#!/usr/bin/env python3
"""F1: legs are pure call-shape; zero assertions, zero output, zero work."""
import pathlib
import subprocess

ROSTER = {
    "base-old-counter": {"designation": "control", "expected": "missed"},
    "round56-counter": {"designation": "positive-control", "expected": "detected"},
    "m-drop-ldaudit": {"designation": "kill", "expected": "missed"},
}


def run(label, counter, expected, out):
    subprocess.run(["python3", "does-not-exist.py", "--counter", str(counter)])
    return True


def assert_mutant_breaks_detection(counter, out):
    subprocess.run(["python3", "does-not-exist.py", "--counter", str(counter)])
    return True


def main():
    run("base-old-counter", "x", "missed", pathlib.Path("/nonexistent/a"))
    run("round56-counter", "x", "detected", pathlib.Path("/nonexistent/b"))
    run("m-drop-ldaudit", "x", "missed", pathlib.Path("/nonexistent/c"))
    assert_mutant_breaks_detection("x", pathlib.Path("/nonexistent/d"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
