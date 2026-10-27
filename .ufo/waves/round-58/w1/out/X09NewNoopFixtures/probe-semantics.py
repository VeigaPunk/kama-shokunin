#!/usr/bin/env python3
"""X09NewNoopFixtures semantic probe: show each seat-authored variant really has lost the
verification the checker credits it with, independent of the checker's hermetic harness.
Imports the variant modules (definitions only; main() is never called, so nothing is
written into the lane) and exercises the two predicate functions against a genuinely
failing leg and a genuine substring counterexample. Receipts go to --out."""
import argparse
import importlib.util
import pathlib
import subprocess
import sys

LANE = pathlib.Path("/home/vgpnk/Projects/shokunin/kama-shokunin")
NEW = LANE / "tools/round56-replay-code-audit.py"


def load(path):
    spec = importlib.util.spec_from_file_location("m_" + pathlib.Path(path).stem.replace("-", "_"), path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--variants", required=True)
    ap.add_argument("--genuine", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--scratch", required=True)
    a = ap.parse_args()
    scratch = pathlib.Path(a.scratch)
    scratch.mkdir(parents=True, exist_ok=True)
    rows = []
    files = [("00-genuine", a.genuine)] + [(p.stem, p) for p in sorted(pathlib.Path(a.variants).glob("X*.py"))]
    for name, path in files:
        real_run = subprocess.run
        m = load(path)
        subprocess.run = real_run
        # a genuinely failing leg: the positive control does detect, expected says missed -> exit 1
        r_fail = m.run(name, NEW, "missed", scratch / f"{name}-fail.out")
        # the substring counterexample the exact-field predicate exists to reject
        r_cmp = m.exact_field_match({"ld_audit": "undetected"}, "ld_audit", "detected")
        # the kill leg pointed at the unmutated counter (what X14's main does)
        r_kill_unmutated = m.assert_mutant_breaks_detection(NEW, scratch / f"{name}-kill.out")
        rows.append((name, r_fail, r_cmp, r_kill_unmutated))
    lines = ["name run(failing_leg)->bool exact_field_match(undetected,detected)->bool "
             "assert_mutant_breaks_detection(unmutated_counter)->bool"]
    lines += [f"{n} {rf} {rc} {rk}" for n, rf, rc, rk in rows]
    text = "\n".join(lines) + "\n"
    pathlib.Path(a.out).write_text(text)
    print(text, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
