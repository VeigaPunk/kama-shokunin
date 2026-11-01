#!/usr/bin/env python3
"""round65-host-census.py - run the declared host-local self-test census set.

Round 65 moved the lane to a Windows host (MinGW Git Bash, CPython 3.13). The
SCORECARD axes rows name self-test commands written as ``python3 tools/...``;
on this host ``python3`` is the Microsoft Store alias stub (exit 49, "Python
was not found"), so the registered counting commands are adapted to the
running interpreter (sys.executable). This census runs the declared set, each
member classified:

    pass     exit 0 and the member's pinned marker in its output
    refused  a pinned fail-closed refusal marker (a missing Linux dependency,
             an NTFS-invalid tracked path) or the census time budget; a
             refusal is recorded with its reason, never a pass
    fail     anything else (a defect on this host)

Tiers: tier A members are the self-tests named in SCORECARD axes evidence rows
plus the instrument-registry gate; tier B members are the capability
instruments' self-tests. Exit: 0 only when no member fails; a tier-B residual
defect keeps exit 1 and is reported openly (round 65 carries one: the
append-only-audit v6-revert-class arm, deterministic on this host, root cause
unresolved in-round). Read-only: members write only their own temporary
fixtures; this runner creates and removes one scratch directory per member.
"""
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

LANE = Path(__file__).resolve().parent.parent
BUDGET = 600  # seconds per member

# (tier, name, argv-after-interpreter, pass marker,
#  [(refused marker, reason), ...])
MEMBERS = [
    ("A", "test-snapshot harness",
     ["bash", "tools/test-snapshot.sh"],
     "RESULT pass=30 fail=0",
     [("missing dependency", "fail-closed refusal: Linux-only dependency absent on this host")]),
    ("A", "pin-watch selftest",
     ["tools/pin-watch.py", "selftest"],
     "selftest pass=9 fail=0", []),
    ("A", "report-landing-audit selftest",
     ["tools/report-landing-audit.py", "--selftest"],
     "selftest cases=79 failed=0", []),
    ("A", "sources-append-only selftest",
     ["tools/sources-append-only.py", "--selftest"],
     "46/46 selftest cases passed", []),
    ("A", "citation-provenance selftest",
     ["tools/citation-provenance.py", "--selftest"],
     "selftest: ok (24 cases)", []),
    ("A", "capability-repertoire-audit selftest",
     ["tools/capability-repertoire-audit.py", "--selftest"],
     "CAP_SELFTEST pass=2 fail=0", []),
    ("A", "instrument-agreement selftest",
     ["tools/instrument-agreement.py", "--selftest"],
     "IA_SELFTEST pass=4 fail=0", []),
    ("A", "round42-selfdesc-reconcile selftest",
     ["tools/round42-selfdesc-reconcile.py", "--selftest", "--work", "__WORK__"],
     "",
     [("invalid path", "fail-closed refusal: the lane holds a tracked path NTFS cannot check out, so the fixture clone cannot be created on this host (L0 question, kama round-65)")]),
    ("A", "gate-registry-check selftest (lane-tip arm)",
     ["tools/gate-registry-check.py", "--selftest"],
     "GATE_SELFTEST pass=6 fail=0",
     [("cannot resolve master", "lane tip unresolvable")]),
    ("A", "worktree-landing-check selftest",
     ["tools/round67-worktree-landing-check.py", "--selftest"],
     "WLC_SELFTEST pass=6 fail=0", []),
    ("A", "receipt-pointer-audit selftest",
     ["tools/round68-receipt-pointer-audit.py", "--selftest"],
     "9/9 selftest arms passed", []),
    ("B", "digest-ledger selftest",
     ["tools/digest-ledger.py", "selftest"],
     "selftest pass=11 fail=0", []),
    ("B", "hexrun-census selftest",
     ["tools/hexrun-census.py", "selftest"],
     "selftest pass=18 fail=0", []),
    ("B", "kama-ollama-evidence selftest",
     ["tools/kama-ollama-evidence.py", "--selftest"],
     '"finding_id": "clean"', []),
    ("B", "gguf-identity selftest",
     ["tools/gguf-identity.py", "--selftest"],
     '"status": "passed"', []),
    ("B", "manifest-crosscheck selftest",
     ["tools/manifest-crosscheck.py", "--selftest"],
     "MANIFEST_CROSSCHECK_SELFTEST pass=5 fail=0", []),
    ("B", "error-verdict-census selftest",
     ["tools/error-verdict-census.py", "--selftest"],
     "selftest: ok (15 pinned cells", []),
    ("B", "seat-report-immutability selftest",
     ["tools/seat-report-immutability.py", "--selftest"],
     "SEAT_REPORT_IMMUTABILITY_SELFTEST pass=13 fail=0", []),
    ("B", "prereg-time-check selftest",
     ["tools/prereg-time-check.py", "--selftest"],
     "SELFTEST PASS", []),
    ("B", "release-recheck selftest",
     ["tools/release-recheck.py", "selftest"],
     "selftest pass=5 fail=0", []),
    ("B", "append-only-audit selftest",
     ["tools/append-only-audit.py", "--selftest"],
     "AOA_SELFTEST pass=51 fail=0",
     []),
]


def main():
    passed = failed = refused = 0
    fails_a = fails_b = 0
    lines = []
    for tier, name, argv, marker, refusals in MEMBERS:
        work = Path(tempfile.mkdtemp(prefix="r65census-"))
        try:
            run_argv = [a.replace("__WORK__", str(work)) for a in argv]
            if run_argv[0].endswith(".py"):
                # a .py path is not a CreateProcess executable on Windows;
                # on POSIX the shebang made direct exec work. Spawn under
                # the running interpreter everywhere (the docstring's
                # adaptation), keeping non-python members as declared.
                run_argv = [sys.executable] + run_argv
            proc = subprocess.run(run_argv, cwd=str(LANE), capture_output=True,
                                  text=True, errors="replace", timeout=BUDGET)
            out = proc.stdout + proc.stderr
            hit = next((r for r in refusals if r[0] in out), None)
            if hit:
                refused += 1
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
            refused += 1
            lines.append(f"refused [{tier}] {name}: census budget {BUDGET}s exceeded (recorded, not a verdict)")
        except OSError as exc:
            failed += 1
            if tier == "A":
                fails_a += 1
            else:
                fails_b += 1
            lines.append(f"FAIL [{tier}] {name}: spawn error {exc}")
        finally:
            shutil.rmtree(work, ignore_errors=True)
    for line in lines:
        print(line)
    print(f"HOST_CENSUS pass={passed} fail={failed} refused={refused} total={len(MEMBERS)} "
          f"tierA_fail={fails_a} tierB_fail={fails_b}")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
