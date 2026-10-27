#!/usr/bin/env python3
"""Inventory integers in the SCORECARD head + `## Axes` rows that no declared
fact consumes (HASH / LINES / RUN). Read-only; prints a per-row list.

A number inside a declared fact is re-derived by the counters. A number outside
any fact is prose: nothing re-computes it, so it can go stale silently.
"""
import re
import sys

RUN = re.compile(r"run `([^`]+)` → `([^`]+)`(?: \(exit (\d+)\))?")
HASH = re.compile(r"`([^`]+)` (md5|sha256) `([0-9a-f]+)`")
LINES = re.compile(r"`([^`]+)` \((\d+) lines")


def spans(text):
    out = []
    for m in RUN.finditer(text):
        out.append(m.span())
    for m in HASH.finditer(text):
        out.append(m.span())
    for m in LINES.finditer(text):
        out.append(m.span())
    return out


def main():
    text = open(sys.argv[1]).read()
    lines = text.split("\n")
    head = []
    for l in lines:
        if l.startswith("## "):
            break
        head.append(l)
    rows = []
    in_axes = False
    for l in lines:
        if l.strip() == "## Axes":
            in_axes = True
            continue
        if in_axes:
            if l.startswith("###") or (l.startswith("## ") and l.strip() != "## Axes"):
                break
            if l.startswith("|") and not re.match(r"^\|\s*-", l) and "| Axis |" not in l:
                rows.append(l)
    cells = [r.strip().strip("|").split("|") for r in rows]
    total = 0
    for c in cells:
        if len(c) < 3:
            continue
        ax = c[0].replace("*", "").strip()
        cell = c[2]
        sp = spans(cell)
        free = []
        for m in re.finditer(r"\d+", cell):
            if any(a <= m.start() and m.end() <= b for a, b in sp):
                continue
            free.append(m.group(0))
        total += len(free)
        print(f"{ax}: unbound={len(free)} values={free}")
    # head
    ht = "\n".join(head)
    sp = spans(ht)
    free = [m.group(0) for m in re.finditer(r"\d+", ht)
            if not any(a <= m.start() and m.end() <= b for a, b in sp)]
    print(f"head: unbound={len(free)} values={free}")
    print(f"total unbound integers (head + axes rows) = {total + len(free)}")


if __name__ == "__main__":
    main()
