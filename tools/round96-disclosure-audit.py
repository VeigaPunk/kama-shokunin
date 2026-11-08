#!/usr/bin/env python3
"""round96-disclosure-audit.py - round-96 C3 (calibration) frozen counter.

PREDICATE (frozen: plans/round-96-claims.md section C3):

    `python3 tools/round96-disclosure-audit.py --repo . --rev <M3>` prints
    `DISCLOSURE_AUDIT checks=<d> mismatches=0 met=True` and exits 0 at the measured commit M3,
    the counter's bytes identical to this freeze commit.

Grades three filings against the bytes beside them:
(1) the probe's ceiling comment agrees with MAX_STEPS (6 steps per tensor header) and no longer
    names 1 000 000 as the enforced ceiling;
(2) the frozen C1 counter's docstring formula (`20 + 25 * npaths`) matches the shell wrapper
    literal;
(3) the `router-byte-decided` capability row's evidence commit resolves and precedes the tip.
"""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path


def show(repo: Path, rev: str, path: str):
    p = subprocess.run(["git", "-C", str(repo), "show", f"{rev}:{path}"], capture_output=True)
    return p.stdout.decode("utf-8", "replace") if p.returncode == 0 else None


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", type=Path, required=True)
    ap.add_argument("--rev", required=True)
    a = ap.parse_args()
    rv = subprocess.run(["git", "-C", str(a.repo), "rev-parse", "--verify", a.rev + "^{commit}"],
                        capture_output=True, text=True)
    if rv.returncode != 0:
        print(f"DISCLOSURE_AUDIT could-not-evaluate: unresolvable rev {a.rev}")
        return 2
    rev = rv.stdout.strip()
    probe = show(a.repo, rev, "tools/kama-probe.sh") or ""
    counter = show(a.repo, rev, "tools/round96-router-budget.py") or ""
    score = show(a.repo, rev, "SCORECARD.md") or ""
    checks = 0
    mismatches = 0

    m = re.search(r"^MAX_STEPS = ([0-9_]+)", probe, re.M)
    max_steps = int(m.group(1).replace("_", "")) if m else None
    checks += 1
    if max_steps != 5_000_000 or "6 steps per tensor header" not in probe:
        mismatches += 1
    checks += 1
    if "MAX_TENSORS = 1_000_000" in probe and "the ceiling is 1,000,000" in probe:
        mismatches += 1
    checks += 1
    if "20 + 25 * npaths" not in counter or "20 + 15 * ncand" in counter:
        mismatches += 1
    # capability row: find the router-byte-decided row, extract its commit hash
    checks += 1
    row = None
    for line in score.splitlines():
        if "router-byte-decided" in line and line.startswith("|"):
            row = line
    m2 = re.search(r"`([0-9a-f]{4,40})`", row or "")
    if not m2:
        mismatches += 1
    else:
        ev = m2.group(1)
        ok = subprocess.run(["git", "-C", str(a.repo), "cat-file", "-e", f"{ev}^{{commit}}"],
                            capture_output=True).returncode == 0
        anc = subprocess.run(["git", "-C", str(a.repo), "merge-base", "--is-ancestor", ev, rev],
                             capture_output=True).returncode == 0
        if not (ok and anc):
            mismatches += 1
    checks += 1
    if probe and "20 + 25 * npaths" not in probe:
        mismatches += 1
    print(f"DISCLOSURE_AUDIT checks={checks} mismatches={mismatches} met={mismatches == 0}")
    return 0 if mismatches == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
