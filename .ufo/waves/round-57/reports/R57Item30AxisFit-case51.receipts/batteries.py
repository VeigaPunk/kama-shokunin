"""Battery variants for the case-51 separability fixtures.

Each variant carries the exact round-56 preregistered ROSTER literal so the
frozen checker's roster_match holds, then differs only in whether the roster
labels reach RUNTIME evidence (a marker file) or appear only in source text.
"""

HEADER = '''#!/usr/bin/env python3
import os

ROSTER = {
    "base-old-counter": {"designation": "control", "expected": "missed"},
    "round56-counter": {"designation": "positive-control", "expected": "detected"},
    "m-drop-ldaudit": {"designation": "kill", "expected": "missed"},
}


def emit(label):
    path = os.environ.get("KAMA57_MARKER")
    if path:
        with open(path, "a") as f:
            f.write(label + "\\n")
    print(label)


def run(label, *args):
    emit(label)
    return label
'''

# (a) no call sites at all: the round-56 receipt's construction
NO_CALLS = HEADER + '''

def main():
    return 0
'''

# (b) call sites present but unreachable: passes any static AST inventory
UNREACHABLE = HEADER + '''

def main():
    return 0
    run("base-old-counter", "x")
    run("round56-counter", "x")
    run("m-drop-ldaudit", "x")
'''

# (c) genuine: the roster labels are emitted by the running process
GENUINE = HEADER + '''

def main():
    run("base-old-counter", "x")
    run("round56-counter", "x")
    run("m-drop-ldaudit", "x")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
'''

VARIANTS = {"no-calls": NO_CALLS, "unreachable-calls": UNREACHABLE, "genuine": GENUINE}
