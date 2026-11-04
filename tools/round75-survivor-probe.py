#!/usr/bin/env python3
"""Round-75 C2: certify the committed receipt-binding selftest's five kill arms.

Only a shared clone and copies under --work are changed. --keep retains that work
for inspection. --json adds structured per-mutant evidence after the text receipt.
The selftest rejects a count-only cheat whose mutation catalogue is empty.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile

PREDICATE = "`python3 tools/round75-survivor-probe.py --repo <lane>` prints one `SURVIVORS2 mutants=5 killed=5 escaped=0` line and exits 0 only when it applies five named source mutations to a copy of the committed `tools/round74-receipt-claim-binding.py` in its own scratch, runs the pristine module's selftest green and every mutated copy's selftest red, and names for each mutant the selftest arm that fails — `case-hex` (the `tip=`/`rev=` header parse loses `re.I`), `kind-boundary` (a same-line tip claim no longer inherits `stale-claim`), `paragraph-scope` (per-line instead of per-paragraph claim grading), `conflict-off` (the conflicting-header check in `_header_rev_v2` is removed) and `header-window` (`HEADER_WINDOW` narrowed from 5 to 3) — it exits 1 naming `SURVIVORS2_FINDING <mutant>` with the mutant's selftest exit and the arm that stayed green, and 2 on could-not-evaluate (the module absent, a clone failure, CLI misuse)."

TARGET = "tools/round74-receipt-claim-binding.py"
DEFAULT_WORK = "/fast/scratch/hyaku/kama-r75/EX02Survivors"
TIMEOUT = 300
# Exact old/new source patches from controls/mutation-control.py C2_MUTANTS.
MUTANTS = {
    "case-hex": (
        'HEADER_RE_V2 = re.compile(r"(?:^|[^\\w-])(?:#\\s*)?(?:tip|rev)=([0-9a-fA-F]{40})(?![0-9a-fA-F])", re.I)',
        'HEADER_RE_V2 = re.compile(r"(?:^|[^\\w-])(?:#\\s*)?(?:tip|rev)=([0-9a-f]{40})(?![0-9a-f])")',
    ),
    "kind-boundary": (
        '                    if kind == "same-line":\n                        kind = "stale-claim"\n',
        '                    pass\n',
    ),
    "paragraph-scope": (
        '        for start, plines in _paragraphs(lines):',
        '        for start, plines in [(i + 1, [l]) for i, l in enumerate(lines)]:',
    ),
    "conflict-off": ('    if len(set(revs)) > 1:', '    if False:'),
    "header-window": ('HEADER_WINDOW = 5', 'HEADER_WINDOW = 3'),
}
EXPECTED_ARMS = {
    "case-hex": "blob-reader-seam",
    "kind-boundary": "same-line-stale-claim",
    "paragraph-scope": "committed-fixtures",
    "conflict-off": "conflicting-headers",
    "header-window": "header-window-fifth-line",
}
REQUIRED_ARMS = {
    "predicate", "predicate-at-tip", "committed-fixtures", "blob-reader-seam",
    "stale-revision", "same-line-stale-claim", "base-absent", "record-missing",
    "cli-misuse",
}


class CouldNotEvaluate(Exception):
    pass


def run(command, cwd, env):
    return subprocess.run(command, cwd=cwd, env=env, capture_output=True,
                          text=True, timeout=TIMEOUT)


def decode_selftest(proc):
    arms = re.findall(r"^RECEIPT_CLAIM_V2_ARM (\S+) (ok|FAIL)(?: |$)",
                      proc.stdout, re.M)
    summaries = re.findall(r"^RECEIPT_CLAIM_V2_SELFTEST pass=(\d+) fail=(\d+)$",
                           proc.stdout, re.M)
    names = [name for name, _ in arms]
    if (len(summaries) != 1 or len(set(names)) != len(names)
            or not REQUIRED_ARMS.issubset(names)):
        raise CouldNotEvaluate("incomplete module selftest receipt: " + proc.stderr.strip())
    passed, failed = map(int, summaries[0])
    failed_arms = [name for name, status in arms if status == "FAIL"]
    if (failed != len(failed_arms) or passed + failed != len(arms)
            or proc.returncode != (1 if failed else 0)):
        raise CouldNotEvaluate("inconsistent module selftest exit/counts")
    return failed_arms


def grade(pristine_exit, rows, catalogue):
    # Do not trust a printed total: require exactly the five executed mutations.
    names = [row["mutant"] for row in rows]
    complete = (set(catalogue) == set(EXPECTED_ARMS)
                and len(names) == 5 and set(names) == set(EXPECTED_ARMS))
    killed = sum(row["mutant_exit"] == 1
                 and EXPECTED_ARMS.get(row["mutant"]) in row["failed_arms"]
                 for row in rows)
    return {"mutants": len(rows), "killed": killed,
            "escaped": len(rows) - killed,
            "exit": 0 if complete and pristine_exit == 0 and killed == 5 else 1,
            "complete": complete, "pristine_exit": pristine_exit, "results": rows}


def probe(repo, work, keep):
    work.mkdir(parents=True, exist_ok=True)
    scratch = Path(tempfile.mkdtemp(prefix="survivors2-", dir=work))
    env = dict(os.environ, TMPDIR=str(scratch), PYTHONDONTWRITEBYTECODE="1")
    try:
        clone = scratch / "clone"
        proc = run(["git", "clone", "--shared", str(repo), str(clone)], scratch, env)
        if proc.returncode:
            raise CouldNotEvaluate("clone failed: " + proc.stderr.strip())
        target = clone / TARGET
        if not target.is_file():
            raise CouldNotEvaluate("committed module absent: " + TARGET)
        original = target.read_text(encoding="utf-8")
        runs = scratch / "runs"
        runs.mkdir()
        def selftest(path, name):
            case_work = runs / name
            case_work.mkdir()
            result = run([sys.executable, str(path), "--selftest", "--work", str(case_work)],
                         clone, env)
            return result, decode_selftest(result)
        pristine, pristine_failures = selftest(target, "pristine")
        rows = []
        for name, (old, new) in MUTANTS.items():
            if original.count(old) != 1:
                raise CouldNotEvaluate("mutation anchor not unique: " + name)
            copy = target.with_name("round75-mutant-" + name + ".py")
            copy.write_text(original.replace(old, new, 1), encoding="utf-8")
            result, failures = selftest(copy, name)
            rows.append({"mutant": name, "mutant_exit": result.returncode,
                         "arm": EXPECTED_ARMS.get(name, "none") if failures else "none",
                         "failed_arms": failures, "stdout": result.stdout,
                         "stderr": result.stderr})
        doc = grade(pristine.returncode, rows, MUTANTS)
        doc.update(pristine_stdout=pristine.stdout, pristine_stderr=pristine.stderr,
                   pristine_failed_arms=pristine_failures)
        if keep:
            doc["work"] = str(scratch)
        return doc
    finally:
        if not keep:
            shutil.rmtree(scratch)


def selftest():
    rows = [{"mutant": name, "mutant_exit": 1, "failed_arms": [arm]}
            for name, arm in EXPECTED_ARMS.items()]
    checks = {
        "complete-kills": grade(0, rows, MUTANTS)["exit"] == 0,
        "empty-list-cheat": grade(0, [], {})["exit"] == 1,
        "pristine-red": grade(1, rows, MUTANTS)["exit"] == 1,
        "green-mutant": grade(0, [dict(row, mutant_exit=0) for row in rows], MUTANTS)["exit"] == 1,
        "wrong-arm": grade(0, [dict(row, failed_arms=["unrelated"]) for row in rows], MUTANTS)["exit"] == 1,
    }
    for name, ok in checks.items():
        print("SURVIVORS2_ARM {} {}".format(name, "ok" if ok else "FAIL"))
    failed = sum(not ok for ok in checks.values())
    print("SURVIVORS2_SELFTEST pass={} fail={}".format(len(checks) - failed, failed))
    return int(bool(failed))


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", default=".")
    parser.add_argument("--work", default=DEFAULT_WORK)
    parser.add_argument("--keep", action="store_true")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--selftest", action="store_true")
    args = parser.parse_args(argv)
    if args.selftest:
        return selftest()
    try:
        doc = probe(Path(args.repo).resolve(), Path(args.work).resolve(), args.keep)
    except (CouldNotEvaluate, OSError, UnicodeError, subprocess.SubprocessError) as exc:
        print("SURVIVORS2 CouldNotEvaluate: {}".format(exc))
        return 2
    for row in doc["results"]:
        killed = row["mutant_exit"] == 1 and EXPECTED_ARMS[row["mutant"]] in row["failed_arms"]
        print("{} {} mutant_exit={} arm={}".format(
            "SURVIVORS2_MUTANT" if killed else "SURVIVORS2_FINDING",
            row["mutant"], row["mutant_exit"],
            EXPECTED_ARMS[row["mutant"]] if killed else "none"))
    if doc["pristine_exit"]:
        print("SURVIVORS2_FINDING pristine mutant_exit={} arm={}".format(
            doc["pristine_exit"], ",".join(doc["pristine_failed_arms"]) or "none"))
    if not doc["complete"]:
        print("SURVIVORS2_FINDING catalogue mutant_exit=none arm=none")
    print("SURVIVORS2 mutants={mutants} killed={killed} escaped={escaped}".format(**doc))
    if args.json:
        print(json.dumps(doc, indent=2, sort_keys=True))
    return doc["exit"]


if __name__ == "__main__":
    sys.exit(main())
