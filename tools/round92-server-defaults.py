#!/usr/bin/env python3
"""round92-server-defaults.py - round-92 C1 (depth) frozen counter.

PREDICATE (frozen: plans/round-92-claims.md section C1):

    `python3 tools/round92-server-defaults.py --repo <lane> --rev <R> --binary <llama-server>` prints
    `SERVER_DEFAULTS rows=<n> bound=<n> unbound=0 duplicates=0 engines=<e> fetch_failures=0
    help_checked=<h> help_disagree=0 supersedes=14 ...` with n >= 14, e >= 3 and h >= 7, and exits 0.

Population: the rendered data rows of the `SKILL.md` section headed exactly
`## Serving defaults (round 92 revision)` at <R> (the section runs to the next `## ` heading).
Rendered means outside HTML comments and backtick/tilde fences; a row is a line starting in
column 0 with `| R<digits> |`. Rows anywhere else are not counted.

Row shape, 10 cells:
  | R<nn> | <engine> <pin> | <parameter> | <flag> | <value> | S<nnn> | <line> | `<literal>` | <supersedes> | <decision> |

A row is BOUND only when every condition holds (B1-B7 are the round-91 rules, unchanged in meaning):
  B1 every cell is non-empty; only the flag cell may be `-`;
  B2 the value cell's first number token (sign kept: `-?\\d+(\\.\\d+)?`) occurs in the literal;
  B3 S<nnn> is a data row of `corpus/SOURCES.md` at <R> (0-3 leading spaces), status `mined`, tier
     A or B, whose source cell names an https URL and whose anchor cell names `sha256 <64 hex>`;
  B4 the URL names no moving ref (`/main/`, `/master/`, `/HEAD/`, `refs/heads`), the engine cell's
     pin token (last word) occurs in the URL and its engine name (first word, lower-cased) occurs in
     the lower-cased URL;
  B5 the URL fetched live now (curl -sfL, 60 s) has that sha256 (a fetch error counts in
     fetch_failures);
  B6 line <line> (1-based) of the fetched bytes contains the literal (backticks stripped);
  B7 the parameter cell holds a backticked token of 3+ characters that occurs in the literal.
KQ146 (corpus/QUALITY.md; round-91 lesson M1) — a default must be the one the binary itself uses:
  H1 a `llama.cpp` row whose flag cell is a backticked option (`-...`) is help-checked: the pinned
     binary's `--help` block for that option (the block whose first line names the option followed
     by a space, comma or line end) prints `default: <x>`, and <x> equals the value's first number
     token. A block with no `default:` or a different <x> leaves the row unbound (help_disagree).
  H2 a `llama.cpp` row whose flag cell is `-` (a derived default no option prints) binds only when its
     URL path names the server entry point (`/tools/server/`).
  H3 a `llama.cpp` row must be one of the two: a backticked option (H1) or `-` (H2).
The binary is pinned: its sha256 must be BINARY_SHA256 (llama.cpp b12177 Linux x64), else exit 2.
Supersession: the supersedes cell holds `T<nn>` tokens; `supersedes` counts the distinct T01-T14 ids
named by bound rows; the predicate needs all 14 (the round-91 table is replaced row for row).
Duplicates: a repeated R id, or a repeated (S<nnn>, line) pair, is counted in `duplicates` and never
bound. `engines` counts distinct engine names among bound rows.
Semantic fit of parameter, value and decision to the line is the non-author reviewer read (plan C1 K2).

Usage: round92-server-defaults.py --repo DIR --rev REV --binary PATH
Exit: 0 predicate met | 1 not met | 2 could-not-evaluate (bad --rev, file absent, binary pin).
"""
from __future__ import annotations

import argparse
import hashlib
import re
import subprocess
import sys

HEAD = "## Serving defaults (round 92 revision)"
BINARY_SHA256 = "ba272ee3446d9b98c9150c79667e6a8b217f25ee58ce0c6156cc96d2b5b362b0"
MIN_ROWS = 14
MIN_ENGINES = 3
MIN_HELP = 7
SUPERSEDE = {f"T{i:02d}" for i in range(1, 15)}
ROW_RE = re.compile(r"^\| *(R\d+) *\|")
SRC_RE = re.compile(r"^ {0,3}\| *(S\d{3,}) *\|")
NUM_RE = re.compile(r"-?\d+(?:\.\d+)?")
MOVING = ("/main/", "/master/", "/HEAD/", "refs/heads")


class CannotEvaluate(Exception):
    pass


def show(repo, rev, path) -> str:
    p = subprocess.run(["git", "-C", repo, "show", f"{rev}:{path}"], capture_output=True)
    if p.returncode != 0:
        raise CannotEvaluate(f"{path} absent at {rev}")
    return p.stdout.decode("utf-8", "replace")


def rendered_lines(text: str):
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
            rows.append([c.strip() for c in line.strip().strip("|").split("|")])
    return rows


def sources(text: str):
    out = {}
    for line in text.split("\n"):
        m = SRC_RE.match(line)
        if m:
            out.setdefault(m.group(1), [c.strip() for c in line.strip().strip("|").split("|")])
    return out


def help_blocks(text: str):
    blocks, cur = [], None
    for line in text.splitlines():
        if line.startswith("-"):
            cur = [line]
            blocks.append(cur)
        elif cur is not None:
            cur.append(line)
    return blocks


def help_default(blocks, flag: str):
    pat = re.compile(r"(^|[\s,])" + re.escape(flag) + r"(\s|,|$)")
    for b in blocks:
        if pat.search(b[0]):
            m = re.search(r"default:\s*(-?\d+(?:\.\d+)?)", " ".join(b))
            return m.group(1) if m else None
    return None


_cache = {}


def fetch(url: str):
    if url not in _cache:
        p = subprocess.run(["curl", "-sfL", "--max-time", "60", url], capture_output=True)
        _cache[url] = p.stdout if p.returncode == 0 else None
    return _cache[url]


def grade(cells, srcs, blocks):
    """-> (bound, why, fetch_failed, help_checked, help_disagree)"""
    if len(cells) != 10:
        return False, f"cells={len(cells)}", False, False, False
    rid, engine, name, flag, value, sid, line, literal, sup, decision = cells
    for i, c in enumerate(cells):
        if not c or (c == "-" and i != 3):
            return False, "empty-cell", False, False, False
    lit = literal.strip().strip("`")
    nums = NUM_RE.findall(value)
    if not nums or nums[0] not in lit:
        return False, "value-not-in-literal", False, False, False
    row = srcs.get(sid)
    if row is None or len(row) < 9:
        return False, "source-absent", False, False, False
    tier, anchor, status = row[3], row[5], row[7]
    if status != "mined" or tier not in ("A", "B"):
        return False, f"source-status={status}/tier={tier}", False, False, False
    m = re.search(r"https://\S+", row[1])
    h = re.search(r"sha256 ([0-9a-f]{64})", anchor)
    if not m or not h:
        return False, "source-no-url-or-sha", False, False, False
    url = m.group(0).rstrip(").,;")
    if any(x in url for x in MOVING):
        return False, "moving-ref", False, False, False
    words = engine.split()
    if words[-1] not in url:
        return False, "pin-not-in-url", False, False, False
    eng = words[0].lower()
    if eng not in url.lower():
        return False, "engine-not-in-url", False, False, False
    checked = disagree = False
    if eng == "llama.cpp":
        opts = re.findall(r"`(-[^`]+)`", flag)
        if flag == "-":
            if "/tools/server/" not in url:
                return False, "derived-default-not-entry-point", False, False, False
        elif opts:
            checked = True
            d = help_default(blocks, opts[0])
            if d is None or d != nums[0]:
                return False, f"help-default={d}", False, True, True
        else:
            return False, "llama-flag-not-option", False, False, False
    body = fetch(url)
    if body is None:
        return False, "fetch-failed", True, checked, False
    if hashlib.sha256(body).hexdigest() != h.group(1):
        return False, "sha-mismatch", False, checked, False
    try:
        n = int(line)
    except ValueError:
        return False, "bad-line", False, checked, False
    lines = body.decode("utf-8", "replace").split("\n")
    if not 1 <= n <= len(lines) or lit not in lines[n - 1]:
        return False, "literal-not-at-line", False, checked, False
    toks = [t for t in re.findall(r"`([^`]+)`", name) if len(t) >= 3]
    if not any(t in lit for t in toks):
        return False, "name-not-in-literal", False, checked, False
    return True, "bound", False, checked, False


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", required=True)
    ap.add_argument("--rev", required=True)
    ap.add_argument("--binary", required=True)
    a = ap.parse_args()
    try:
        rv = subprocess.run(["git", "-C", a.repo, "rev-parse", "--verify", a.rev + "^{commit}"],
                            capture_output=True, text=True)
        if rv.returncode != 0:
            raise CannotEvaluate(f"unresolvable --rev {a.rev}")
        rev = rv.stdout.strip()
        try:
            bsha = hashlib.sha256(open(a.binary, "rb").read()).hexdigest()
        except OSError as e:
            raise CannotEvaluate(f"binary unreadable: {e}")
        if bsha != BINARY_SHA256:
            raise CannotEvaluate(f"binary sha256 {bsha} is not the pinned {BINARY_SHA256}")
        hp = subprocess.run([a.binary, "--help"], capture_output=True, text=True, timeout=60)
        blocks = help_blocks(hp.stdout)
        if not blocks:
            raise CannotEvaluate("binary --help printed no option blocks")
        rows = section_rows(show(a.repo, rev, "SKILL.md"))
        srcs = sources(show(a.repo, rev, "corpus/SOURCES.md"))
    except CannotEvaluate as e:
        print(f"SERVER_DEFAULTS could-not-evaluate: {e}")
        return 2
    seen_id, seen_pair = set(), set()
    bound = unbound = dup = fails = hchk = hdis = 0
    engines, sup = set(), set()
    for cells in rows:
        rid = cells[0]
        pair = (cells[5], cells[6]) if len(cells) >= 7 else None
        if rid in seen_id or (pair and pair in seen_pair):
            dup += 1
            print(f"SERVER_DEFAULT {rid} bound=0 why=duplicate")
            continue
        seen_id.add(rid)
        if pair:
            seen_pair.add(pair)
        ok, why, f, c, d = grade(cells, srcs, blocks)
        fails += f
        hchk += c
        hdis += d
        if ok:
            bound += 1
            engines.add(cells[1].split()[0].lower())
            sup.update(t for t in re.findall(r"T\d{2}", cells[8]) if t in SUPERSEDE)
        else:
            unbound += 1
        print(f"SERVER_DEFAULT {rid} bound={int(ok)} help_checked={int(c)} why={why}")
    n = len(rows)
    print(f"SERVER_DEFAULTS rows={n} bound={bound} unbound={unbound} duplicates={dup} engines={len(engines)} "
          f"fetch_failures={fails} help_checked={hchk} help_disagree={hdis} supersedes={len(sup)} "
          f"binary_sha256={bsha} rev={rev}")
    met = (n >= MIN_ROWS and bound == n and unbound == 0 and dup == 0 and fails == 0
           and len(engines) >= MIN_ENGINES and hchk >= MIN_HELP and hdis == 0 and len(sup) == len(SUPERSEDE))
    return 0 if met else 1


if __name__ == "__main__":
    sys.exit(main())
