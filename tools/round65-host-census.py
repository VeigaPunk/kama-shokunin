#!/usr/bin/env python3
"""round65-host-census.py - run the declared host-local self-test census set.

Round 65 moved the lane to a Windows host (MinGW Git Bash, CPython 3.13). The
SCORECARD axes rows name self-test commands written as ``python3 tools/...``;
on this host ``python3`` is the Microsoft Store alias stub (exit 49, "Python
was not found"), so the registered counting commands are adapted to the
running interpreter (sys.executable). This census runs the declared set, each
member classified:

    pass           exit 0 and the member's pinned marker in its output
    refused        the census could not obtain a verdict from the member: a
                   pinned fail-closed refusal marker (a missing Linux
                   dependency, an NTFS-invalid tracked path), the census time
                   budget, or a member that could not be spawned at all; a
                   refusal is recorded with its reason, never a pass
    fail           the member ran and rejected (a defect on this host)

Round 70 verdict accounting: refused members are counted in
``not_evaluated`` and a member that did not run is never a pass. Exit is 0
only when ``fail=0`` AND every not-evaluated member is named by an explicit
``--waive <member-name>`` (repeatable, exact member name). A waived member
keeps its reason on its own line and the verdict keeps ``waived=<w>``
visible; a not-evaluated member with no waiver makes exit 1. A member that
ran keeps its real semantics: a pass stays a pass, a fail stays a fail, and
a waiver never covers a fail. Verdict line:

    HOST_CENSUS pass=<p> fail=<f> not_evaluated=<n> waived=<w> total=<t> tierA_fail=<a> tierB_fail=<b>

Tiers: tier A members are the self-tests named in SCORECARD axes evidence rows
plus the instrument-registry gate; tier B members are the capability
instruments' self-tests. tierA_fail / tierB_fail count only members that ran
and failed. Read-only: members write only their own temporary fixtures; this
runner creates and removes one scratch directory per member.
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
     "GATE_SELFTEST pass=7 fail=0",
     [("cannot resolve master", "lane tip unresolvable")]),
    ("A", "worktree-landing-check selftest",
     ["tools/round67-worktree-landing-check.py", "--selftest"],
     "WLC_SELFTEST pass=6 fail=0", []),
    ("A", "receipt-pointer-audit selftest",
     ["tools/round68-receipt-pointer-audit.py", "--selftest"],
     "9/9 selftest arms passed", []),
    ("A", "newest-closure-counter selftest",
     ["tools/round69-newest-closure-counter.py", "--selftest"],
     "10/10 selftest arms passed", []),
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
    # --waive <member-name> (repeatable, exact member name): accepts a member
    # that did not run on this pass. Only not-evaluated members consume a
    # waiver; a waiver never covers a pass/fail verdict.
    cli = sys.argv[1:]
    waive = []
    i = 0
    while i < len(cli):
        if cli[i] == "--waive" and i + 1 < len(cli):
            waive.append(cli[i + 1])
            i += 2
        elif cli[i].startswith("--waive="):
            waive.append(cli[i][len("--waive="):])
            i += 1
        else:
            i += 1
    waive_set = set(waive)

    passed = failed = not_evaluated = waived = 0
    fails_a = fails_b = 0
    evaluated = {}  # member name -> "pass" | "fail" (members that ran)
    unwaived_ne = []  # not-evaluated members without a waiver
    lines = []

    def record_ne(member_name):
        # The member did not run, so there is no verdict about it: counted in
        # not_evaluated, waived only by an explicit --waive of its exact name.
        nonlocal not_evaluated, waived
        not_evaluated += 1
        if member_name in waive_set:
            waived += 1
            return " [waived]"
        unwaived_ne.append(member_name)
        return ""

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
                suffix = record_ne(name)
                lines.append(f"refused [{tier}] {name}: {hit[1]} (marker {hit[0]!r}){suffix}")
            elif proc.returncode == 0 and (not marker or marker in out):
                passed += 1
                evaluated[name] = "pass"
                lines.append(f"pass [{tier}] {name}")
            else:
                failed += 1
                evaluated[name] = "fail"
                if tier == "A":
                    fails_a += 1
                else:
                    fails_b += 1
                tail = " | ".join(out.strip().splitlines()[-1:]) if out.strip() else ""
                lines.append(f"FAIL [{tier}] {name}: exit={proc.returncode} tail={tail!r}")
        except subprocess.TimeoutExpired:
            suffix = record_ne(name)
            lines.append(f"refused [{tier}] {name}: census budget {BUDGET}s exceeded (recorded, not a verdict){suffix}")
        except OSError as exc:
            # Round 70: the member never ran, so this is not a verdict about
            # the member; it is a not-evaluated member, never a silent pass.
            suffix = record_ne(name)
            lines.append(f"refused [{tier}] {name}: spawn error {exc}{suffix}")
        finally:
            shutil.rmtree(work, ignore_errors=True)
    member_names = {name for _, name, _, _, _ in MEMBERS}
    for w in waive:
        if w not in member_names:
            print(f"warning: --waive {w!r} is not a census member name", file=sys.stderr)
        elif w in evaluated:
            print(f"warning: --waive {w!r} unused: member was evaluated "
                  f"({evaluated[w]}); a waiver covers only not-evaluated members",
                  file=sys.stderr)
    for line in lines:
        print(line)
    print(f"HOST_CENSUS pass={passed} fail={failed} not_evaluated={not_evaluated} "
          f"waived={waived} total={len(MEMBERS)} tierA_fail={fails_a} tierB_fail={fails_b}")
    if unwaived_ne:
        print(f"HOST_CENSUS exit 1: {len(unwaived_ne)} not-evaluated member(s) "
              f"without a waiver: {', '.join(unwaived_ne)}")
    # Round 70: the exit is derived from the not-evaluated count. Exit 0 needs
    # fail=0 AND every not-evaluated member explicitly waived.
    return 0 if (failed == 0 and not unwaived_ne) else 1


if __name__ == "__main__":
    sys.exit(main())
