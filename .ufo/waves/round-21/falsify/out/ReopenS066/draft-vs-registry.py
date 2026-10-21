#!/usr/bin/env python3
"""ReopenS066: cell-by-cell diff of the build seat's S066 draft row against the registry row at a6617149.
Usage: draft-vs-registry.py DRAFT_ROW_MD SOURCES_MD
"""
import re
import sys

NAMES = ["id", "source", "kind", "tier", "scope", "anchor", "teaches", "status", "opened", "recheck", "used_by"]


def row_cells(path):
    rows = [l for l in open(path, encoding="utf-8").read().splitlines() if re.match(r"^\|\s*S066\s*\|", l)]
    if len(rows) != 1:
        raise SystemExit(f"{path}: expected one S066 row, found {len(rows)}")
    return [c.strip() for c in rows[0].split("|")[1:-1]]


draft, reg = row_cells(sys.argv[1]), row_cells(sys.argv[2])
print(f"cells draft={len(draft)} registry={len(reg)}")
for name, a, b in zip(NAMES, draft, reg):
    print(f"{name}: {'SAME' if a == b else 'DIFF'}")
    if a != b:
        print(f"  draft    : {a}")
        print(f"  registry : {b}")
