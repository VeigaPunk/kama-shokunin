#!/usr/bin/env python3
"""Scan corpus/QUALITY.md for live criteria rows whose last cell names no lesson file.

Usage: python3 scan-rows.py <path-to-QUALITY.md>
Live rows = table lines starting `| KQ<n>` outside fenced blocks (the `## Restored lines`
blocks at the end are fences; their restored rows are historical bytes, not live criteria).
"""
import re
import sys

path = sys.argv[1] if len(sys.argv) > 1 else "corpus/QUALITY.md"
lines = open(path, encoding="utf-8").read().split("\n")
infence = False
fencemark = None
rows = []
for n, line in enumerate(lines, 1):
    m = re.match(r"^(`{3,}|~{3,})", line)
    if m:
        if not infence:
            infence, fencemark = True, m.group(1)
        elif line.startswith(fencemark[0] * len(fencemark)):
            infence, fencemark = False, None
        continue
    if infence or not line.startswith("|"):
        continue
    cells = [c.strip() for c in line.strip().strip("|").split("|")]
    if not cells or not re.match(r"^KQ\d+", cells[0]):
        continue
    rows.append((n, cells[0], cells[-1], len(cells)))

nolesson = [r for r in rows if not re.search(r"lessons/[A-Za-z0-9._-]+\.md|round-[0-9]+[A-Za-z0-9._-]*\.md", r[2])]
print("total rows", len(rows))
print("== rows whose last cell names no lesson file ==", len(nolesson))
for n, i, c, k in nolesson:
    print(f"{n}\t{i}\tcells={k}\t{c[:220]}")

refs = sorted(set(re.findall(r"lessons/([A-Za-z0-9._-]+\.md)", "\n".join(lines))))
import os
missing = [r for r in refs if not os.path.exists(os.path.join(os.path.dirname(path), "lessons", r))]
print("lesson refs", len(refs), "missing", missing)
