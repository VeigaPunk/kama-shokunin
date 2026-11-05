#!/usr/bin/env python3
"""round86-mutant-owners.py - round-86 C2 (operability): map every declared mutant of
the delivered subject-binding selftest to explicit OWNING arms and reconcile one
completed selftest summary with failure-line cardinality.

Population: five named mutations of ``tools/round81-append-debt.py`` read as committed
bytes at ``--rev`` (never the worktree), each with one declared owning arm:

  M2  deletion != accepting            -> note-deletion-equals-subject
  M3  deletion != subject -> <         -> note-deletion-above-subject
  M4  drop the ``continue`` after the   -> note-subject-exact-summary
      note-wrong-deletion-round finding
  M5  drop one cases.append arm         -> arm-count
  M6  forge the summary (pass=0 fail=0) -> summary-cardinality

Reconciliation clauses (each a way a summary can lie):
  * exactly one ``APPEND_DEBT_SELFTEST`` summary line and, when the tool prints one,
    exactly one ``APPEND_DEBT_SELFTEST_ARMS`` line;
  * ``pass + fail == arms`` in the summary;
  * the ARMS line's ``arms`` equals its declared ``expected`` population;
  * the ARMS line's ``fail_lines`` equals the summary's ``fail``;
  * the ARMS line's ``fail_lines`` equals the number of ``APPEND_DEBT_SELFTEST_FAIL``
    lines actually printed;
  * empty stderr and no traceback.

A mutant is KILLED when it exits 1 with the declared owning arm named on a failure line,
or when its exit-0 output breaks a reconciliation clause (the owning arm is then
``summary-cardinality`` or ``arm-count``); ESCAPED when it exits 0 with a reconcilable
green summary; INVALID for a crash, a missing mutation site, two summaries, a foreign
owner or a non-reconcilable exit-1 run.

Output: one ``DEBT_MUTANT_OWNERS mutants=5 killed=<k> escaped=<e> invalid=<i>
arms=<n|unknown> cardinality=<ok|bad|unknown> owners=<k>/5`` line, then one
``DEBT_MUTANT_OWNER <mutant> owner=<label> verdict=<killed|escaped|invalid> <detail>``
line per mutant.

Exit: 0 every mutant killed and the pristine run reconciles; 1 any survivor, invalid
execution or pristine regression; 2 could-not-evaluate (mutation site missing, the
pristine selftest not runnable).

``--selftest`` exercises the classifier on synthetic outputs in $TMPDIR.
"""

from __future__ import annotations

import argparse
import os
import pathlib
import re
import subprocess
import sys
import tempfile

PREDICATE = (
    "`python3 tools/round86-mutant-owners.py --repo <lane> --rev <rev> --work <dir>` prints one "
    "`DEBT_MUTANT_OWNERS mutants=5 killed=5 escaped=0 invalid=0 arms=34 cardinality=ok owners=5/5` "
    "line and exits 0 only when all five declared mutants of the delivered debt selftest are "
    "killed on their declared owning arms, each completed summary reconciles with its arm "
    "population and its failure-line cardinality, and the pristine selftest is green."
)

SOURCE = "tools/round81-append-debt.py"
CONDITION = "subject_round is not None and deletion != subject_round"
CONTINUE_BLOCK = ('            bad("note-wrong-deletion-round", f"{detail}: note deletion round {deletion} "\n'
                  '                                             f"differs from subject round {subject_round}")\n'
                  "            continue")
ARM_LINE = '    cases.append(("note-deletion-equals-subject", r, 0, None))\n'
SUMMARY = 'print(f"APPEND_DEBT_SELFTEST pass={len(cases) - fail} fail={fail}"'
SUMMARY_PASS = "pass={len(cases) - fail}"
SUMMARY_FAIL = "fail={fail}"

MUTATIONS = (
    ("M2", "note-deletion-equals-subject",
     ((CONDITION, "subject_round is not None and deletion != accepting"),)),
    ("M3", "note-deletion-above-subject",
     ((CONDITION, "subject_round is not None and deletion < subject_round"),)),
    ("M4", "note-subject-exact-summary",
     ((CONTINUE_BLOCK, CONTINUE_BLOCK.rsplit("\n", 1)[0]),)),
    ("M5", "arm-count",
     ((ARM_LINE, ""),)),
    ("M6", "summary-cardinality",
     ((SUMMARY_PASS, "pass=0"), (SUMMARY_FAIL, "fail=0"))),
)

SUMMARY_RE = re.compile(r"^APPEND_DEBT_SELFTEST pass=([0-9]+) fail=([0-9]+)(?: arms=([0-9]+))?$", re.M)
ARMS_RE = re.compile(r"^APPEND_DEBT_SELFTEST_ARMS arms=([0-9]+) expected=([0-9]+) "
                     r"fail_lines=([0-9]+)$", re.M)
FAIL_RE = re.compile(r"^APPEND_DEBT_SELFTEST_FAIL (\S+) ", re.M)
# The arm population the frozen target line names (`arms=34`). Round-86 w1 critic: a subject copy
# with 33 arms and EXPECTED_ARMS=33 still exited 0, so the printed population is pinned here.
DECLARED_POPULATION = 34


class CouldNotEvaluate(Exception):
    pass


def classify(stdout: str, stderr: str, rc: int, owner: str):
    """Return (verdict, owning_label, detail) for one mutant run.

    Frozen clauses implemented literally (plans/round-86-claims.md C2): exactly one summary
    line and exactly one ARMS line (a summary with no declared population cannot reconcile,
    and two declarations are ambiguous); pass + fail == the declared arm population;
    ARMS arms == expected; ARMS fail_lines == summary fail == the printed FAIL lines; empty
    stderr; no traceback. Round-86 w2 `MT02CardinalityForgery` proved the earlier code skipped
    every clause that needed the ARMS line and ignored non-traceback stderr.
    """
    if "Traceback (most recent call last)" in stderr:
        return "invalid", owner, "traceback on stderr"
    if stderr.strip():
        return "invalid", owner, "non-empty stderr"
    summaries = SUMMARY_RE.findall(stdout)
    arms_lines = ARMS_RE.findall(stdout)
    fails = FAIL_RE.findall(stdout)
    if len(summaries) != 1:
        return "invalid", owner, f"{len(summaries)} summary lines"
    if len(arms_lines) > 1:
        return "invalid", owner, f"{len(arms_lines)} ARMS lines (at most one)"
    passed, failed, arms = (int(x) if x else None for x in summaries[0])
    problems = []
    if arms_lines:
        # The declared population is the ARMS line, and it is the clause's ground truth: the
        # summary's pass+fail must reconcile with it whether or not the summary repeats `arms`.
        declared, expected, fail_lines = (int(x) for x in arms_lines[0])
        if arms is not None and arms != declared:
            problems.append(f"summary arms={arms} != ARMS arms={declared}")
        if passed + failed != declared:
            problems.append(f"summary pass+fail={passed + failed} != arms={declared}")
        if declared != expected:
            problems.append(f"arms={declared} != expected={expected}")
        if fail_lines != failed:
            problems.append(f"ARMS fail_lines={fail_lines} != summary fail={failed}")
        if fail_lines != len(fails):
            problems.append(f"ARMS fail_lines={fail_lines} != {len(fails)} FAIL lines")
    if problems:
        label = "arm-count" if any("expected" in p for p in problems) else "summary-cardinality"
        return "killed", label, "; ".join(problems)
    if rc == 0:
        if failed:
            return "invalid", owner, f"exit 0 with fail={failed}"
        return "escaped", owner, "green summary"
    if rc == 1:
        if owner in fails:
            return "killed", owner, f"owning failure line present ({len(fails)} FAIL lines)"
        return "invalid", owner, f"exit 1 without the declared owning arm ({fails})"
    return "invalid", owner, f"exit {rc}"


def run_selftest(source: str, work: pathlib.Path, name: str):
    path = work / f"{name}.py"
    path.write_text(source, encoding="utf-8")
    return subprocess.run([sys.executable, str(path), "--selftest"], text=True,
                          capture_output=True, env={**os.environ, "TMPDIR": str(work)},
                          timeout=900)


def grade(repo: pathlib.Path, rev: str, work: pathlib.Path):
    if rev == "worktree":
        try:
            source = (repo / SOURCE).read_text(encoding="utf-8")
        except OSError as exc:
            raise CouldNotEvaluate(f"no worktree {SOURCE}: {exc}") from exc
    else:
        try:
            source = subprocess.check_output(
                ["git", "-C", str(repo), "show", f"{rev}:{SOURCE}"], text=True)
        except subprocess.CalledProcessError as exc:
            raise CouldNotEvaluate(f"no {SOURCE} at {rev}: {exc}") from exc
    work.mkdir(parents=True, exist_ok=True)
    pristine = run_selftest(source, work, "pristine")
    verdict, label, detail = classify(pristine.stdout, pristine.stderr, pristine.returncode,
                                      "pristine")
    arms = ARMS_RE.findall(pristine.stdout)
    arms_value = arms[0][0] if arms else "unknown"
    if verdict != "escaped" or pristine.returncode != 0:
        raise CouldNotEvaluate(f"pristine selftest not green: {detail}")
    results = []
    for name, owner, edits in MUTATIONS:
        mutated = source
        for old, new in edits:
            if mutated.count(old) != 1:
                raise CouldNotEvaluate(f"{name}: mutation site count {mutated.count(old)}")
            mutated = mutated.replace(old, new)
        run = run_selftest(mutated, work, name)
        verdict, label, detail = classify(run.stdout, run.stderr, run.returncode, owner)
        results.append((name, owner, verdict, label, detail))
    killed = sum(1 for r in results if r[2] == "killed")
    escaped = sum(1 for r in results if r[2] == "escaped")
    invalid = sum(1 for r in results if r[2] == "invalid")
    owners = sum(1 for r in results if r[2] == "killed" and r[3] == r[1])
    cardinality = "ok" if all(r[2] != "invalid" for r in results) else "bad"
    return {"results": results, "killed": killed, "escaped": escaped, "invalid": invalid,
            "owners": owners, "arms": arms_value, "cardinality": cardinality,
            "population": ("unknown" if arms_value == "unknown"
                           else "ok" if arms_value == str(DECLARED_POPULATION) else "bad"),
            "pristine": pristine.stdout.strip().splitlines()[-1]}


def render(result):
    return (f"DEBT_MUTANT_OWNERS mutants=5 killed={result['killed']} escaped={result['escaped']} "
            f"invalid={result['invalid']} arms={result['arms']} "
            f"cardinality={result['cardinality']} owners={result['owners']}/5")


# ---------------------------------------------------------------- selftest

GOOD_STDOUT = ("APPEND_DEBT_SELFTEST_ARMS arms=34 expected=34 fail_lines=0\n"
               "APPEND_DEBT_SELFTEST pass=34 fail=0 arms=34\n")
OWNED_FAIL = ("APPEND_DEBT_SELFTEST_FAIL note-deletion-equals-subject exit=1 want=0\n"
              "APPEND_DEBT_SELFTEST_ARMS arms=34 expected=34 fail_lines=1\n"
              "APPEND_DEBT_SELFTEST pass=33 fail=1 arms=34\n")


def selftest():
    arms = []

    def arm(name, stdout, stderr, rc, owner, want):
        got, label, detail = classify(stdout, stderr, rc, owner)
        arms.append((name, got == want, f"verdict={got} owner={label} {detail}"))

    arm("pristine-green", GOOD_STDOUT, "", 0, "pristine", "escaped")
    arm("owned-failure", OWNED_FAIL, "", 1, "note-deletion-equals-subject", "killed")
    arm("forged-summary", "APPEND_DEBT_SELFTEST_ARMS arms=34 expected=34 fail_lines=0\n"
        "APPEND_DEBT_SELFTEST pass=0 fail=0 arms=34\n", "", 0, "summary-cardinality", "killed")
    arm("dropped-arm", "APPEND_DEBT_SELFTEST_ARMS arms=33 expected=34 fail_lines=1\n"
        "APPEND_DEBT_SELFTEST_FAIL arm-count arms=33 want=34\n"
        "APPEND_DEBT_SELFTEST pass=33 fail=0 arms=33\n", "", 1, "arm-count", "killed")
    arm("fail-lines-disagree", "APPEND_DEBT_SELFTEST_ARMS arms=34 expected=34 fail_lines=2\n"
        "APPEND_DEBT_SELFTEST pass=33 fail=1 arms=34\n", "", 0, "summary-cardinality", "killed")
    arm("two-summaries", GOOD_STDOUT + "APPEND_DEBT_SELFTEST pass=34 fail=0 arms=34\n",
        "", 0, "summary-cardinality", "invalid")
    arm("foreign-owner", OWNED_FAIL.replace("note-deletion-equals-subject", "other-arm"),
        "", 1, "note-deletion-equals-subject", "invalid")
    arm("traceback", "", "Traceback (most recent call last):\n", 1,
        "note-deletion-equals-subject", "invalid")
    arm("exit-two", "", "", 2, "note-deletion-equals-subject", "invalid")
    arm("green-with-fail", "APPEND_DEBT_SELFTEST pass=33 fail=1 arms=34\n", "", 0,
        "note-deletion-equals-subject", "invalid")
    # w2 MT02CardinalityForgery escapes, now closed by the frozen clauses.
    arm("stderr-noise", GOOD_STDOUT, "warning: something\n", 0, "pristine", "invalid")
    arm("summary-without-arms-field",
        "APPEND_DEBT_SELFTEST_ARMS arms=34 expected=34 fail_lines=0\n"
        "APPEND_DEBT_SELFTEST pass=0 fail=0\n", "", 0, "summary-cardinality", "killed")
    # Disclosed limit, pinned as a control: a run that prints NO ARMS line has no declared
    # population to reconcile against, so it is not distinguishable from an honest green run.
    # The round-81 base tree is exactly this shape (the before receipt's pristine line), which is
    # why requiring one would make the do-nothing control unreproducible.
    arm("no-arms-line-disclosed-limit", "APPEND_DEBT_SELFTEST pass=34 fail=0\n", "", 0,
        "summary-cardinality", "escaped")
    fail = sum(1 for _, ok, _ in arms if not ok)
    for name, ok, detail in arms:
        print(f"DEBT_MUTANT_OWNERS_SELFTEST_{'PASS' if ok else 'FAIL'} {name} {detail}")
    print(f"DEBT_MUTANT_OWNERS_SELFTEST pass={len(arms) - fail} fail={fail}")
    return 0 if fail == 0 else 1


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", default=".")
    parser.add_argument("--rev", default="master")
    parser.add_argument("--work", required=False)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--selftest", action="store_true")
    args = parser.parse_args(argv)
    if args.selftest:
        return selftest()
    if not args.work:
        print("could-not-evaluate: --work is required (no hardcoded /tmp)", file=sys.stderr)
        return 2
    try:
        result = grade(pathlib.Path(args.repo).resolve(), args.rev, pathlib.Path(args.work))
    except (CouldNotEvaluate, OSError, subprocess.TimeoutExpired) as exc:
        print(f"could-not-evaluate: {exc}", file=sys.stderr)
        return 2
    if args.json:
        import json
        print(json.dumps(result, indent=2))
    else:
        print(render(result))
        for name, owner, verdict, label, detail in result["results"]:
            print(f"DEBT_MUTANT_OWNER {name} owner={label} verdict={verdict} {detail}")
        print(f"DEBT_MUTANT_OWNER_PRISTINE {result['pristine']}")
        if result["population"] == "bad":
            print(f"DEBT_MUTANT_OWNERS_FINDING population arms={result['arms']} "
                  f"!= declared={DECLARED_POPULATION}")
    return 0 if (result["killed"] == 5 and result["escaped"] == 0
                 and result["invalid"] == 0 and result["owners"] == 5
                 and result["cardinality"] == "ok"
                 and result["population"] != "bad") else 1


if __name__ == "__main__":
    sys.exit(main())
