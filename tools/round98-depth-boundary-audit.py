#!/usr/bin/env python3
"""round98-depth-boundary-audit.py - round-97 C3 (depth, lowest axis 7) frozen counter.

PREDICATE (frozen: plans/round-98-claims.md section C3):

    `python3 tools/round98-depth-boundary-audit.py --repo . --rev <M3>` prints
    `DEPTH_BOUNDARY98 rows=8 checks=<c> mismatches=0 met=True rev=<resolved>` and exits 0 at M3;
    the counter's own bytes never change after the freeze commit (kill rule K1).

Round-96's depth table states the per-rank ceilings but not the two boundary classes the
round-97 counter now grades, and its prose cannot answer "does this file decide?" for a
rank the table does not name. This counter re-derives every row of the SKILL.md section
`### Round 97 correction` against the probe's own MAX_STEPS:

    steps = 4 + T * (5 + nd)           four preamble steps, `5 + nd` per header
    verdict = "invalid" if steps <= MAX_STEPS else "-"

Each row is parsed, its stated step count recomputed, its `<=`/`>` comparison checked and
its verdict matched. A row whose arithmetic or comparison is wrong is a mismatch; the eight
required boundary rows are (833 332, nd=1), (833 333, nd=1), (900 000, nd=1),
(700 000, nd=4), (555 555, nd=4), (555 556, nd=4), (800 000, nd=1) and (520 000, nd=4). Literal presence of a number is not
enough: a table that says "the ceiling is 833,332" without the recomputed arithmetic for
the named file class fails, which is the round-96 C3 defect (CR02 B2-B5).

Exit: 0 met | 1 mismatches>0 | 2 could-not-evaluate.
"""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

PREAMBLE = 4
SECTION = "### Round 97 correction"
REQUIRED = {(833_332, 1), (833_333, 1), (900_000, 1), (700_000, 4),
            (555_555, 4), (555_556, 4), (800_000, 1), (520_000, 4)}
ROW = re.compile(
    r"^\|\s*([\d, ]+)\s*\|\s*nd=(\d)\s*\|\s*([\d, ]+)\s*\|\s*(<=|>)\s*budget\s*\|"
    r"\s*(invalid|-)\s*\|\s*$")


def show(repo: Path, rev: str, path: str):
    p = subprocess.run(["git", "-C", str(repo), "show", f"{rev}:{path}"], capture_output=True)
    return p.stdout.decode("utf-8", "replace") if p.returncode == 0 else None


def num(cell: str) -> int:
    return int(cell.replace(",", "").replace(" ", ""))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", type=Path, required=True)
    ap.add_argument("--rev", required=True)
    a = ap.parse_args()
    rv = subprocess.run(["git", "-C", str(a.repo), "rev-parse", "--verify", a.rev + "^{commit}"],
                        capture_output=True, text=True)
    if rv.returncode != 0:
        print(f"DEPTH_BOUNDARY98 could-not-evaluate: unresolvable rev {a.rev}")
        return 2
    rev = rv.stdout.strip()
    skill = show(a.repo, rev, "SKILL.md")
    probe = show(a.repo, rev, "tools/kama-probe.sh")
    if skill is None or probe is None:
        print("DEPTH_BOUNDARY98 could-not-evaluate: SKILL.md or tools/kama-probe.sh missing")
        return 2
    m = re.search(r"^MAX_STEPS = ([0-9_]+)", probe, re.M)
    if not m:
        print("DEPTH_BOUNDARY98 could-not-evaluate: no MAX_STEPS in the probe")
        return 2
    max_steps = int(m.group(1).replace("_", ""))

    lines = skill.splitlines()
    start = next((i for i, l in enumerate(lines) if l.startswith(SECTION)), None)
    mismatches = 0
    checks = 0
    rows = 0
    if start is None:
        checks += 1
        mismatches += 1
        print(f"DEPTH_BOUNDARY98 rows=0 mismatches={mismatches} met=False rev={rev}")
        return 1
    section = []
    for l in lines[start + 1:]:
        if l.startswith("### ") or l.startswith("## "):
            break
        section.append(l)

    seen = set()
    for line in section:
        rm = ROW.match(line.strip())
        if not rm:
            continue
        rows += 1
        checks += 1
        t = num(rm.group(1))
        nd = int(rm.group(2))
        stated_steps = num(rm.group(3))
        comp = rm.group(4)
        verdict = rm.group(5)
        want_steps = PREAMBLE + t * (5 + nd)
        within = want_steps <= max_steps
        want_comp = "<=" if within else ">"
        want_verdict = "invalid" if within else "-"
        if (stated_steps, comp, verdict) != (want_steps, want_comp, want_verdict):
            mismatches += 1
        seen.add((t, nd))

    for pair in sorted(REQUIRED - seen):
        checks += 1
        mismatches += 1

    # The table must be sourced on the spec and the superseding code row, and name the
    # budget it compares against.
    sect = "\n".join(section)
    checks += 1
    if "S620" not in sect or "S621" not in sect or "S622" not in sect:
        mismatches += 1
    checks += 1
    if "{:,}".format(max_steps) not in sect:
        mismatches += 1
    # The table's class caveat: the rows are KV-free files at rank <= 4 (CR01 boundary review).
    checks += 1
    if "KV-free" not in sect or "nd > 4" not in sect:
        mismatches += 1
    # The claimed row count is enforced, not descriptive (CR02 C3 clause 1).
    checks += 1
    if rows != 8:
        mismatches += 1

    print(f"DEPTH_BOUNDARY98 rows={rows} checks={checks} mismatches={mismatches} "
          f"met={mismatches == 0} rev={rev}")
    return 0 if mismatches == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
