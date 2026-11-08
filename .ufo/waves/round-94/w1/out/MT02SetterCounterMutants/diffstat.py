#!/usr/bin/env python3
"""Per-mutant edit footprint: changed-line counts and the edited source lines."""
import difflib
from pathlib import Path

OUT = Path(__file__).resolve().parent
base = (OUT / "counter.M2.py").read_text().splitlines()
print("mutant\tchanged_lines\t+/-\tcontext")
for p in sorted((OUT / "mutants").glob("m*.py")):
    mut = p.read_text().splitlines()
    sm = difflib.SequenceMatcher(None, base, mut, autojunk=False)
    ops = [o for o in sm.get_opcodes() if o[0] != "equal"]
    removed = sum(o[2] - o[1] for o in ops)
    added = sum(o[4] - o[3] for o in ops)
    ctx = "; ".join(f"{o[0]} base:{o[1]+1}-{o[2]} mut:{o[3]+1}-{o[4]}" for o in ops)
    print(f"{p.stem}\t{removed+added}\t+{added}/-{removed}\t{ctx}")
