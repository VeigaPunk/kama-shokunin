#!/usr/bin/env python3
"""sources-anchor-check.py - locate a SOURCES row's line-number anchor in the fetched copy.

Round 53, seat W2Quality: the check drafted as KQ96 (round-52 closure R1). A `corpus/SOURCES.md`
registry row whose `anchor` cell names line numbers of a source is admitted only when the
quote it carries is located at those lines in the copy fetched now; a row that names no line
number (the `§SECTION` form of S506-S508) is neither admitted nor rejected here and reads
`n/a`. A row whose anchor uses a form outside this grammar (a bare `path line N (declaration
`X`)`, a lane-local file at a commit) also reads `n/a` with its reason: the check never
passes a row it did not read.

Grammar (frozen here; that is the contract):
  `SYM` from line N    the first line of the fetched copy containing SYM must be N
  `SYM` lines A-B      the first line containing SYM must lie in [A, B] (a function body
                       span, not a token on every line)
  line N (the cell also says "quote"/"quoted")
                       the row's quote - the first double-quoted span of `teaches` that is
                       at least 8 characters - must be found on line N
The quote span is matched by substring, so a source that wraps the comment still locates it.

Read-only: fetches each row's URL (`github.com/<o>/<r>/blob/<ref>/<path>` is rewritten to the
raw file), writes nothing. `--copy ROW=PATH` (repeatable) compares the fetched bytes with a
committed text copy by sha256 and fails when they differ - a copy that is not the fetch is not
evidence.

Output: one `detail: row=SN anchor=... want=... got=... verdict=ok|fail|n/a` line per anchor,
then `rows=N anchors=N ok=N fail=N na=N covered_copy=N copy_mismatch=N`, then `met=True|False`.
Exit 0 met (no fail, no copy mismatch), 1 not met, 2 could not evaluate.
"""
from __future__ import annotations

import argparse
import hashlib
import re
import sys
import urllib.request

ROW = re.compile(r"^\|\s*(S\d{3,})\s*\|")
SYM_FROM = re.compile(r"`([^`]+)`[^,;]*?\bfrom line (\d+)")
SYM_LINES = re.compile(r"`([^`]+)`\s*,?\s*\blines? (\d+)\s*[-\u2013\u2014]\s*(\d+)")
BARE_LINE = re.compile(r"(?<![-\w])lines?\s+(\d+)(?![-\u2013\u2014]\d)")
QUOTE = re.compile(r'"([^"]{8,})"')
COLS = ["id", "source", "kind", "tier", "scope", "anchor", "teaches", "status", "opened",
        "recheck", "used-by"]


def parse(path):
    rows, header = {}, None
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            if not line.startswith("|"):
                continue
            m = ROW.match(line)
            if not m:
                if header is None and "| anchor |" in line:
                    header = [c.strip() for c in line.strip().strip("|").split("|")]
                continue
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            rows[m.group(1)] = dict(zip(header or COLS, cells))
    return rows


def url_of(source):
    m = re.search(r"https://\S+", source)
    if not m:
        return None
    url = re.sub(r"#L\d+$", "", m.group(0).rstrip(".,;)|"))
    m = re.match(r"https://github\.com/([^/]+)/([^/]+)/blob/([^/]+)/(.+)$", url)
    if m:  # a blob URL is an HTML page; the anchor is a claim about the file's bytes
        url = f"https://raw.githubusercontent.com/{m.group(1)}/{m.group(2)}/{m.group(3)}/{m.group(4)}"
    return url


def anchors_of(cell):
    """[(kind, sym, lo, hi, text)]; symbol forms consume their line numbers first."""
    out, used = [], []
    for m in SYM_FROM.finditer(cell):
        n = int(m.group(2))
        out.append(("sym-first", m.group(1).strip(), n, n, m.group(0)))
        used.append(m.span())
    for m in SYM_LINES.finditer(cell):
        lo, hi = sorted((int(m.group(2)), int(m.group(3))))
        out.append(("sym-range", m.group(1).strip(), lo, hi, m.group(0)))
        used.append(m.span())
    for m in BARE_LINE.finditer(cell):
        if any(a <= m.start() < b for a, b in used):
            continue
        n = int(m.group(1))
        out.append(("line", None, n, n, m.group(0)))
    return out


def judge(kind, sym, lo, hi, text, lines, quotes):
    if kind == "sym-first":
        hits = [i + 1 for i, ln in enumerate(lines) if sym in ln]
        return (bool(hits) and hits[0] == lo), hits[:3]
    if kind == "sym-range":
        hits = [i + 1 for i, ln in enumerate(lines) if sym in ln]
        return (bool(hits) and lo <= hits[0] <= hi), hits[:3]
    if not quotes:
        return None, "no-quote-in-teaches"
    hits = [i + 1 for i, ln in enumerate(lines) if any(q in ln for q in quotes)]
    return (bool(hits) and any(lo <= h <= hi for h in hits)), hits[:3]


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--sources", required=True)
    ap.add_argument("--row", action="append", default=[])
    ap.add_argument("--copy", action="append", default=[], metavar="ROW=PATH")
    ap.add_argument("--timeout", type=float, default=60.0)
    a = ap.parse_args(argv)

    rows = parse(a.sources)
    want = a.row or sorted(rows)
    copies = dict(c.rsplit("=", 1) for c in a.copy)
    fetched, n_ok, n_fail, n_na, n_copy, n_mismatch, detail = {}, 0, 0, 0, 0, 0, []
    for rid in want:
        row = rows.get(rid)
        if row is None:
            n_na += 1
            detail.append(f"row={rid} verdict=n/a reason=no-such-row")
            continue
        anc = anchors_of(row.get("anchor", ""))
        if not anc:
            n_na += 1
            detail.append(f"row={rid} anchor={row.get('anchor', '')[:70]!r} verdict=n/a "
                          f"reason=no-line-number-anchor")
            continue
        url = url_of(row.get("source", ""))
        if url is None:
            n_na += 1
            detail.append(f"row={rid} anchor={row.get('anchor', '')[:70]!r} verdict=n/a "
                          f"reason=no-fetchable-url-in-source")
            continue
        if url not in fetched:
            try:
                with urllib.request.urlopen(url, timeout=a.timeout) as fh:
                    raw = fh.read()
                fetched[url] = (raw, raw.decode("utf-8", "replace").splitlines())
            except Exception as exc:  # noqa: BLE001 - reported, never raised
                n_na += 1
                detail.append(f"row={rid} url={url} verdict=n/a "
                              f"reason=fetch:{type(exc).__name__}:{exc}")
                continue
        raw, lines = fetched[url]
        sha = hashlib.sha256(raw).hexdigest()
        if rid in copies:
            with open(copies[rid], "rb") as fh:
                csha = hashlib.sha256(fh.read()).hexdigest()
            n_copy += 1
            if csha != sha:
                n_mismatch += 1
                detail.append(f"row={rid} copy={copies[rid]} fetched={sha} copy_sha256={csha} "
                              f"verdict=fail reason=copy-differs-from-fetch")
        quoted = "quote" in row.get("anchor", "").lower()
        quotes = QUOTE.findall(row.get("teaches", "")) if quoted else []
        for kind, sym, lo, hi, text in anc:
            if kind == "line" and not quoted:
                n_na += 1
                detail.append(f"row={rid} anchor={text!r} want={lo} verdict=n/a "
                              f"reason=form-not-in-grammar url={url} sha256={sha} lines={len(lines)}")
                continue
            ok, got = judge(kind, sym, lo, hi, text, lines, quotes)
            if ok is None:
                n_na += 1
                detail.append(f"row={rid} anchor={text!r} want={lo} verdict=n/a reason={got} "
                              f"url={url} sha256={sha} lines={len(lines)}")
                continue
            n_ok += int(ok)
            n_fail += int(not ok)
            span = str(lo) if hi == lo else f"{lo}-{hi}"
            detail.append(f"row={rid} anchor={text!r} want={span} got={got} "
                          f"verdict={'ok' if ok else 'fail'} url={url} sha256={sha} lines={len(lines)}")
    met = n_fail == 0 and n_mismatch == 0
    for d in detail:
        print("detail: " + d)
    print(f"rows={len(want)} anchors={n_ok + n_fail} ok={n_ok} fail={n_fail} na={n_na} "
          f"covered_copy={n_copy} copy_mismatch={n_mismatch}")
    print(f"met={'True' if met else 'False'}")
    return 0 if met else 1


if __name__ == "__main__":
    sys.exit(main())
