#!/usr/bin/env python3
"""case45_independent.py - distinct case 45, second implementation.

Deliberately shares nothing with canonical_rows_audit.py: different file reading
(string search + line slicing, not a table parser), different path test (a shell
`git cat-file -e` child, not os.path.exists), different section locator (a literal
line search, not a heading index).  It measures the same five quantities so the two
implementations can be compared:

  gen          the round in the last "canonical list as of round N" marker
  rows         body rows of the table that follows the last marker
  names        the first cell of each body row (unique count)
  evidence     rows whose every backticked path token resolves at --tip
  mirror       rows in the first table of the `## Capabilities` section
  firsts       length of the "capability first-working rounds" list in `## Saturation`
  expected     the greatest round named by "Mirror of the round-N" / "the round-N
               canonical capability list stays canonical"
  omission     expected != gen  (the control this seat's prototype must trip)

Usage: case45_independent.py --repo R --tip T
Exit 0 when the case's readings are internally consistent (rows == names ==
                 mirror == firsts and evidence == rows), else 1; 2 cannot evaluate.
"""
from __future__ import annotations

import argparse
import os
import subprocess
import sys

MARK = "canonical list as of round "
CAP_HDR = "| Capability | What it can now do | Evidence pointer | First-working round |"


def show(repo, tip, path):
    if tip:
        p = subprocess.run(["git", "-C", repo, "show", "%s:%s" % (tip, path)],
                           capture_output=True)
        return p.stdout.decode("utf-8", "replace") if p.returncode == 0 else None
    full = os.path.join(repo, path)
    return open(full, encoding="utf-8", errors="replace").read() if os.path.isfile(full) else None


def present(repo, tip, path):
    if tip:
        return subprocess.run(["git", "-C", repo, "cat-file", "-e", "%s:%s" % (tip, path)],
                              capture_output=True).returncode == 0
    return subprocess.run(["test", "-e", os.path.join(repo, path)]).returncode == 0


def backticked(cell):
    out, i = [], 0
    while True:
        a = cell.find("`", i)
        if a < 0:
            return out
        b = cell.find("`", a + 1)
        if b < 0:
            return out
        out.append(cell[a + 1:b])
        i = b + 1


def cells(line):
    """Split a pipe row without a regex: strip the outer pipes, then split."""
    body = line.strip()
    if body.startswith("|"):
        body = body[1:]
    if body.endswith("|"):
        body = body[:-1]
    return [c.strip() for c in body.split("|")]


def section_lines(rows, heading):
    out, on = [], False
    for r in rows:
        if r == heading:
            on = True
            continue
        if on and r.startswith("## "):
            break
        if on:
            out.append(r)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", default=".")
    ap.add_argument("--tip", default=None)
    a = ap.parse_args()
    repo = os.path.abspath(a.repo)
    sc = show(repo, a.tip, "SCORECARD.md")
    if sc is None:
        print("CASE45 could-not-evaluate: no SCORECARD.md", file=sys.stderr)
        return 2
    rows = sc.split("\n")

    # gen: the last marker, read by string search
    at = sc.rfind(MARK)
    if at < 0:
        print("CASE45 gen=none rows=0 names=0 evidence=0/0 mirror=0 firsts=0 "
              "expected=none omission=True consistent=False met=False")
        return 1
    tail = sc[at + len(MARK):]
    digits = ""
    for ch in tail:
        if ch.isdigit():
            digits += ch
        else:
            break
    gen = int(digits) if digits else None

    # rows: the first table after the marker, counted by line, no table parser
    idx = sc[:at].count("\n")
    while idx < len(rows) and not rows[idx].startswith("|"):
        idx += 1
    if idx < len(rows) and rows[idx].strip() != CAP_HDR:
        print("CASE45 gen=%s rows=0 names=0 evidence=0/0 mirror=0 firsts=0 expected=? "
              "omission=? consistent=False met=False" % gen)
        return 1
    idx += 2                                  # header + separator
    names, evidence, ev_tot = [], 0, 0
    while idx < len(rows) and rows[idx].startswith("|"):
        c = cells(rows[idx])
        names.append(c[0].strip("`").strip())
        if len(c) >= 3:
            toks = [t for t in backticked(c[2]) if "/" in t]
            ev_tot += 1
            if toks and all(present(repo, a.tip, t) for t in toks):
                evidence += 1
        idx += 1
    nrows = len(names)

    # mirror: rows of the first table in `## Capabilities`
    mirror = 0
    for ln in section_lines(rows, "## Capabilities"):
        if ln.startswith("|") and len(cells(ln)) == 4:
            mirror += 1
    mirror = max(0, mirror - 2)               # header + separator

    # firsts: the comma list after the literal phrase, read by slicing
    firsts = 0
    for ln in section_lines(rows, "## Saturation"):
        i = ln.find("capability first-working rounds ")
        if i < 0:
            continue
        rest = ln[i + len("capability first-working rounds "):]
        end = rest.find("(")
        chunk = rest if end < 0 else rest[:end]
        firsts = len([p for p in chunk.replace(" ", "").split(",") if p])
        break

    # expected: the greatest round the SCORECARD's own prose points at
    exp = []
    needle = "Mirror of the round-"
    i = 0
    while True:
        i = sc.find(needle, i)
        if i < 0:
            break
        j = i + len(needle)
        d = ""
        while j < len(sc) and sc[j].isdigit():
            d += sc[j]
            j += 1
        if d:
            exp.append(int(d))
        i = j
    needle2 = " canonical capability list stays canonical"
    i = 0
    while True:
        i = sc.find(needle2, i)
        if i < 0:
            break
        k, d = i, ""
        while k > 0 and sc[k - 1].isdigit():
            k -= 1
            d = sc[k] + d
        if d:
            exp.append(int(d))
        i += 1
    expected = max(exp) if exp else None

    omission = expected is not None and gen != expected
    consistent = (nrows == len(set(names)) == mirror == firsts and evidence == nrows
                  and nrows > 0 and not omission)
    print("CASE45 gen=%s rows=%d names=%d evidence=%d/%d mirror=%d firsts=%d expected=%s "
          "omission=%s consistent=%s met=%s"
          % (gen, nrows, len(set(names)), evidence, ev_tot, mirror, firsts, expected,
             omission, consistent, consistent))
    return 0 if consistent else 1


if __name__ == "__main__":
    sys.exit(main())
