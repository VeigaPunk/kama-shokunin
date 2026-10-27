#!/usr/bin/env python3
"""anchor-quote-check.py - check one corpus/SOURCES.md row's located quote against the
source bytes at the line/range its own `anchor` cell names (KQ45).

Question: does the quote a SOURCES row puts in `teaches` occur inside the line or range
the row's `anchor` cell names, in the source file the row is about?

Routed: round-52 closure R1 (S505's anchor "lines 422-439" and the round-52 lesson's
"line 431" are wrong; the quote is at line 491), corpus/QUALITY.md KQ45 (a quote that sits
at a line other than the one its anchor names is a defect, corrected by an appended
superseding row). KQ45 has had no lane instrument.

Cells are resolved by header name (KQ48), never by position: the header is the last
`| id | source |` line before the row. The quote is the first quoted span of `teaches` that
occurs in the source file at all, so the anchor-critique quotes of a correction row
("lines 422-439", "line 431") are not mistaken for the located quote.

Usage:
  python3 anchor-quote-check.py --sources <SOURCES.md> --source-file <bytes> --row S505
Output (one line, exit 0 met / 1 not met / 2 unreadable):
  row=S505 quote="..." words=7 anchors=422-439 occurs_at=[491] in_anchor=False met=False
"""
import argparse
import re
import sys

HEADER_HINT = "| id | source |"


def cells(line):
    return [c.strip() for c in line.strip().strip("|").split("|")]


def row_cells(text, row):
    header = None
    for ln in text.split("\n"):
        if ln.startswith(HEADER_HINT):
            header = [c.lower() for c in cells(ln)]
    if header is None:
        raise SystemExit("could not-eval: no `| id | source |` header row")
    for ln in text.split("\n"):
        if not ln.startswith("| S"):
            continue
        cs = cells(ln)
        if not cs or cs[0] != row:
            continue
        if len(cs) != len(header):
            raise SystemExit(f"could not-eval: row {row} has {len(cs)} cells, header {len(header)}")
        return dict(zip(header, cs))
    raise SystemExit(f"could not-eval: row {row} not found")


def quotes(cell):
    return re.findall(r'[“"]([^"“”]{8,})[”"]', cell)


def anchors(cell):
    """[(lo, hi)] for `line N`, `lines N-M`, `lines N, M`, `from line N`."""
    out = []
    for m in re.finditer(r"lines?\s+(\d+)\s*(?:[–\-]\s*(\d+)|,\s*(\d+))?", cell):
        lo = int(m.group(1))
        hi = int(m.group(2) or m.group(3) or lo)
        out.append((lo, hi))
    return out


def norm(s):
    return re.sub(r"\s+", " ", s).strip()


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--sources", required=True)
    ap.add_argument("--source-file", required=True)
    ap.add_argument("--row", required=True)
    a = ap.parse_args(argv)
    try:
        text = open(a.sources, encoding="utf-8").read()
        src = open(a.source_file, encoding="utf-8", errors="replace").read().split("\n")
    except OSError as exc:
        print(f"could not-eval: {exc}")
        return 2
    cellsd = row_cells(text, a.row)
    ans = anchors(cellsd.get("anchor", ""))
    if not ans:
        print(f"could not-eval: row={a.row} names no line anchor")
        return 2
    nsrc = [norm(l) for l in src]
    q = None
    for cand in quotes(cellsd.get("teaches", "")):
        if any(norm(cand) in l for l in nsrc):
            q = cand
            break
    if q is None:
        print(f"could not-eval: row={a.row} found no quoted span that occurs in the source")
        return 2
    qn = norm(q)
    occurs = [i + 1 for i, l in enumerate(nsrc) if qn in l]
    in_anchor = any(lo <= at <= hi for at in occurs for lo, hi in ans)
    spans = ",".join(f"{lo}-{hi}" if lo != hi else str(lo) for lo, hi in ans)
    print(f'row={a.row} quote="{q}" words={len(q.split())} anchors={spans} '
          f"occurs_at={occurs} in_anchor={in_anchor} met={in_anchor}")
    for lo, hi in ans:
        print(f"detail: anchor {lo}-{hi}: {hi - lo + 1} lines, "
              f"{sum(1 for l in nsrc[lo - 1:hi] if qn in l)} hold the quote")
    return 0 if in_anchor else 1


if __name__ == "__main__":
    sys.exit(main())
