#!/usr/bin/env python3
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
            hit = None  # refusal support deleted
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
