#!/usr/bin/env python3
"""round97-self-assessment-audit.py - round-97 C1 (calibration, lowest axis 7) frozen counter.

PREDICATE (frozen: plans/round-97-claims.md section C1):

    `python3 tools/round97-self-assessment-audit.py --repo . --rev <M1>` prints
    `SELF_ASSESS97 checks=14 mismatches=0 met=True` and exits 0 at the measured commit M1;
    the counter's own bytes never change after the freeze commit (kill rule K1).

A calibration claim counts mismatches between what the lane says about itself and the
repository it claims to describe (AXES.md calibration; CORPUS.md "a count carries its
command"). Round-96's closure routed defect 1: the probe ceiling comment and S618's
`teaches` cell restated a constant "6 steps per tensor header" while the parser prices
`5 + nd`; the round-96 C3 counter stayed green because it REQUIRED that string. This
counter grades the binding claim instead:

  1-3  SCORECARD live `depth` row: SKILL.md sha256, line count, `^## ` section count.
  4-5  SCORECARD live `adjacency` row: cross-lane-scope.md sha256 and pipe-line count.
  6    SCORECARD capability row `router-byte-decided`: the pointer commit resolves, is an
       ancestor of the graded revision, and the evidence path it cites exists there.
  7    The probe's ceiling comment states `5 + nd` and no longer states a constant
       "6 steps per tensor header".
  8    The probe's comment carries every per-rank ceiling derived from MAX_STEPS:
       (MAX_STEPS - 4) // (5 + nd) for nd = 1..4.
  9    SKILL.md's step-cost section carries all five ceilings (nd = 0..4) and cites both
       S620 (the spec) and S621 (the superseding code row).
  10   S621 exists, is status `mined`, and its `teaches` opens `supersedes S618 —` with the
       `5 + nd` arithmetic (append-only correction of S618's false constant-6 cell).
  11   S620 exists, is status `mined`, kind `spec`, tier `A` (the GGUF spec opened this
       round; it grounds the five-field tensor-info struct and `dimensions[n_dimensions]`).
  12   The round-96 identity clause is true: `tools/round96-router-budget.py` at `f175a902`
       is byte-identical to the graded revision's file, and SCORECARD names `f175a902`.
  13-14 SCORECARD's quoted round-96 C2 and C3 receipts are present in the receipts
       themselves (`DEPTH_AUDIT checks=14 mismatches=0`, `DISCLOSURE_AUDIT checks=6
       mismatches=0`); a quoted number no receipt carries is a fabrication.

Exit: 0 met | 1 mismatches>0 | 2 could-not-evaluate.
"""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

PREAMBLE = 4
COUNTER96 = "tools/round96-router-budget.py"
IDENTITY_REV = "f175a902"


def show(repo: Path, rev: str, path: str):
    p = subprocess.run(["git", "-C", str(repo), "show", f"{rev}:{path}"], capture_output=True)
    return p.stdout.decode("utf-8", "replace") if p.returncode == 0 else None


def git(repo: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True)


def sources_rows(text: str) -> dict:
    rows = {}
    for line in (text or "").splitlines():
        m = re.match(r"^ {0,3}\| *(S\d{3,}) *\|", line)
        if m:
            rows[m.group(1)] = [c.strip() for c in line.split("|")]
    return rows


_detail = []

def _mark():
    _detail.append(True)

def _fail():
    _detail[-1] = False

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", type=Path, required=True)
    ap.add_argument("--rev", required=True)
    a = ap.parse_args()
    rv = git(a.repo, "rev-parse", "--verify", a.rev + "^{commit}")
    if rv.returncode != 0:
        print(f"SELF_ASSESS97 could-not-evaluate: unresolvable rev {a.rev}")
        return 2
    rev = rv.stdout.strip()
    skill = show(a.repo, rev, "SKILL.md")
    score = show(a.repo, rev, "SCORECARD.md")
    probe = show(a.repo, rev, "tools/kama-probe.sh")
    sources = show(a.repo, rev, "corpus/SOURCES.md")
    if skill is None or score is None or probe is None or sources is None:
        print("SELF_ASSESS97 could-not-evaluate: SKILL.md, SCORECARD.md, tools/kama-probe.sh "
              "or corpus/SOURCES.md missing at the graded revision")
        return 2

    checks = 0
    mismatches = 0

    # 1-3: the live depth row must describe SKILL.md at this revision.
    depth = next((l for l in score.splitlines() if l.startswith("| depth |")), "")
    declared_sha = re.search(r"sha256 `([0-9a-f]{64})`", depth)
    declared_lines = re.search(r"\((\d+) lines\)", depth)
    declared_sections = re.search(r"grep -c '\^## ' SKILL\.md` → `(\d+)`", depth)
    observed_sha = subprocess.run(["git", "-C", str(a.repo), "show", f"{rev}:SKILL.md"],
                                  capture_output=True).stdout
    import hashlib
    checks += 1; _mark()
    if not declared_sha or hashlib.sha256(observed_sha).hexdigest() != declared_sha.group(1):
        mismatches += 1; _fail()
    checks += 1; _mark()
    if not declared_lines or int(declared_lines.group(1)) != len(skill.splitlines()):
        mismatches += 1; _fail()
    checks += 1; _mark()
    sections = sum(1 for l in skill.splitlines() if l.startswith("## "))
    if not declared_sections or int(declared_sections.group(1)) != sections:
        mismatches += 1; _fail()

    # 4-5: the adjacency row's declared digest and pipe-line count.
    adj = next((l for l in score.splitlines() if l.startswith("| adjacency |")), "")
    adj_sha = re.search(r"sha256 `([0-9a-f]{64})`", adj)
    adj_pipes = re.search(r"→ `(\d+)` \(lines starting with a table pipe", adj)
    cross = show(a.repo, rev, "corpus/knowledge/cross-lane-scope.md") or ""
    checks += 1; _mark()
    if not adj_sha or hashlib.sha256(cross.encode()).hexdigest() != adj_sha.group(1):
        mismatches += 1; _fail()
    checks += 1; _mark()
    if not adj_pipes or int(adj_pipes.group(1)) != sum(1 for l in cross.splitlines()
                                                       if l.startswith("|")):
        mismatches += 1; _fail()

    # 6: the capability pointer resolves, precedes the tip, and its evidence path exists.
    cap = next((l for l in score.splitlines()
                if l.startswith("|") and "`router-byte-decided`" in l), "")
    ptr = re.search(r"`([0-9a-f]{7,40})`", cap)
    ev = re.search(r"`(\.ufo/waves/[^`]+)`", cap)
    checks += 1; _mark()
    if not ptr or not ev:
        mismatches += 1; _fail()
    else:
        exists = git(a.repo, "cat-file", "-e", f"{ptr.group(1)}^{{commit}}").returncode == 0
        anc = git(a.repo, "merge-base", "--is-ancestor", ptr.group(1), rev).returncode == 0
        has_path = show(a.repo, ptr.group(1), ev.group(1)) is not None
        if not (exists and anc and has_path):
            mismatches += 1; _fail()

    # 7-8: the probe's ceiling comment states the binding arithmetic and every rank ceiling.
    m = re.search(r"^MAX_STEPS = ([0-9_]+)", probe, re.M)
    max_steps = int(m.group(1).replace("_", "")) if m else None
    checks += 1; _mark()
    if "5 + nd" not in probe or "6 steps per tensor header" in probe:
        mismatches += 1; _fail()
    checks += 1; _mark()
    if max_steps is None:
        mismatches += 1; _fail()
    else:
        for nd in (1, 2, 3, 4):
            want = "{:,}".format((max_steps - PREAMBLE) // (5 + nd))
            if want not in probe:
                mismatches += 1; _fail()
                break

    # 9: SKILL carries all five ceilings and cites the spec and the superseding row.
    checks += 1; _mark()
    if max_steps is None:
        mismatches += 1; _fail()
    else:
        ok = "S620" in skill and "S621" in skill
        for nd in range(0, 5):
            ok = ok and "{:,}".format((max_steps - PREAMBLE) // (5 + nd)) in skill
        if not ok:
            mismatches += 1; _fail()

    # 10-11: the correction row and the spec row.
    rows = sources_rows(sources)
    s621 = rows.get("S621", [])
    checks += 1; _mark()
    if not s621 or len(s621) < 12:
        mismatches += 1; _fail()
    else:
        teaches = s621[7]
        status = s621[8]
        if not teaches.startswith("supersedes S618 —") or "5 + nd" not in teaches \
                or status != "mined":
            mismatches += 1; _fail()
    s620 = rows.get("S620", [])
    checks += 1; _mark()
    if not s620 or len(s620) < 12:
        mismatches += 1; _fail()
    else:
        if s620[3] != "spec" or s620[4] != "A" or s620[8] != "mined":
            mismatches += 1; _fail()

    # 12: the round-96 identity clause names a revision whose bytes are the current bytes.
    checks += 1; _mark()
    cur = show(a.repo, rev, COUNTER96)
    old = show(a.repo, IDENTITY_REV, COUNTER96)
    if cur is None or old is None or cur != old or IDENTITY_REV not in score:
        mismatches += 1; _fail()

    # 13-14: quoted round-96 receipts exist in their own files.
    for path, needle in ((".ufo/waves/round-96/measured/c2.out",
                          "DEPTH_AUDIT checks=14 mismatches=0"),
                         (".ufo/waves/round-96/measured/c3.out",
                          "DISCLOSURE_AUDIT checks=6 mismatches=0")):
        checks += 1; _mark()
        receipt = show(a.repo, rev, path) or ""
        if needle not in receipt or needle not in score.replace("`", ""):
            mismatches += 1; _fail()

    print("PERCHECK " + " ".join(f"{i+1}:{'P' if v else 'F'}" for i, v in enumerate(_detail)))
    print(f"SELF_ASSESS97 checks={checks} mismatches={mismatches} met={mismatches == 0}")
    return 0 if mismatches == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
