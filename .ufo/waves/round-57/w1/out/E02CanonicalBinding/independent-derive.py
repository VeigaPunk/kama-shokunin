#!/usr/bin/env python3
"""independent derivation for distinct case 4: a second, deliberately different route
to the same facts, used to cross-check the prototype's canon_rows / row names /
first-working rounds without importing canon-binding.py."""
import re
import subprocess
import sys

repo, tip = sys.argv[1], sys.argv[2]
sc = subprocess.run(["git", "-C", repo, "cat-file", "-p", f"{tip}:SCORECARD.md"],
                    capture_output=True).stdout.decode()
lines = sc.split("\n")
idx = [i for i, l in enumerate(lines) if re.search(r"canonical list as of round 49\*\*", l)]
print(f"round49_headings={len(idx)} at_line={idx}")
start = idx[-1]
head = lines[start]
print(f"heading={head[:80]}")
# route A: count the contiguous pipe block that starts within 3 lines of the heading
j = start + 1
while j < len(lines) and not lines[j].startswith("|"):
    j += 1
block = []
while j < len(lines) and lines[j].startswith("|"):
    block.append(lines[j])
    j += 1
print(f"routeA_pipe_lines={len(block)} routeA_rows={len(block) - 2}")
names = [b.strip().strip("|").split("|")[0].strip() for b in block[2:]]
firsts = [re.findall(r"\d+", b.strip().strip("|").split("|")[3])[-1] for b in block[2:]]
print("routeA_names=" + ",".join(names))
print("routeA_firsts=" + ",".join(firsts))
# route B: the §Saturation prose list, a different sentence in the same document
sat = [l for l in lines if "first-working rounds" in l][0]
prose = re.findall(r"\d+", sat.split("first-working rounds")[1].split("(")[0])
print("routeB_prose_firsts=" + ",".join(prose))
print(f"agree_names_n={len(names)} agree_firsts={firsts == prose}")
print("retired_line_axes=" + ",".join(re.findall(r"\d+ axes", "\n".join(lines))[:1]))
print("retired_line_caps=" + ",".join(re.findall(r"\d+ capabilities", "\n".join(lines))[:1]))
