#!/usr/bin/env python3
"""m20 equivalence proof: opts[0] vs opts[-1] in arg_block.

Population lines in common/arg.cpp are the only inputs to arg_block. For every
population key in common/arg.cpp, recompute the option window arg_block reads
(lines[start:min(start+3,end+1)]) and report keys whose window has more than one
distinct long option (only those can distinguish opts[0] from opts[-1]).
"""
import importlib.util
import re
from pathlib import Path

X = Path("/fast/scratch/hyaku/kama-r94/MT02SetterCounterMutants/x/llama.cpp-b12177")
COUNTER = Path("/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-94/w1/out/MT02SetterCounterMutants/counter.M2.py")
spec = importlib.util.spec_from_file_location("sw", COUNTER)
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

files = {}
for rel_dir in ("common", "tools"):
    for p in sorted((X / rel_dir).rglob("*")):
        if p.suffix in (".cpp", ".h", ".hpp"):
            rel = str(p.relative_to(X))
            files[rel] = p.read_text(errors="replace").split("\n")
pop = m.population(files)
keys = sorted(k for k in pop if k[0] == "common/arg.cpp")
print(f"population={len(pop)} arg_cpp_population={len(keys)}")

multi, none, single = [], [], 0
for f, ln in keys:
    lines = files[f]
    i = ln - 1
    start = None
    while i >= 0:
        t = lines[i]
        if "add_opt(common_arg(" in t:
            start = i
            break
        if i < ln - 1 and re.match(r"\s*\)\s*(\.set_\w+\(.*\))*\s*\)\s*;", t):
            break
        i -= 1
    if start is None:
        none.append((f, ln))
        continue
    end = None
    for j in range(ln - 1, len(lines)):
        if re.match(r"\s*\)(\.set_\w+\(.*\))*\s*\)\s*;", lines[j]) or re.search(r"\)\);\s*$", lines[j]):
            end = j
            break
    if end is None:
        none.append((f, ln))
        continue
    window = "\n".join(lines[start:min(start + 3, end + 1)])
    opts = re.findall(r'"(--[A-Za-z0-9][\w.-]*)"', window)
    if len(set(opts)) > 1:
        multi.append((f, ln, opts))
    else:
        single += 1

print(f"arg_block=None rows={len(none)}")
print(f"arg_block rows with exactly one distinct long option={single}")
print(f"arg_block rows with >1 distinct long option={len(multi)}")
for x in multi:
    print("MULTI", x)
print("verdict:", "EQUIVALENT (opts[0]==opts[-1] for every population row)"
      if not multi else "DISTINGUISHABLE")
