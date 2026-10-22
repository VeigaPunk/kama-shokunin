#!/usr/bin/env python3
"""Build mutant M1: the PINNED auditor with lookup() transplanted verbatim
from the pre-commit revision ed1cc3a (the merged-bare, no canonical-merge
implementation).  The mutant lives in the seat's scratch only; the pinned
clone is not modified.
"""
import hashlib
from pathlib import Path

SCRATCH = Path("/fast/scratch/hyaku/kama-r24/postfix/FinalCase12")
cur = (SCRATCH / "clone/tools/report-landing-audit.py").read_text()
old = (SCRATCH / "pre-commit-audit.py").read_text()


def block(src, start_marker):
    i = src.index(start_marker)
    j = src.index("\ndef ", i + 10) + 1
    return i, j, src[i:j]


ci, cj, cblock = block(cur, "def lookup(stores, tokens")
oi, oj, oblock = block(old, "def lookup(stores, tokens")
assert cblock != oblock
mut = cur[:ci] + oblock + cur[cj:]
# the mutant keeps the new bare_objects() helper unused; that is fine.
p = SCRATCH / "mutant-M1-precommit-lookup.py"
p.write_text(mut, encoding="utf-8")
print("mutant", p)
print("sha256", hashlib.sha256(mut.encode()).hexdigest())
print("pinned sha256", hashlib.sha256(cur.encode()).hexdigest())
print("transplanted bytes", len(oblock), "of", len(cblock))
