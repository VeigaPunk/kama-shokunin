#!/usr/bin/env python3
"""M01DropAudit mutant probe: one-line deletion of LD_AUDIT from BAD_ENV.
Creates the mutant from the pristine scratch copy, records hashes, reruns the
env-leg detector and the battery's run() assertion, all inside this scratch."""
import hashlib
import pathlib
import subprocess
import sys

HERE = pathlib.Path(__file__).resolve().parent
PRISTINE = HERE / "pristine-counter.py"
MUTANT = HERE / "mutant-counter.py"
TEST = HERE / "round56-env-leg-test.py"
BATTERY = HERE / "round56-env-leg-battery.py"
RECEIPTS = HERE / "receipts"

OLD = 'BAD_ENV = ("LD_PRELOAD", "DYLD_INSERT_LIBRARIES", "LD_AUDIT")'
NEW = 'BAD_ENV = ("LD_PRELOAD", "DYLD_INSERT_LIBRARIES")'


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def env_leg(counter, expect):
    p = subprocess.run([sys.executable, str(TEST), "--counter", str(counter),
                        "--expect", expect], capture_output=True, text=True,
                       env={"PATH": "/usr/bin:/bin", "TMPDIR": str(HERE / "tmp")})
    return p


print("== mutant creation (one-line deletion from BAD_ENV)")
src = PRISTINE.read_text()
n = src.count(OLD)
print(f"anchor occurrences in pristine counter: {n}")
assert n == 1, "mutant anchor is not unique"
MUTANT.write_text(src.replace(OLD, NEW))
print(f"before sha256 {PRISTINE.name}: {sha(PRISTINE)}")
print(f"after  sha256 {MUTANT.name}:  {sha(MUTANT)}")
before_line = [l for l in src.splitlines() if "BAD_ENV =" in l][0]
after_line = [l for l in MUTANT.read_text().splitlines() if "BAD_ENV =" in l][0]
print(f"before line: {before_line}")
print(f"after  line: {after_line}")
changed = sum(1 for a, b in zip(src.splitlines(), MUTANT.read_text().splitlines()) if a != b)
print(f"changed lines: {changed}")

print("== leg A: mutant env_leg must MISS (expected-detected assertion must fail)")
p = env_leg(MUTANT, "detected")
print(p.stdout.strip())
if p.stderr.strip():
    print("stderr:", p.stderr.strip())
print(f"exit={p.returncode}  -> expected-detected assertion "
      f"{'HELD (unexpected, mutant SURVIVES)' if p.returncode == 0 else 'FAILS as required (mutant misses)'}")
(RECEIPTS / "mutant-expected-detected.out").write_text(p.stdout + p.stderr + f"exit={p.returncode}\n")
legA = p.returncode == 1

print("== leg B: mutant against battery kill roster expectation 'missed'")
p = env_leg(MUTANT, "missed")
print(p.stdout.strip())
if p.stderr.strip():
    print("stderr:", p.stderr.strip())
print(f"exit={p.returncode}  -> matches kill roster 'missed': {'yes' if p.returncode == 0 else 'NO'}")
(RECEIPTS / "mutant-expected-missed.out").write_text(p.stdout + p.stderr + f"exit={p.returncode}\n")
legB = p.returncode == 0

print("== leg C: battery run() assertions on pristine vs mutant")
import importlib.util
spec = importlib.util.spec_from_file_location("battery", BATTERY)
b = importlib.util.module_from_spec(spec)
spec.loader.exec_module(b)
r_pos = b.run("round56-counter", PRISTINE, "detected", RECEIPTS / "battery-positive-control.out")
r_kill = b.run("m-drop-ldaudit", MUTANT, "missed", RECEIPTS / "battery-kill-leg.out")
r_wrong = b.run("m-drop-ldaudit-if-graded-detected", MUTANT, "detected",
                RECEIPTS / "battery-kill-graded-detected.out")
print(f"frozen-roster battery green (positive-control + kill): {all([r_pos, r_kill])}")
print(f"expected-detected assertion on mutant: {'pass' if r_wrong else 'fail'}")

verdict = "KILLED" if (legA and legB and r_pos and r_kill and not r_wrong) else "SURVIVED/INCONCLUSIVE"
print(f"== verdict: {verdict}")
sys.exit(0 if verdict == "KILLED" else 1)
