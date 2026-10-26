#!/usr/bin/env python3
"""round44-release-recheck-audit.py - kama round-44 C1 (freshness) counter.

Question: at a lane revision, has every frozen population row - a registry row
of the base tree whose recheck cadence is `on-release` and whose source is a
ggml-org/llama.cpp file pinned to a commit - been re-verified at llama.cpp
release b11889, with each verdict re-derivable from the upstream bytes, and is
every row whose anchored statement drifted or vanished flagged where the lane
uses it?

Frozen names (before data):
  base        9d9cc93ec50783cd114829a91757b90d57c78dc6 (population source)
  release     b11889 = d854d98bae598388ecea1ed84396587e5edc326d
  ledger      registry/release-recheck-b11889.tsv
  sources     corpus/SOURCES.md, section heading containing
              `Round-44 release re-verification`
Population: registry rows of corpus/SOURCES.md at base (0-3 leading spaces,
`| S###`), 11 cells, recheck cell `on-release`, status `mined` or `queued`,
source cell naming https://github.com/ggml-org/llama.cpp/(blob|tree)/<ref>/<path>
or https://raw.githubusercontent.com/ggml-org/llama.cpp/<ref>/<path>; the pin is
<ref> when it is 40-hex, else the first 40-hex run of the anchor cell; rows
with neither are outside the population. Path drops any `#...` suffix.

Ledger: TSV, header then one row per population id:
  id path pin_commit release pin_blob release_blob changed pin_lines
  release_lines verdict note
  pin_blob / release_blob  `git rev-parse <commit>:<path>`; release_blob `-` when
                           the path is absent at the release
  changed     1 when the blobs differ, else 0
  pin_lines   comma list of 1-based inclusive ranges `a-b` (or `a`), each <= 80
              lines and inside the pinned file
  release_lines  same count of elements, each a range inside the release file
              or `-`
  verdict     unchanged-file  changed 0 and release_lines == pin_lines
              holds           changed 1, every pair text-equal
              holds-reworded  changed 1, no element `-`, at least one pair not
                              text-equal, the statement still true; note >= 20
              drifted         changed 1, not every element `-` (the anchored
                              text may be equal while the statement around it
                              changed); note >= 20 chars
              removed         every release element `-`; for each pin range its
                              first stripped line of >= 8 chars occurs as no
                              stripped line of the release file; note >= 20 chars
  text-equal: the stripped non-blank lines of the two ranges, joined, are equal.
Cited lines: numbers in the source and anchor cells after removing 7+ hex runs,
ISO dates, `round-N` and `b/v` version tokens. STRONG: `#L<a>[-L<b>]`, `L<n>`,
`line(s) <n>` and bare `<a>-<b>` ranges (b-a < 400); WEAK: other bare 2-5 digit
numbers. Every STRONG number not beyond the pinned file's length must lie in
the union of pin_lines; when no STRONG number applies and some WEAK number is
within the file, the union must contain at least one WEAK number. Every pin
range must carry >= 20 non-whitespace characters.

A population row is VALID when it has exactly one ledger row, path and
pin_commit equal the population's, release is `b11889`, both blobs and the
changed flag re-derive, the ranges parse and satisfy its verdict, and the
cited-line rule holds. unverified = population - valid.
Flags: for each valid drifted/removed row, every used-by path that is a
`corpus/knowledge/*.md` file existing at --tip has a line containing the id and
`b11889`, and the SOURCES section has a line containing the id.
met = unverified 0 and flags_missing 0 and the SOURCES section exists.
PREDICATE (same sentence in the preregistration): every frozen population row
re-verifies at b11889 from upstream bytes and every drifted or removed row is
flagged; unverified=0.

Output: `pop=P rows=R valid=V unverified=U unchanged=a holds=h reworded=w
drifted=d removed=r flags_missing=F section=S met=True|False`, then `detail:`
lines.
Exit 0 met, 1 not met, 2 could not evaluate (git failure on lane or upstream).
Read-only on --repo and --upstream (a blobless clone fetches blobs lazily).
"""
from __future__ import annotations

import argparse
import re
import subprocess
import sys

BASE = "9d9cc93ec50783cd114829a91757b90d57c78dc6"
RELEASE = "b11889"
RELEASE_COMMIT = "d854d98bae598388ecea1ed84396587e5edc326d"
LEDGER = "registry/release-recheck-b11889.tsv"
SOURCES = "corpus/SOURCES.md"
SECTION = "Round-44 release re-verification"
HEADER = ["id", "path", "pin_commit", "release", "pin_blob", "release_blob",
          "changed", "pin_lines", "release_lines", "verdict", "note"]
ROW = re.compile(r"^ {0,3}\|\s*(S\d{3,})\s*\|")
URL = re.compile(r"https://(?:github\.com/ggml-org/llama\.cpp/(?:blob|tree)/([\w.\-]+)/([^\s`;,)|]+)"
                 r"|raw\.githubusercontent\.com/ggml-org/llama\.cpp/([\w.\-]+)/([^\s`;,)|]+))")
HEX40 = re.compile(r"\b[0-9a-f]{40}\b")


class EvalError(Exception):
    pass


def git(repo, *args, check=True):
    p = subprocess.run(["git", "-C", repo, *args], capture_output=True, text=True)
    if check and p.returncode != 0:
        raise EvalError(f"git {' '.join(args)}: {p.stderr.strip()[:200]}")
    return p


def show(repo, rev, path):
    p = git(repo, "show", f"{rev}:{path}", check=False)
    return p.stdout if p.returncode == 0 else None


def blob(repo, rev, path):
    p = git(repo, "rev-parse", "--verify", "-q", f"{rev}:{path}", check=False)
    return p.stdout.strip() if p.returncode == 0 else "-"


def cells(line):
    return [c.strip() for c in line.strip().strip("|").split("|")]


def population(text):
    out = {}
    for line in text.splitlines():
        if not ROW.match(line):
            continue
        c = cells(line)
        if len(c) != 11 or c[9] != "on-release" or c[7] not in ("mined", "queued"):
            continue
        m = URL.search(c[1])
        if not m:
            continue
        ref, path = (m.group(1), m.group(2)) if m.group(1) else (m.group(3), m.group(4))
        path = path.split("#")[0]
        if HEX40.fullmatch(ref):
            pin = ref
        else:
            h = HEX40.search(c[5])
            if not h:
                continue
            pin = h.group(0)
        out[c[0]] = {"path": path, "pin": pin, "cells": c}
    return out


def cited(c):
    s = c[1] + " " + c[5]
    s = re.sub(r"[0-9a-fA-F]{7,}", " ", s)
    s = re.sub(r"\d{4}-\d\d-\d\d", " ", s)
    s = re.sub(r"round-\d+", " ", s)
    s = re.sub(r"\b[bv]\d[\d.]*", " ", s)
    strong, weak = set(), set()
    for m in re.finditer(r"#L(\d+)(?:-L(\d+))?", s):
        a, b = int(m.group(1)), int(m.group(2) or m.group(1))
        if 0 < a <= b and b - a < 400:
            strong.update(range(a, b + 1))
    for m in re.finditer(r"\bL(\d{1,5})\b", s):
        strong.add(int(m.group(1)))
    for m in re.finditer(r"(?<![\w.])(\d{1,5})\s*[-\u2013]\s*(\d{1,5})(?![\w.])", s):
        a, b = int(m.group(1)), int(m.group(2))
        if 0 < a <= b and b - a < 400:
            strong.update(range(a, b + 1))
    for m in re.finditer(r"\blines? (\d{1,5})(?![\w.\-])", s):
        strong.add(int(m.group(1)))
    for m in re.finditer(r"(?<![\w.#\-])(\d{2,5})(?![\w.\-])", s):
        weak.add(int(m.group(1)))
    return strong, weak - strong


def ranges(spec, allow_dash):
    out = []
    for el in spec.split(","):
        el = el.strip()
        if el == "-" and allow_dash:
            out.append(None)
            continue
        m = re.fullmatch(r"(\d+)(?:-(\d+))?", el)
        if not m:
            return None
        a, b = int(m.group(1)), int(m.group(2) or m.group(1))
        if a < 1 or b < a or b - a >= 80:
            return None
        out.append((a, b))
    return out or None


MOVE = 2000
QUOTE = 12


def note_quotes(note, text, n=QUOTE):
    note = re.sub(r"\s+", " ", note)
    text = re.sub(r"\s+", " ", text).strip()
    return bool(text) and any(text[i:i + n] in note for i in range(0, len(text) - n + 1))


def pin_first_lines(ptext, pr):
    return [next((x.strip() for x in ptext[p[0] - 1:p[1]] if len(x.strip()) >= 8), None) for p in pr]


def excerpt(lines, r):
    return "\n".join(x.strip() for x in lines[r[0] - 1:r[1]] if x.strip())


def check_row(ent, lr, up):
    """Return (ok, reason)."""
    path, pin = ent["path"], ent["pin"]
    if lr["path"] != path or lr["pin_commit"] != pin:
        return False, "path/pin differ from population"
    if lr["release"] != RELEASE:
        return False, "release cell"
    pb, rb = blob(up, pin, path), blob(up, RELEASE_COMMIT, path)
    if pb == "-":
        return False, "path absent at pin upstream"
    if lr["pin_blob"] != pb or lr["release_blob"] != rb:
        return False, f"blob mismatch (want {pb[:10]} {rb[:10]})"
    changed = "0" if pb == rb else "1"
    if lr["changed"] != changed:
        return False, "changed flag"
    pr = ranges(lr["pin_lines"], False)
    rr = ranges(lr["release_lines"], True)
    if pr is None or rr is None or len(pr) != len(rr):
        return False, "ranges do not parse or counts differ"
    ptext = show(up, pin, path).splitlines()
    rtext = (show(up, RELEASE_COMMIT, path) or "").splitlines() if rb != "-" else []
    for r in pr:
        if r[1] > len(ptext):
            return False, "pin range outside file"
        if len(re.sub(r"\s", "", "".join(ptext[r[0] - 1:r[1]]))) < 20:
            return False, "pin range carries < 20 non-whitespace chars"
    for r in rr:
        if r and r[1] > len(rtext):
            return False, "release range outside file"
    strong, weak = cited(ent["cells"])
    covered = lambda n: any(a <= n <= b for (a, b) in pr)
    strong = {n for n in strong if n <= len(ptext)}
    weak = {n for n in weak if n <= len(ptext)}
    if strong:
        miss = sorted(n for n in strong if not covered(n))
        if miss:
            return False, f"pin_lines miss cited lines {miss[:5]}"
    elif weak and not any(covered(n) for n in weak):
        return False, "pin_lines miss every cited number"
    v, note = lr["verdict"], lr["note"]
    pairs = list(zip(pr, rr))
    eq = [r is not None and excerpt(ptext, p) == excerpt(rtext, r) for p, r in pairs]
    if v == "unchanged-file":
        return (changed == "0" and lr["release_lines"].replace(" ", "") == lr["pin_lines"].replace(" ", ""),
                "unchanged-file rule")
    if changed != "1":
        return False, f"{v} needs changed=1"
    near = all(r is not None and abs(r[0] - p[0]) <= MOVE for p, r in pairs)
    rising = all(r is not None for r in rr) and all(rr[i + 1][0] > rr[i][1] for i in range(len(rr) - 1))
    if v == "holds":
        return (all(eq) and near and rising), "holds needs ordered, near, text-equal pairs"
    if v == "holds-reworded":
        if len(note) < 20:
            return False, "note too short"
        if not (near and rising):
            return False, "holds-reworded pairs must be near and rising"
        diff = [(p, r) for (p, r), e in zip(pairs, eq) if r is not None and not e]
        if not diff:
            return False, "holds-reworded needs a differing pair"
        if not any(note_quotes(note, excerpt(rtext, r)) for _, r in diff):
            return False, "note does not quote the reworded release text"
        return True, ""
    if v == "drifted":
        if len(note) < 20:
            return False, "note too short"
        if not near:
            return False, "release ranges must stay within MOVE of the pin ranges"
        rset = {x.strip() for x in rtext}
        gone = [f for f in pin_first_lines(ptext, pr) if f and f not in rset]
        if not gone:
            return False, "drifted without a missing pin line"
        if not any(note_quotes(note, g, 16) for g in gone):
            return False, "note does not quote a missing pin line"
        return True, ""
    if v == "removed":
        if len(note) < 20 or not all(r is None for r in rr):
            return False, "removed rule"
        if rb != "-":
            return False, "removed but path present at release"
        rset = {x.strip() for x in rtext}
        for p in pr:
            first = next((x.strip() for x in ptext[p[0] - 1:p[1]] if len(x.strip()) >= 8), None)
            if first is None or first in rset:
                return False, "removed: pin text still present"
        return True, ""
    return False, "unknown verdict"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", required=True)
    ap.add_argument("--tip", required=True)
    ap.add_argument("--upstream", required=True, help="llama.cpp clone holding both commits")
    ap.add_argument("--out")
    a = ap.parse_args()
    detail = []
    try:
        tip = git(a.repo, "rev-parse", "--verify", a.tip + "^{commit}").stdout.strip()
        for c in (RELEASE_COMMIT,):
            git(a.upstream, "cat-file", "-e", c + "^{commit}")
        base_src = show(a.repo, BASE, SOURCES)
        if base_src is None:
            raise EvalError("base SOURCES.md unreadable")
        pop = population(base_src)
        for e in pop.values():
            git(a.upstream, "cat-file", "-e", e["pin"] + "^{commit}")
        led_text = show(a.repo, tip, LEDGER)
        ledger = {}
        dup = set()
        if led_text is not None:
            lines = [x for x in led_text.splitlines() if x.strip()]
            if lines and lines[0].split("\t") == HEADER:
                for x in lines[1:]:
                    f = x.split("\t")
                    if len(f) != len(HEADER):
                        detail.append(f"bad ledger line: {x[:60]}")
                        continue
                    d = dict(zip(HEADER, f))
                    if d["id"] in ledger:
                        dup.add(d["id"])
                    ledger[d["id"]] = d
            else:
                detail.append("ledger header mismatch")
        counts = {"unchanged-file": 0, "holds": 0, "holds-reworded": 0, "drifted": 0, "removed": 0}
        valid = []
        for sid, ent in sorted(pop.items()):
            lr = ledger.get(sid)
            if lr is None:
                detail.append(f"{sid} no ledger row")
                continue
            if sid in dup:
                detail.append(f"{sid} duplicate ledger rows")
                continue
            ok, why = check_row(ent, lr, a.upstream)
            if ok:
                valid.append(sid)
                counts[lr["verdict"]] += 1
            else:
                detail.append(f"{sid} invalid: {why}")
        tip_src = show(a.repo, tip, SOURCES) or ""
        sec_lines, in_sec = [], False
        for x in tip_src.splitlines():
            if x.startswith("#"):
                in_sec = SECTION in x
                continue
            if in_sec:
                sec_lines.append(x)
        section = int(any(SECTION in x and x.startswith("#") for x in tip_src.splitlines()))
        missing = 0
        for sid in valid:
            lr = ledger[sid]
            if lr["verdict"] not in ("drifted", "removed"):
                continue
            if not any(RELEASE in x and re.findall(r"\bS\d{3,}\b", x) == [sid] for x in sec_lines):
                missing += 1
                detail.append(f"{sid} not listed in SOURCES section")
            for u in [u.strip() for u in pop[sid]["cells"][10].split(",")]:
                if not re.fullmatch(r"corpus/knowledge/[\w.\-]+\.md", u):
                    continue
                body = show(a.repo, tip, u)
                if body is None:
                    missing += 1
                    detail.append(f"{sid} used-by entry missing: {u}")
                    continue
                if not any(RELEASE in x and re.findall(r"\bS\d{3,}\b", x) == [sid] for x in body.splitlines()):
                    missing += 1
                    detail.append(f"{sid} not flagged in {u}")
    except EvalError as e:
        print(f"could-not-evaluate: {e}", file=sys.stderr)
        return 2
    unverified = len(pop) - len(valid)
    met = unverified == 0 and missing == 0 and section == 1
    line = (f"pop={len(pop)} rows={len(ledger)} valid={len(valid)} unverified={unverified} "
            f"unchanged={counts['unchanged-file']} holds={counts['holds']} reworded={counts['holds-reworded']} "
            f"drifted={counts['drifted']} removed={counts['removed']} flags_missing={missing} "
            f"section={section} met={met}")
    out = [f"tip={tip}", line] + [f"detail: {d}" for d in detail]
    text = "\n".join(out) + "\n"
    if a.out:
        with open(a.out, "w") as fh:
            fh.write(text)
    sys.stdout.write(text)
    return 0 if met else 1


if __name__ == "__main__":
    sys.exit(main())
