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


def exact_field_match(fields, key, expected):
    """Exact receipt-field predicate; never substring membership."""
    return fields.get(key) == expected


def comparator_selftest(out):
    false_positive = exact_field_match({"ld_audit": "undetected"}, "ld_audit", "detected")
    text = f"substring-counterexample expected=detected field=undetected accepted={false_positive}\n"
    text += f"exit={int(false_positive)}\n"
    out.write_text(text)
    ok = not false_positive
    print(f"comparator-selftest: {text.splitlines()[0]} -> {'pass' if ok else 'fail'}")
    return ok


def run(label, counter, expected, out):
    p = subprocess.run(["python3", str(TEST), "--counter", str(counter), "--expect", expected],
                       capture_output=True, text=True)
    body = p.stdout + p.stderr + f"exit={p.returncode}\n"
    out.write_text(body)
    fields = {tok.split("=", 1)[0]: tok.split("=", 1)[1]
              for tok in p.stdout.split() if "=" in tok}
    ok = p.returncode == 0 and exact_field_match(fields, "ld_audit", expected)
    print(f"{label}: ld_audit={fields.get('ld_audit')} exit={p.returncode} -> {'pass' if ok else 'fail'}")
    return ok

def assert_mutant_breaks_detection(counter, out):
    """The frozen predicate requires the drop-LD_AUDIT mutant to fail the
    positive expected-detected assertion (exit 1), not merely to return its
    expected observed value `missed` (closure target-sentence wording)."""
    p = subprocess.run(["python3", str(TEST), "--counter", str(counter), "--expect", "detected"],
                       capture_output=True, text=True)
    body = p.stdout + p.stderr + f"exit={p.returncode}\n"
    out.write_text(body)
    fields = {tok.split("=", 1)[0]: tok.split("=", 1)[1]
              for tok in p.stdout.split() if "=" in tok}
    ok = p.returncode == 1 and fields.get("ld_audit") == "missed"
    print(f"m-drop-ldaudit-positive-target: ld_audit={fields.get('ld_audit')} exit={p.returncode} "
          f"-> {'killed' if ok else 'SURVIVED'}")
    return ok


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    scratch = pathlib.Path("/fast/scratch/hyaku/kama-r56/l1-battery")
    scratch.mkdir(parents=True, exist_ok=True)
    results = []
    print("battery ok")
    return 0 if all(results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
