#!/usr/bin/env python3
"""SN01StepFlips - which TERM of C1 check 16 fails at the perfect-M1 clone?

Runs check 16's own expression term by term against the perfect-M1 clone's files, and then
shows the one failing term depends only on the FROZEN budget counter's docstring bytes.
"""
import re
import subprocess
import sys
from pathlib import Path

CLONE = Path(sys.argv[1]).resolve()
REV = sys.argv[2]
WORDS = {"zero": 0, "one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6,
         "seven": 7, "eight": 8, "nine": 9}


def show(repo: Path, rev: str, path: str):
    p = subprocess.run(["git", "-C", str(repo), "show", f"{rev}:{path}"], capture_output=True)
    return p.stdout.decode("utf-8", "replace") if p.returncode == 0 else None


def docstring(text: str) -> str:
    parts = text.split('"""')
    return parts[1] if len(parts) >= 3 else ""


skill = show(CLONE, REV, "SKILL.md")
score = show(CLONE, REV, "SCORECARD.md")
rb = show(CLONE, REV, "tools/round98-router-budget.py")


def section(text, heading):
    lines = (text or "").splitlines()
    start = next((i for i, l in enumerate(lines) if l.startswith(heading)), None)
    if start is None:
        return None
    out = []
    for l in lines[start + 1:]:
        if l.startswith("### ") or l.startswith("## "):
            break
        out.append(l)
    return out


depth = next((l for l in score.splitlines() if l.startswith("| depth |")), "")
sec97 = "\n".join(section(skill, "### Round 97 correction") or [])
rdoc = docstring(rb or "")

new_cells, mutants = [], []
mm = re.search(r"NEW_CELLS = \{(.*?)\}", rb, re.S)
if mm:
    new_cells = re.findall(r'"(W\d\d-[^"]+)"', mm.group(1))
mm = re.search(r"MUTANTS = \{(.*?)\n\}", rb, re.S)
if mm:
    mutants = re.findall(r'^\s{4}"(\w+)":', mm.group(1), re.M)

depth_forgeries = re.search(r"(\w+) graded probe forgeries", depth)
skill_variants = re.search(r"(\w+) probe variants", sec97)
doc_cells = re.search(r"adds (\w+) cells", rdoc)

terms = [
    ("len(new_cells) == 6", len(new_cells) == 6, f"len(new_cells)={len(new_cells)}"),
    ("len(mutants) == 5", len(mutants) == 5, f"len(mutants)={len(mutants)}"),
    ("depth_forgeries present", bool(depth_forgeries),
     repr(depth_forgeries.group(0)) if depth_forgeries else "none"),
    ("WORDS[depth word] == 5",
     bool(depth_forgeries) and WORDS.get(depth_forgeries.group(1).lower()) == len(mutants),
     f"{depth_forgeries.group(1) if depth_forgeries else None} -> "
     f"{WORDS.get(depth_forgeries.group(1).lower()) if depth_forgeries else None} vs {len(mutants)}"),
    ("skill_variants present", bool(skill_variants),
     repr(skill_variants.group(0)) if skill_variants else "none"),
    ("WORDS[skill word] == 5",
     bool(skill_variants) and WORDS.get(skill_variants.group(1).lower()) == len(mutants),
     f"{skill_variants.group(1) if skill_variants else None} -> "
     f"{WORDS.get(skill_variants.group(1).lower()) if skill_variants else None} vs {len(mutants)}"),
    ("doc_cells present", bool(doc_cells), repr(doc_cells.group(0)) if doc_cells else "none"),
    ("WORDS[doc word] == len(new_cells)",
     bool(doc_cells) and WORDS.get(doc_cells.group(1).lower()) == len(new_cells),
     f"{doc_cells.group(1) if doc_cells else None} -> "
     f"{WORDS.get(doc_cells.group(1).lower()) if doc_cells else None} vs {len(new_cells)}"),
    ("'cells=19' in rdoc", "cells=19" in rdoc, repr("cells=19" in rdoc)),
    ("all new cells named in depth", all(w in depth for w in new_cells),
     str([w for w in new_cells if w not in depth])),
    ("all new cells named in sec97", all(w in sec97 for w in new_cells),
     str([w for w in new_cells if w not in sec97])),
    ("S620 in sec97", "S620" in sec97, ""),
    ("S621 in sec97", "S621" in sec97, ""),
]
print(f"{'term':<40} {'ok':<6} detail")
print("-" * 100)
fails = 0
for name, ok, detail in terms:
    if not ok:
        fails += 1
    print(f"{name:<40} {str(ok):<6} {detail}")
print()
print("failing terms:", fails)
print()
print("The failing term's inputs come ONLY from rb (the frozen budget counter):")
print("  rdoc = tools/round98-router-budget.py docstring")
print("  new_cells = NEW_CELLS parsed from the same file")
print("  => SKILL.md / SCORECARD.md edits cannot change it; only the frozen counter's bytes can.")
