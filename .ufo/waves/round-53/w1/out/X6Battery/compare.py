#!/usr/bin/env python3
"""Compare round-53 build battery receipts against the round-52 measured receipts.

Verdict lines = every line except the `$ command` header and `detail:` evidence lines
(the detail lines carry pids/ports/inodes/nonces and are evidence, not verdict).
Repeated -> `<n> x <line>` so multiset changes are visible.
"""
import sys, os, re
from collections import Counter

OLD = "/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-52/measured"
NEW = "/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-53/w1/out/X6Battery"

VOLATILE = [
    (re.compile(r"/fast/scratch/hyaku/kama-r5[23]/[A-Za-z0-9]+/meas[^/\s]*"), "<SCRATCH>"),
    (re.compile(r"\b\d+\.\d+ s\b"), "<S>"),
    (re.compile(r"started=\S+"), "started=<TS>"),
]

def verdict_lines(path):
    out = []
    with open(path, "r", errors="replace") as fh:
        for line in fh:
            line = line.rstrip("\n")
            if line.startswith("$ "):
                continue
            if line.startswith("detail:"):
                continue
            s = line
            for rx, rep in VOLATILE:
                s = rx.sub(rep, s)
            out.append(s)
    return out

def main():
    names = sys.argv[1:]
    if not names:
        names = sorted(f[:-4] for f in os.listdir(OLD)
                       if f.endswith(".out") and not f.endswith("-build.out"))
    for n in names:
        o = os.path.join(OLD, n + ".out")
        w = os.path.join(NEW, n + ".out")
        if not os.path.exists(o):
            print(f"## {n}: NO ROUND-52 RECEIPT (new in round 53)")
            if os.path.exists(w):
                for l in verdict_lines(w):
                    print(f"   + {l}")
            continue
        if not os.path.exists(w):
            print(f"## {n}: NO BUILD RECEIPT")
            continue
        co, cw = Counter(verdict_lines(o)), Counter(verdict_lines(w))
        if co == cw:
            print(f"## {n}: IDENTICAL verdict ({sum(co.values())} lines)")
            continue
        print(f"## {n}: DIFFERS")
        for line in sorted((co - cw).elements()):
            print(f"   - {line}")
        for line in sorted((cw - co).elements()):
            print(f"   + {line}")

main()
