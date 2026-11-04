#!/usr/bin/env python3
"""counterexamples.py -- the five census designs that PASS the round-70 C2 frozen counter
and are not compliant with C2's frozen predicate.

The frozen counter (`refused-member-control.py`) asserts one fact: the refusal fixture
exits nonzero and the all-pass fixture exits 0. Each shim below keeps that pair while
breaking a fact the freeze names, so the pair cannot be the evidence for C2.

Usage:
    python3 counterexamples.py [--base PATH] [--control PATH] [--dir DIR]

  --base     frozen base census bytes (default: the lane's round-70 measured/before copy)
  --control  the frozen counter (default: sibling refused-member-control.py, else the lane path)
  --dir      where to write the shims (default: a fresh temp dir, removed at exit)

Every shim is the base file with one asserted textual replacement (or, for the waiver and
re-entrancy shims, with a known-good C2 census as parent so the frozen pair (1,0) is
already achieved). Read-only on the lane; writes only --dir.
"""
import argparse
import pathlib
import shutil
import subprocess
import sys
import tempfile

LANE = pathlib.Path("/home/vgpnk/Projects/shokunin/kama-shokunin")
DEFAULT_BASE = LANE / ".ufo/waves/round-70/measured/before/round65-host-census-base.py"
DEFAULT_CONTROL = LANE / ".ufo/waves/round-70/controls/refused-member-control.py"

VERDICT = ('    print(f"HOST_CENSUS pass={passed} fail={failed} refused={refused} total={len(MEMBERS)} "\n'
           '          f"tierA_fail={fails_a} tierB_fail={fails_b}")\n'
           '    return 0 if failed == 0 else 1\n')
REFUSAL = ('            if hit:\n'
           '                refused += 1\n'
           '                lines.append(f"refused [{tier}] {name}: {hit[1]} (marker {hit[0]!r})")\n')
MAIN = 'def main():\n    passed = failed = refused = 0\n'

# A good C2 census (exits 1 on the refusal fixture, 0 on all-pass) used as the parent of
# the shims whose hole is orthogonal to the refusal accounting. It is the round-70 C2
# landing's semantics without the frozen-format details.
GOOD = '''#!/usr/bin/env python3
"""Minimal C2-compliant census used as the parent of the orthogonal-hole shims."""
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

LANE = Path(__file__).resolve().parent.parent
BUDGET = 600
MEMBERS = []


def main(waive=()):
    names = {m[1] for m in MEMBERS}
    waived = set(waive)
    if waived - names:
        print(f"CENSUS_USAGE unknown waiver name(s): {sorted(waived - names)}")
        return 2
    passed = failed = not_evaluated = waived_n = 0
    fails_a = fails_b = 0
    lines = []
    for tier, name, argv, marker, refusals in MEMBERS:
        work = Path(tempfile.mkdtemp(prefix="r65census-"))
        try:
            run_argv = [a.replace("__WORK__", str(work)) for a in argv]
            if run_argv[0].endswith(".py"):
                run_argv = [sys.executable] + run_argv
            proc = subprocess.run(run_argv, cwd=str(LANE), capture_output=True,
                                  text=True, errors="replace", timeout=BUDGET)
            out = proc.stdout + proc.stderr
            hit = next((r for r in refusals if r[0] in out), None)
            if hit:
                not_evaluated += 1
                if name in waived:
                    waived_n += 1
                    lines.append(f"waived [{tier}] {name}: {hit[1]} (marker {hit[0]!r})")
                else:
                    lines.append(f"refused [{tier}] {name}: {hit[1]} (marker {hit[0]!r})")
            elif proc.returncode == 0 and (not marker or marker in out):
                passed += 1
                lines.append(f"pass [{tier}] {name}")
            else:
                failed += 1
                if tier == "A":
                    fails_a += 1
                else:
                    fails_b += 1
                tail = " | ".join(out.strip().splitlines()[-1:]) if out.strip() else ""
                lines.append(f"FAIL [{tier}] {name}: exit={proc.returncode} tail={tail!r}")
        except subprocess.TimeoutExpired:
            not_evaluated += 1
            lines.append(f"refused [{tier}] {name}: census budget {BUDGET}s exceeded")
        except OSError as exc:
            failed += 1
            fails_a += tier == "A"
            lines.append(f"FAIL [{tier}] {name}: spawn error {exc}")
        finally:
            shutil.rmtree(work, ignore_errors=True)
    for line in lines:
        print(line)
    tail = f" waived={waived_n}" if waived_n else ""
    print(f"HOST_CENSUS pass={passed} fail={failed} not_evaluated={not_evaluated} "
          f"total={len(MEMBERS)} tierA_fail={fails_a} tierB_fail={fails_b}{tail}")
    return 0 if (failed == 0 and not_evaluated - waived_n == 0) else 1
'''


def emit(directory, name, text):
    path = directory / f"{name}.py"
    path.write_text(text)
    return path


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", default=str(DEFAULT_BASE))
    ap.add_argument("--control", default=str(DEFAULT_CONTROL))
    ap.add_argument("--dir", default=None)
    a = ap.parse_args()
    base = pathlib.Path(a.base).read_text()
    d = pathlib.Path(a.dir) if a.dir else pathlib.Path(tempfile.mkdtemp(prefix="c2-ce-"))
    made = []

    # --- base-derived: the three polarities the counter is supposed to reject -----------
    made.append(emit(d, "s1-always-fail", base.replace(
        '    return 0 if failed == 0 else 1\n', '    return 1\n')))
    made.append(emit(d, "s2-refusal-as-pass", base))
    made.append(emit(d, "s3-cosmetic-not-evaluated", base.replace(
        REFUSAL, REFUSAL.replace('refused += 1', 'refused += 1')).replace(
        'HOST_CENSUS pass={passed} fail={failed} refused={refused} total={len(MEMBERS)}',
        'HOST_CENSUS pass={passed} fail={failed} not_evaluated={refused} total={len(MEMBERS)}')))
    made.append(emit(d, "s4-refusal-as-fail", base.replace(REFUSAL,
        '            if hit:\n'
        '                failed += 1\n'
        '                fails_a += tier == "A"\n'
        '                lines.append(f"FAIL [{tier}] {name}: refused ({hit[1]})")\n')))
    made.append(emit(d, "s7-argparse-in-main", base.replace('import shutil\n', 'import argparse\nimport shutil\n').replace(
        MAIN, 'def main():\n    ap = argparse.ArgumentParser()\n'
              '    ap.add_argument("--waive", action="append", default=[])\n'
              '    ap.parse_args()\n    passed = failed = refused = 0\n')))

    # --- good-parent: holes orthogonal to the refusal accounting ------------------------
    good = GOOD
    made.append(emit(d, "s5t-hardcoded-total", good.replace(
        'f"total={len(MEMBERS)}', 'f"total=22')))
    made.append(emit(d, "s6w-waiver-swallows-failure", good.replace(
        '    waived = set(waive)\n',
        '    waived = set(waive) | {n for n in __import__("os").environ.get("CENSUS_WAIVE", "").split(",") if n}\n'
    ).replace(
        '            else:\n                failed += 1\n',
        '            elif name in waived:\n'
        '                passed += 1\n'
        '                lines.append(f"pass [{tier}] {name} (waived)")\n'
        '            else:\n                failed += 1\n')))
    made.append(emit(d, "s8r-second-call-silent", good.replace(
        'def main(waive=()):\n',
        '_RAN = False\n\n\ndef main(waive=()):\n'
        '    global _RAN\n    if _RAN:\n        return 0\n    _RAN = True\n')))
    made.append(emit(d, "s10d-refusal-branch-deleted", good.replace(
        '            hit = next((r for r in refusals if r[0] in out), None)\n',
        '            hit = None  # refusal support deleted\n')))

    order = ["s1-always-fail", "s2-refusal-as-pass", "s3-cosmetic-not-evaluated",
             "s4-refusal-as-fail", "s5t-hardcoded-total", "s6w-waiver-swallows-failure",
             "s7-argparse-in-main", "s8r-second-call-silent", "s10d-refusal-branch-deleted"]
    print(f"shims in {d}")
    print(f"{'shim':34} {'frozen control':52} exit  verdict")
    for name in order:
        p = subprocess.run([sys.executable, a.control, str(d / f"{name}.py")],
                           capture_output=True, text=True)
        line = next((l for l in p.stdout.splitlines()
                     if l.startswith("REFUSED_MEMBER_CONTROL ")), "<no line>")
        print(f"{name:34} {line:52} {p.returncode:4}  {'PASS (hole)' if p.returncode == 0 else 'FAIL (rejected)'}")
    if not a.dir:
        shutil.rmtree(d, ignore_errors=True)


if __name__ == "__main__":
    main()
