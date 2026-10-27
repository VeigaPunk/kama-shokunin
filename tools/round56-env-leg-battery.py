#!/usr/bin/env python3
"""Round-56 C1 battery: exact field/value assertions and exit receipts for LD_AUDIT.
Uses committed round-54 code as the red baseline, the round-56 counter as positive
control, and a one-change mutant that removes LD_AUDIT from BAD_ENV."""
import os
import pathlib
import subprocess
import tempfile

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
    expected_result = f"ld_audit={expected}"
    fields = {tok.split("=", 1)[0]: tok.split("=", 1)[1]
              for tok in p.stdout.split() if "=" in tok}
    ok = p.returncode == 0 and fields.get("ld_audit") == expected
    print(f"{label}: ld_audit={fields.get('ld_audit')} exit={p.returncode} -> {'pass' if ok else 'fail'}")
    return ok


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    scratch = pathlib.Path("/fast/scratch/hyaku/kama-r56/l1-battery")
    scratch.mkdir(parents=True, exist_ok=True)
    results = []
    results.append(run("base-old-counter", OLD, "missed", OUT / "base-c1.out"))
    results.append(run("round56-counter", NEW, "detected", OUT / "build-c1.out"))
    with tempfile.TemporaryDirectory(prefix="mutant-", dir=scratch) as d:
        mutant = pathlib.Path(d) / "counter.py"
        src = NEW.read_text()
        old = 'BAD_ENV = ("LD_PRELOAD", "DYLD_INSERT_LIBRARIES", "LD_AUDIT")'
        new = 'BAD_ENV = ("LD_PRELOAD", "DYLD_INSERT_LIBRARIES")'
        if src.count(old) != 1:
            raise SystemExit("mutant anchor is not unique")
        mutant.write_text(src.replace(old, new))
        results.append(run("m-drop-ldaudit", mutant, "missed", OUT / "m-drop-ldaudit.out"))
    return 0 if all(results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
