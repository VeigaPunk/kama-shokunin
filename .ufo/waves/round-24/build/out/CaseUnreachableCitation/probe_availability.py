#!/usr/bin/env python3
"""Bounded probe for the CaseUnreachableCitation oracle case.

Purpose: prove that the fixture's two off-closure citations (X1 dangling =
unreachable from every ref, X2 = reachable only through refs/keep/x2) are
resolved by OBJECT EXISTENCE and are NOT resolved by REACHABILITY, so a
repair that decides "is this citation available?" by walking a closure
(rev-list of the branch, or of all refs) mis-handles this fixture while a
repair that asks the object store (cat-file) handles it correctly.

The probe is a measurement of git semantics only. It runs no auditor
version, no candidate implementation and no suite: it compares three
availability questions against the same built fixture.

Availability questions compared, for one citation oid:

  existence  git cat-file --batch-check <oid>          (object store)
  all-refs   git rev-list --all                        (ref closure)
  branch     git rev-list <branch>                     (branch closure)

Expected for the fixture (asserted, not printed as a discovery):

  C1  existence yes | all-refs yes | branch yes
  C2  existence yes | all-refs yes | branch yes
  X1  existence yes | all-refs NO  | branch NO
  X2  existence yes | all-refs yes | branch NO

Exit: 0 every expectation held; 2 could not evaluate (premise failed).
"""
from __future__ import annotations

import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

HERE = Path(__file__).resolve().parent
SCRATCH = Path("/fast/scratch/hyaku/kama-r24/CaseUnreachableCitation/probe")
CASE = HERE / "case_unreachable_citation.py"
sys.path.insert(0, str(HERE))
import case_unreachable_citation as case_mod  # noqa: E402


def env(**extra):
    e = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    e.update(GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_NOSYSTEM="1",
             GIT_AUTHOR_EMAIL="a@x", GIT_COMMITTER_EMAIL="a@x",
             GIT_AUTHOR_NAME="fixture", GIT_COMMITTER_NAME="fixture")
    e.update(extra)
    return e


def g(repo, *args, data=None):
    p = subprocess.run(["git", "--no-lazy-fetch", "-C", str(repo), *args],
                       input=data, capture_output=True, env=env())
    if p.returncode:
        raise case_mod.Premise(
            f"git {' '.join(map(str, args))}: "
            f"{p.stderr.decode(errors='replace').strip()}")
    return p.stdout.decode(errors="surrogateescape").strip()


def existence(repo, oid):
    out = g(repo, "cat-file", "--batch-check", data=(oid + "\n").encode())
    return out.startswith(oid + " commit")


def in_list(repo, oid, args):
    return oid in g(repo, "rev-list", *args).split("\n")


def main():
    if SCRATCH.exists():
        shutil.rmtree(SCRATCH)
    SCRATCH.mkdir(parents=True)
    facts = case_mod.build(SCRATCH)
    lane = Path(facts["lane"])
    expectations = {
        "C1": (True, True, True),
        "X1": (True, False, False),
        "X2": (True, True, False),
    }
    rows = {}
    failed = []
    for key, want in expectations.items():
        oid = facts[key.lower()]
        got = (existence(lane, oid),
               in_list(lane, oid, ("--all",)),
               in_list(lane, oid, ("master",)))
        rows[key] = {"oid": oid, "existence": got[0], "all_refs": got[1],
                     "branch": got[2], "expected": list(want)}
        if got != want:
            failed.append(f"{key}: got {got}, expected {want}")
    # X1 must really be dangling, and X2 really off-branch
    if "dangling commit" not in g(lane, "fsck", "--no-progress"):
        failed.append("fsck does not report X1 as dangling")
    doc = {"case": "CaseUnreachableCitation", "probe": "availability-questions",
           "rows": rows, "failed": failed}
    (HERE / "probe-availability.json").write_text(
        json.dumps(doc, indent=1, sort_keys=True), encoding="utf-8")
    shutil.rmtree(SCRATCH, ignore_errors=True)
    for key, row in rows.items():
        print(f"{key}: existence={row['existence']} all_refs={row['all_refs']} "
              f"branch={row['branch']} expected={row['expected']}")
    if failed:
        for line in failed:
            print("FAIL " + line, file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
