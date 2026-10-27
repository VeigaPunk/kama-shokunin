#!/usr/bin/env python3
"""Fixture mutator for case-49 stale-count audit tests.

Usage: mutate.py <fixture-repo> claim+1|cmd-noop

Applies exactly one named mutation to the fixture repo's SCORECARD.md in place
(fixture repos only; never the lane).  Prints the applied mutation.
"""
import sys

path = sys.argv[1] + "/SCORECARD.md"
kind = sys.argv[2]
text = open(path, encoding="utf-8").read()

if kind == "claim+1":
    old = "→ `43` (outside closures on record"
    new = "→ `44` (outside closures on record"
elif kind == "cmd-noop":
    old = "python3 -c \"import glob;print(len(glob.glob('corpus/lessons/*verifier-spotcheck.md')))\""
    new = "python3 -c \"print('verifier-spotcheck')\""
else:
    raise SystemExit(f"unknown mutation {kind!r}")

if text.count(old) != 1:
    raise SystemExit(f"mutation {kind}: expected exactly 1 occurrence, found {text.count(old)}")
open(path, "w", encoding="utf-8").write(text.replace(old, new))
print(f"applied={kind}")
