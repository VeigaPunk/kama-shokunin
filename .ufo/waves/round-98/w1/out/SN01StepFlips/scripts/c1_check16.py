#!/usr/bin/env python3
"""SN01StepFlips - isolate C1 check 16's docstring term.

Check 16 of tools/round98-self-assessment-audit.py is:
    doc_cells = re.search(r"adds (\\w+) cells", rdoc)
    ok = (len(new_cells) == 6 and len(mutants) == 5
          and ... and doc_cells and WORDS.get(doc_cells.group(1).lower()) == len(new_cells) ...)

`rdoc` is the docstring of tools/round98-router-budget.py, whose bytes are frozen at the
round-98 freeze commit (C2 kill rule K1). This harness evaluates check 16's own expression
against the FROZEN bytes, with every other term forced green, and shows which term is false
and whether ANY edit to SKILL.md / SCORECARD.md / SOURCES.md can change it.
"""
import re
from pathlib import Path

LANE = Path("/home/vgpnk/Projects/shokunin/kama-shokunin")
WORDS = {"zero": 0, "one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6,
         "seven": 7, "eight": 8, "nine": 9}


def docstring(text: str) -> str:
    parts = text.split('"""')
    return parts[1] if len(parts) >= 3 else ""


rb = (LANE / "tools/round98-router-budget.py").read_text()
rdoc = docstring(rb)
mm = re.search(r"NEW_CELLS = \{(.*?)\}", rb, re.S)
new_cells = re.findall(r'"(W\d\d-[^"]+)"', mm.group(1))
mm2 = re.search(r"MUTANTS = \{(.*?)\n\}", rb, re.S)
mutants = re.findall(r'^\s{4}"(\w+)":', mm2.group(1), re.M)

doc_cells = re.search(r"adds (\w+) cells", rdoc)
term_doc = bool(doc_cells) and WORDS.get(doc_cells.group(1).lower()) == len(new_cells)

print("frozen budget docstring regex 'adds (\\w+) cells' ->",
      repr(doc_cells.group(0)) if doc_cells else None)
print("  parsed word:", doc_cells.group(1) if doc_cells else None,
      "-> WORDS =", WORDS.get(doc_cells.group(1).lower()) if doc_cells else None)
print("  len(new_cells) =", len(new_cells), new_cells)
print("  check16 docstring term (WORDS[word] == len(new_cells)) ->", term_doc)
print()
print("all regex matches in the frozen docstring:",
      [m.group(0) for m in re.finditer(r"adds (\w+) cells", rdoc)])
print("'adds six cells' present:", "adds six cells" in rdoc)
print("'cells=19' present:", "cells=19" in rdoc)
print()
print("The docstring term depends ONLY on rb's bytes (the frozen budget counter).")
print("SKILL.md / SCORECARD.md / SOURCES.md edits cannot change it.")
print("check16 VERDICT at any M1 that leaves the frozen counter bytes alone:",
      "PASS" if term_doc else "MISMATCH (unconditional)")
print()
print("Counter line numbers:")
for i, line in enumerate((LANE / "tools/round98-self-assessment-audit.py").read_text().splitlines(), 1):
    if "doc_cells" in line:
        print(f"  tools/round98-self-assessment-audit.py:{i}: {line.strip()}")
for i, line in enumerate(rb.splitlines(), 1):
    if "adds two cells" in line or "adds six cells" in line:
        print(f"  tools/round98-router-budget.py:{i}: {line.strip()}")
