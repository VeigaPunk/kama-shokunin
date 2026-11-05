#!/usr/bin/env python3
"""Receipt: R1 must not change rendered() bytes over the frozen SCORECARD (all its
fence lines are column 0), and R2 verdict lines over the frozen round-86 closure."""
import importlib.util
import sys

S = "/fast/scratch/hyaku/kama-r87/EX01SelectorRepair"


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


old = load(S + "/wt/tools/round86-rendered-cells.py", "old_sel")
new = load(S + "/round87-rendered-cells.py", "new_sel")
text = open(S + "/wt/scorecard-at-freeze.md").read()
a, b = old.rendered(text), new.rendered(text)
print(f"RENDERED_DIFF old={len(a)} new={len(b)} identical={a == b}")
if a != b:
    print("RENDERED_DIFF MISMATCH — R1 changed the live rendered bytes")
body = open(S + "/wt/corpus/lessons/round-86-verifier-spotcheck.md").read()
for i, line in enumerate(body.splitlines(), 1):
    for m in new.VERDICT.finditer(line):
        tok = m.group(1)
        mark = "VERDICT-LINE" if tok in new.DISPOSITIONS else "not-a-verdict-line"
        print(f"R2_SCAN line {i}: token={tok!r} {mark}")
print("disposition_of(round-86 body):", new.disposition_of(body))
sys.exit(0 if a == b else 1)
