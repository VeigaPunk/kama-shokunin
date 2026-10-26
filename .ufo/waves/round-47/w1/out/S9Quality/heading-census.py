#!/usr/bin/env python3
"""heading-census.py - which lane files call themselves append-only, and is each in the contract?

Scans every lane `.md` outside `.ufo/` for a heading that contains `append-only`
(case-insensitive), and prints one row per heading with whether the file the
heading sits in is matched by a `registry/append-only-contract.tsv` path pattern
(fnmatch on the full repo-relative path, the same rule tools/append-only-audit.py
uses). The heading rule is a candidate generator, not a verdict: a heading such as
`## Round-46 instrument registry (... append-only calibration)` labels a topic
rather than declaring the containing file append-only, and the seat dispositions
each flagged row by hand.

Usage: heading-census.py --repo <clone> [--head <rev>]
Prints `headings=N covered=C uncovered=U` then one `path:line covered=yes|no <text>` line.
Read-only; exit 0 always (a survey, not a gate).
"""
from __future__ import annotations

import argparse
import fnmatch
import subprocess


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", required=True)
    ap.add_argument("--head", default="HEAD")
    a = ap.parse_args()

    files = subprocess.run(["git", "-C", a.repo, "ls-tree", "-r", "--name-only", a.head],
                           capture_output=True, text=True, check=True).stdout.split()
    mds = [f for f in files if f.endswith(".md") and not f.startswith(".ufo/")]
    shown = subprocess.run(["git", "-C", a.repo, "show", f"{a.head}:registry/append-only-contract.tsv"],
                           capture_output=True, text=True, check=True).stdout.splitlines()
    pats = [line.split("\t")[0] for line in shown[1:] if line.strip()]
    if not pats:
        print("no contract rows")
        return 0

    rows = []
    for f in mds:
        body = subprocess.run(["git", "-C", a.repo, "show", f"{a.head}:{f}"],
                              capture_output=True, text=True).stdout
        for i, line in enumerate(body.split("\n"), 1):
            if line.lstrip().startswith("#") and "append-only" in line.lower():
                cov = any(fnmatch.fnmatchcase(f, p) for p in pats)
                rows.append((f, i, cov, line.strip()))

    covered = sum(1 for r in rows if r[2])
    print(f"headings={len(rows)} covered={covered} uncovered={len(rows) - covered}")
    for f, i, cov, text in rows:
        print(f"{f}:{i} covered={'yes' if cov else 'no'} {text[:110]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
