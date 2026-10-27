#!/usr/bin/env python3
"""case49-calib-count-audit.py -- independent stale-count check for the
SCORECARD `## Axes` calibration row's verifier-spotcheck count.

Reads SCORECARD.md at a git tip, extracts the calibration row's
verifier-spotcheck run fact (counting command + claimed integer), then derives
the observed count two independent ways:

  tree  `git ls-tree` of the tip: blobs directly under corpus/lessons whose
        name ends with `verifier-spotcheck.md` (no working-tree access).
  exec  the row's own counting command, run with cwd = a `git archive` export
        of the same tip (measured bytes, not the working tree).

stale = claim != tree or claim != exec.  Exit 0 fresh, 1 stale, 2 cannot
evaluate.  Never writes to --repo.
"""
from __future__ import annotations

import argparse
import os
import re
import shutil
import subprocess
import sys
import tempfile

RUN_FACT = re.compile(r"run\s+`([^`]+)`\s*(?:→|->)\s*`([^`]+)`")
SPOT_CHECK_SUFFIX = "verifier-spotcheck.md"


def git(repo: str, *args: str, binary: bool = False):
    p = subprocess.run(["git", "-C", repo, *args], capture_output=True)
    if p.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)}: {p.stderr.decode(errors='replace').strip()}")
    return p.stdout if binary else p.stdout.decode()


def calib_row(text: str) -> list[str]:
    rows: list[list[str]] = []
    inside = False
    for line in text.split("\n"):
        if line.startswith("## "):
            if inside:
                break
            inside = line.strip() == "## Axes"
            continue
        if inside and line.startswith("|"):
            rows.append([c.strip() for c in line.strip().strip("|").split("|")])
    for r in rows:
        if len(r) >= 3 and r[0].replace("*", "").strip().split(" ")[0].lower() == "calibration":
            return r
    raise RuntimeError("no calibration row in '## Axes'")


def spot_fact(evidence: str) -> tuple[str, int]:
    for cmd, want in RUN_FACT.findall(evidence):
        if "verifier-spotcheck" in cmd:
            if not re.fullmatch(r"\d+", want):
                raise RuntimeError(f"claim token {want!r} is not an integer")
            return cmd, int(want)
    raise RuntimeError("calibration row has no verifier-spotcheck run fact")


def tree_count(repo: str, tip: str) -> int:
    names = git(repo, "ls-tree", "-r", "--name-only", tip, "corpus/lessons").split("\n")
    return sum(1 for n in names
               if n.startswith("corpus/lessons/")
               and "/" not in n[len("corpus/lessons/"):]
               and n.endswith(SPOT_CHECK_SUFFIX))


def exec_count(repo: str, tip: str, cmd: str) -> int | None:
    export = tempfile.mkdtemp(prefix="case49-export-")
    try:
        arc = git(repo, "archive", "--format=tar", tip, binary=True)
        subprocess.run(["tar", "-x", "-C", export], input=arc, check=True)
        p = subprocess.run(["bash", "-c", cmd], cwd=export, capture_output=True,
                           text=True, timeout=300)
        if p.returncode != 0:
            return None
        ints = [int(l.strip()) for l in p.stdout.splitlines() if re.fullmatch(r"\d+", l.strip())]
        return ints[0] if ints else None
    finally:
        shutil.rmtree(export, ignore_errors=True)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", default=".")
    ap.add_argument("--tip", default="HEAD")
    a = ap.parse_args()
    repo = os.path.abspath(a.repo)
    try:
        tip = git(repo, "rev-parse", "--verify", f"{a.tip}^{{commit}}").strip()
        sc = git(repo, "show", f"{tip}:SCORECARD.md")
        row = calib_row(sc)
        cmd, claim = spot_fact(row[2])
        tree = tree_count(repo, tip)
        exe = exec_count(repo, tip, cmd)
    except (RuntimeError, subprocess.CalledProcessError) as e:
        print(f"cannot-evaluate: {e}")
        return 2
    if exe is None:
        print(f"repo={repo} tip={tip} axis=calibration claim={claim} tree_count={tree} "
              f"exec_count=none stale=indeterminate reason=counting-command-produced-no-integer")
        return 2
    stale = claim != tree or claim != exe
    reason = "claim==tree==exec" if not stale else (
        "claim!=tree" if claim != tree else "claim!=exec")
    print(f"repo={repo} tip={tip} axis=calibration claim={claim} tree_count={tree} "
          f"exec_count={exe} stale={stale} reason={reason}")
    return 1 if stale else 0


if __name__ == "__main__":
    sys.exit(main())
