#!/usr/bin/env python3
"""check-sufficiency-row.py - did a lesson carry the sufficiency family as a row with a runnable check?

Round-46 lesson sweep finding 1 (`corpus/lessons/round-46.md:87`, routed by
`corpus/lessons/round-46-verifier-spotcheck.md:139` D3): "counters prove facts, not
sufficiency" was carried in the closures of rounds 41-45 and never became a
`## Mistakes` row. The sweep proposed: a carried item that survives three closures
must be written as a row with a fail-capable check or dropped with a reason.

This check is deliberately narrow and mechanical. It reads one lesson file, finds
the `## Mistakes` table, and looks for a row whose class cell matches `sufficien`
(case-insensitive) and whose fix cell names a command that can exit nonzero
(`--check`, `exit 1`, `exit=1`, or a `.py` path). Anything less - prose in
`## Claims`/`## Gate`, a sweep paragraph, a mention in a closure - does not count:
the sweep itself proved that mentions survive without becoming rows.

Usage: check-sufficiency-row.py <lesson.md>
Output: `row=<0|1> file=<path> command=<1|0>`; exit 0 when the row exists, 1 when not.
Read-only. Stdlib only.
"""
import re
import sys

CHECK = re.compile(r"--check|exit[ =]1|\.py\b")


def mistakes_rows(text):
    lines = text.split("\n")
    start = None
    for i, ln in enumerate(lines):
        if ln.strip() == "## Mistakes":
            start = i + 1
            break
    if start is None:
        return []
    rows = []
    for ln in lines[start:]:
        if ln.startswith("## "):
            break
        if not ln.startswith("|"):
            continue
        cells = [c.strip() for c in ln.strip().strip("|").split("|")]
        if len(cells) < 3:
            continue
        if set(cells[0]) <= set("-: "):
            continue
        rows.append(cells)
    return rows


def main(argv):
    if len(argv) != 2:
        print(__doc__.strip().split("\n")[-1])
        return 2
    path = argv[1]
    try:
        with open(path, encoding="utf-8", errors="replace") as fh:
            text = fh.read()
    except OSError as exc:
        print(f"row=0 file={path} command=0 error={exc}")
        return 1
    hit = False
    has_cmd = False
    for cells in mistakes_rows(text):
        if "sufficien" in cells[0].lower():
            hit = True
            if CHECK.search(" | ".join(cells)):
                has_cmd = True
    print(f"row={int(hit)} file={path} command={int(has_cmd)}")
    return 0 if (hit and has_cmd) else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
