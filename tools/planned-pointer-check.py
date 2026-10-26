#!/usr/bin/env python3
"""Proposed KQ check for SCORECARD's Planned pointer (round-44 lesson, mistake b).

facts:
  pointer  the first `## Planned` section contains the contiguous sentence
           'The live plan is `### Planned (round <N>)` at the end of this file'
           (round-43's tip split it with an inserted block, leaving a prefix).
  measured every `§Round-<N> measured results` reference resolves to a line
           '### Round-<N> measured results' (optionally followed by more words) in
           the same file. (Round-44 L1 copy of seat S9Mistake's proposal, with that
           heading-prefix rule added.)

usage: planned-pointer-check.py <SCORECARD.md>   (exit 0 met, 1 not met)
"""
import re, sys

text = open(sys.argv[1], encoding="utf-8").read()
lines = text.splitlines()
bad = 0

start = next(i for i, l in enumerate(lines) if l.strip() == "## Planned")
end = next((i for i in range(start + 1, len(lines)) if lines[i].startswith("## ")), len(lines))
sect = "\n".join(lines[start:end])
m = re.search(r"The live plan is `### Planned \(round \d+\)` at the end of this file", sect)
if m:
    print(f"pointer: ok ({m.group(0)})")
else:
    bad += 1
    print("pointer: first ## Planned section lacks the contiguous "
          "'The live plan is `### Planned (round N)` at the end of this file' sentence")

refs = sorted(set(re.findall(r"§(Round-\d+ measured results)", text)))
for ref in refs:
    if any(l.strip() == f"### {ref}" or l.strip().startswith(f"### {ref} ") for l in lines):
        print(f"measured: ok (### {ref})")
    else:
        bad += 1
        print(f"measured: dangling reference §{ref} — no line '### {ref}'")
if not refs:
    print("measured: no §Round-<N> measured results references")
print("met=" + ("True" if bad == 0 else "False"))
sys.exit(0 if bad == 0 else 1)
