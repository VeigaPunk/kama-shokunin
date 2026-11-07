#!/usr/bin/env python3
"""Population/derived-reason analysis for the MT02 report (read-only).

Uses the frozen counter's own functions at M2 to enumerate:
  - arg.cpp population rows and the add_opt block arg_block() finds
  - how many long options each such block declares in its first three lines
    (mutant 07 `opts[0]` -> `opts[-1]` is only observable if > 1)
  - rows that take the non-add_opt `ex == LLAMA_EXAMPLE_X` branch
  - the candidate rows' parameter/effect/scope, to name the forgeries used.
"""
import importlib.util
import re
import sys
import tempfile
from pathlib import Path

LANE = Path("/home/vgpnk/Projects/shokunin/kama-shokunin")
OUT = LANE / ".ufo/waves/round-93/w1/out/MT02SetterCounterMutants"
SCR = Path("/fast/scratch/hyaku/kama-r93/MT02SetterCounterMutants")

spec = importlib.util.spec_from_file_location("m2", OUT / "mutants/m2-counter.py")
m2 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m2)

work = Path(tempfile.mkdtemp(prefix="mt02-an-", dir=SCR))
files, digest = m2.load_archive(work, SCR / "b12177.tar.gz")
pop = m2.population(files)
print(f"population={len(pop)} digest={digest}")

print("\n# arg.cpp population rows: arg_block option count")
multi = 0
for (rel, ln) in sorted(pop):
    if rel != "common/arg.cpp":
        continue
    lines = files[rel]
    b = m2.arg_block(lines, ln)
    if b is None:
        prev = " ".join(lines[max(0, ln - 3):ln - 1])
        mm = re.search(r"ex == (LLAMA_EXAMPLE_\w+)", prev)
        print(f"{rel}:{ln} block=NONE ex_branch={mm.group(1) if mm else '-'} line={pop[(rel, ln)].strip()[:60]!r}")
        continue
    opt, ex = b
    start = None
    for i in range(ln - 1, -1, -1):
        if "add_opt(common_arg(" in lines[i]:
            start = i
            break
    head = "\n".join(lines[start:start + 3])
    opts = re.findall(r'"(--[A-Za-z0-9][\w.-]*)"', head)
    if len(opts) > 1:
        multi += 1
    print(f"{rel}:{ln} opts={opts} ex={ex} line={pop[(rel, ln)].strip()[:60]!r}")
print(f"rows_with_multiple_long_options={multi}")

print("\n# population by file")
from collections import Counter
print(Counter(rel for rel, _ in pop))

sec = (LANE / ".ufo/waves/round-93/controls/c2-candidate-section.md").read_text()
rows = [m2.split_cells(l) for l in sec.split("\n") if m2.P_RE.match(l)]
print(f"\n# candidate rows={len(rows)}")
for c in rows:
    print(f"{c[0]} {c[1]}:{c[2]} param={c[4]} effect={c[7]} value={c[8]!r} src={c[9]}")
print(Counter((c[4], c[7]) for c in rows))
