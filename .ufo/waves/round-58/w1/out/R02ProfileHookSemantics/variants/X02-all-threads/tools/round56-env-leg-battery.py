#!/usr/bin/env python3
"""LIMIT variant X02 (seat R02ProfileHookSemantics, round 58).

Every leg genuinely issues its subprocess invocation from inside a run() /
assert_mutant_breaks_detection() frame - but on a worker thread. sys.setprofile is
thread-local: the fresh threads carry no profile hook, so no watched call event ever
reaches the harness and the frames list comes back empty. The roster-to-execution
binding is blind to legs that run off the main thread.
"""
import pathlib
import subprocess
import threading

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


def run(label, counter, expected, out):
    p = subprocess.run(["python3", str(TEST), "--counter", str(counter), "--expect", expected],
                       capture_output=True, text=True)
    body = p.stdout + p.stderr + f"exit={p.returncode}\n"
    out.write_text(body)
    fields = {tok.split("=", 1)[0]: tok.split("=", 1)[1]
              for tok in p.stdout.split() if "=" in tok}
    return p.returncode == 0 and fields.get("ld_audit") == expected


def assert_mutant_breaks_detection(counter, out):
    p = subprocess.run(["python3", str(TEST), "--counter", str(counter), "--expect", "detected"],
                       capture_output=True, text=True)
    body = p.stdout + p.stderr + f"exit={p.returncode}\n"
    out.write_text(body)
    return p.returncode == 1


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    legs = [
        threading.Thread(target=run, args=("base-old-counter", OLD, "missed", OUT / "base-c1.out")),
        threading.Thread(target=run, args=("round56-counter", NEW, "detected", OUT / "build-c1.out")),
        threading.Thread(target=run, args=("m-drop-ldaudit", NEW, "missed", OUT / "m-drop-ldaudit.out")),
        threading.Thread(target=assert_mutant_breaks_detection, args=(NEW, OUT / "m-drop-ldaudit-target-fails.out")),
    ]
    for t in legs:
        t.start()
    for t in legs:
        t.join()


if __name__ == "__main__":
    main()
