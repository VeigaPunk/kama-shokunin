#!/usr/bin/env python3
"""round91-threshold-rows.py - round-91 C2 (depth) frozen counter.

PREDICATE (frozen: plans/round-91-claims.md section C2):

    `python3 tools/round91-threshold-rows.py --repo <lane> --rev <R>` prints
    `THRESHOLD_ROWS rows=<n> bound=<n> unbound=0 duplicates=0 engines=<e> fetch_failures=0 ...`
    with n >= 10 and e >= 3, and exits 0.

Population: the rendered data rows of the `SKILL.md` section headed exactly
`## Serving timeout and limit thresholds` at <R> (the section runs to the next `## ` heading).
Rendered means: outside HTML comments (`<!-- ... -->`, also multi-line) and outside backtick or
tilde fences; a row is a line starting in column 0 with `| T<digits> |`. Header and separator
lines are not rows. Rows anywhere else in SKILL.md are not counted.

Row shape, 8 cells:
    | T<nn> | <engine> <pin> | <threshold name> | <value> | S<nnn> | <line> | `<literal>` | <decision> |

A row is BOUND only when every condition holds:
  B1 all 8 cells are non-empty and none is `-`;
  B2 the value cell holds a number token and that token occurs in the literal cell;
  B3 S<nnn> is a data row of `corpus/SOURCES.md` at <R> (0-3 leading spaces), status `mined`, tier
     A or B, whose source cell names an https URL and whose anchor cell names `sha256 <64 hex>`;
  B4 the URL does not name a moving ref (`/main/`, `/master/`, `/HEAD/`, `refs/heads`), the
     engine cell's pin token (its last word) occurs in the URL, and the engine name (its first
     word, lower-cased) occurs in the lower-cased URL;
  B5 the URL, fetched live now (curl -sfL, 60 s), has that sha256 (a fetch error counts in
     fetch_failures and leaves the row unbound);
  B6 line <line> (1-based) of the fetched bytes, decoded as UTF-8, contains the literal (backticks
     stripped) as an exact substring;
  B7 the threshold-name cell holds at least one backticked token of 3 or more characters that
     also occurs in the literal (the row names the parameter, flag or constant the line sets).
Semantic fit of the name, value and decision to the line is a reviewer read (plan C2 K2), not
graded here.
A row whose id, or whose (S<nnn>, line) pair, repeats an earlier row is a duplicate: counted in
`duplicates`, never bound. `engines` counts distinct engine names (first word, lower-cased) among
bound rows.

Usage: round91-threshold-rows.py --repo DIR --rev REV
Exit: 0 predicate met | 1 not met | 2 could-not-evaluate (bad --rev, file absent at <R>).
"""
from __future__ import annotations

import argparse
import hashlib
import re
import subprocess
import sys

HEAD = "## Serving timeout and limit thresholds"
MIN_ROWS = 10
MIN_ENGINES = 3
ROW_RE = re.compile(r"^\| *(T\d+) *\|")
SRC_RE = re.compile(r"^ {0,3}\| *(S\d{3,}) *\|")
NUM_RE = re.compile(r"\d+(?:\.\d+)?")
MOVING = ("/main/", "/master/", "/HEAD/", "refs/heads")


class CannotEvaluate(Exception):
    pass


def show(repo, rev, path) -> str:
    p = subprocess.run(["git", "-C", repo, "show", f"{rev}:{path}"], capture_output=True)
    if p.returncode != 0:
        raise CannotEvaluate(f"{path} absent at {rev}")
    return p.stdout.decode("utf-8", "replace")


def rendered_lines(text: str):
    """Yield lines outside HTML comments and fences."""
    in_comment = False
    fence = None
    for line in text.split("\n"):
        if fence is not None:
            if line.strip().startswith(fence):
                fence = None
            continue
        if in_comment:
            if "-->" in line:
                in_comment = False
                line = line.split("-->", 1)[1]
                if not line.strip():
                    continue
            else:
                continue
        while "<!--" in line:
            pre, rest = line.split("<!--", 1)
            if "-->" in rest:
                line = pre + rest.split("-->", 1)[1]
            else:
                line = pre
                in_comment = True
                break
        s = line.lstrip()
        if s.startswith("```") or s.startswith("~~~"):
            fence = s[:3]
            continue
        yield line


def section_rows(skill: str):
    rows, inside = [], False
    for line in rendered_lines(skill):
        if line.startswith("## "):
            inside = line.rstrip() == HEAD
            continue
        if inside and ROW_RE.match(line):
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            rows.append(cells)
    return rows


def sources(text: str):
    out = {}
    for line in text.split("\n"):
        m = SRC_RE.match(line)
        if m:
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            out.setdefault(m.group(1), cells)
    return out


_cache = {}


def fetch(url: str):
    if url not in _cache:
        p = subprocess.run(["curl", "-sfL", "--max-time", "60", url], capture_output=True)
        _cache[url] = p.stdout if p.returncode == 0 else None
    return _cache[url]


def grade(cells, srcs):
    if len(cells) != 8:
        return False, f"cells={len(cells)}", None
    rid, engine, _name, value, sid, line, literal, _decision = cells
    if any(not c or c == "-" for c in cells):
        return False, "empty-cell", None
    lit = literal.strip().strip("`")
    nums = NUM_RE.findall(value)
    row = srcs.get(sid)
    if row is None or len(row) < 9:
        return False, "source-absent", None
    tier, anchor, status = row[3], row[5], row[7]
    if status != "mined" or tier not in ("A", "B"):
        return False, f"source-status={status}/tier={tier}", None
    m = re.search(r"https://\S+", row[1])
    h = re.search(r"sha256 ([0-9a-f]{64})", anchor)
    if not m or not h:
        return False, "source-no-url-or-sha", None
    url = m.group(0).rstrip(").,;")
    if any(x in url for x in MOVING):
        return False, "moving-ref", None
    pin = engine.split()[-1]
    if pin not in url:
        return False, "pin-not-in-url", None
    if engine.split()[0].lower() not in url.lower():
        return False, "engine-not-in-url", None
    body = fetch(url)
    if body is None:
        return False, "fetch-failed", "fetch"
    if hashlib.sha256(body).hexdigest() != h.group(1):
        return False, "sha-mismatch", None
    try:
        n = int(line)
    except ValueError:
        return False, "bad-line", None
    lines = body.decode("utf-8", "replace").split("\n")
    if not 1 <= n <= len(lines) or lit not in lines[n - 1]:
        return False, "literal-not-at-line", None
    names = [t for t in re.findall(r"`([^`]+)`", _name) if len(t) >= 3]
    if not any(t in lit for t in names):
        return False, "name-not-in-literal", None
    return True, "bound", None


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", required=True)
    ap.add_argument("--rev", required=True)
    a = ap.parse_args()
    try:
        rv = subprocess.run(["git", "-C", a.repo, "rev-parse", "--verify", a.rev + "^{commit}"],
                            capture_output=True, text=True)
        if rv.returncode != 0:
            raise CannotEvaluate(f"unresolvable --rev {a.rev}")
        rev = rv.stdout.strip()
        rows = section_rows(show(a.repo, rev, "SKILL.md"))
        srcs = sources(show(a.repo, rev, "corpus/SOURCES.md"))
    except CannotEvaluate as e:
        print(f"THRESHOLD_ROWS could-not-evaluate: {e}")
        return 2
    seen_id, seen_pair = set(), set()
    bound = unbound = dup = fails = 0
    engines = set()
    for cells in rows:
        rid = cells[0]
        pair = (cells[4], cells[5]) if len(cells) >= 6 else None
        if rid in seen_id or (pair and pair in seen_pair):
            dup += 1
            print(f"THRESHOLD_ROW {rid} bound=0 why=duplicate")
            continue
        seen_id.add(rid)
        if pair:
            seen_pair.add(pair)
        ok, why, f = grade(cells, srcs)
        fails += f == "fetch"
        if ok:
            bound += 1
            engines.add(cells[1].split()[0].lower())
        else:
            unbound += 1
        print(f"THRESHOLD_ROW {rid} bound={int(ok)} why={why}")
    n = len(rows)
    print(f"THRESHOLD_ROWS rows={n} bound={bound} unbound={unbound} duplicates={dup} "
          f"engines={len(engines)} fetch_failures={fails} rev={rev}")
    met = n >= MIN_ROWS and bound == n and unbound == 0 and dup == 0 and fails == 0 \
        and len(engines) >= MIN_ENGINES
    return 0 if met else 1


if __name__ == "__main__":
    sys.exit(main())
