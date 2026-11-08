#!/usr/bin/env python3
"""round96-depth-audit.py - round-96 C2 (depth, lowest axis 7) frozen counter.

PREDICATE (frozen: plans/round-96-claims.md section C2):

    `python3 tools/round96-depth-audit.py --repo . --rev <M2>` prints
    `DEPTH_AUDIT checks=<c> mismatches=0 met=True` and exits 0 at the measured commit M2,
    the counter's bytes identical to this freeze commit.

Grades: the SKILL.md step-cost table exists and its arithmetic agrees with the probe's
constants at that revision (MAX_STEPS, `5 + nd` steps per tensor header, per-rank ceilings
from (MAX_STEPS - 4) // (5 + nd): 999,999 / 833,332 / 714,285 / 624,999 / 555,555), and S618
resolves to a Registry row with status not `rejected`.
"""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

STEPS_PER_HEADER = 6      # nd = 1: 5 + nd
PREAMBLE = 4              # magic rd(4), version u32, n_tensors u64, n_kv u64
CEILING = 833_332         # (5_000_000 - 4) // 6 = 833 332 decidable headers (RV01 F3)


def show(repo: Path, rev: str, path: str):
    p = subprocess.run(["git", "-C", str(repo), "show", f"{rev}:{path}"], capture_output=True)
    return p.stdout.decode("utf-8", "replace") if p.returncode == 0 else None


def sources_status(repo: Path, rev: str):
    text = show(repo, rev, "corpus/SOURCES.md")
    if text is None:
        raise SystemExit("no corpus/SOURCES.md")
    out = {}
    for line in text.splitlines():
        m = re.match(r"^ {0,3}\| *(S\d{3,}) *\|", line)
        if m:
            cells = [c.strip() for c in line.split("|")]
            out[m.group(1)] = cells[8] if len(cells) > 8 else ""
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", type=Path, required=True)
    ap.add_argument("--rev", required=True)
    a = ap.parse_args()
    rev = subprocess.run(["git", "-C", str(a.repo), "rev-parse", "--verify", a.rev + "^{commit}"],
                         capture_output=True, text=True)
    if rev.returncode != 0:
        print(f"DEPTH_AUDIT could-not-evaluate: unresolvable rev {a.rev}")
        return 2
    rev = rev.stdout.strip()
    skill = show(a.repo, rev, "SKILL.md") or ""
    probe = show(a.repo, rev, "tools/kama-probe.sh") or ""
    checks = 0
    mismatches = 0

    m = re.search(r"^MAX_STEPS = ([0-9_]+)", probe, re.M)
    max_steps = int(m.group(1).replace("_", "")) if m else None
    if max_steps != 5_000_000:
        mismatches += 1
    checks += 1

    derived_ceiling = max_steps // STEPS_PER_HEADER if max_steps else None
    for needle, label in (("`5 + nd` steps", "step-table"),
                          ("833,332", "ceiling"),
                          ("714,285", "nd2-ceiling"),
                          ("624,999", "nd3-ceiling"),
                          ("555,555", "nd4-ceiling"),
                          ("S618", "sourced")):
        checks += 1
        if needle not in skill:
            mismatches += 1
    status = sources_status(a.repo, rev).get("S618", "")
    checks += 1
    if status in ("", "rejected"):
        mismatches += 1
    derived = (max_steps - PREAMBLE) // STEPS_PER_HEADER if max_steps else None
    checks += 1
    if derived != CEILING:
        mismatches += 1
    # every rank's stated ceiling must equal the arithmetic the parser enforces (RV01 F2/SC02 def.)
    for nd, stated in ((0, 999_999), (1, 833_332), (2, 714_285), (3, 624_999), (4, 555_555)):
        checks += 1
        want = (max_steps - PREAMBLE) // (5 + nd) if max_steps else None
        if want != stated or "{:,}".format(want) not in skill:
            mismatches += 1
    print(f"DEPTH_AUDIT checks={checks} mismatches={mismatches} met={mismatches == 0}")
    return 0 if mismatches == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
