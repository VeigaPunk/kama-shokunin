#!/usr/bin/env python3
"""Generate the remaining v3 variants: vi (empty region cell), vj (held over D), vl (exit on unmatched)."""
import os

SRC = "/fast/scratch/hyaku/kama-r48/K1Fixture/aoa-canonical.py"
OUT = "/fast/scratch/hyaku/kama-r48/K1Fixture/var"
base = open(SRC).read()

def patch(name, old, new, count=1):
    n = base.count(old)
    assert n == count, f"{name}: anchor found {n} != {count}"
    src = base.replace(old, new)
    open(os.path.join(OUT, name + ".py"), "w").write(src)
    print(name, len(src))

patch("vi_empty_region_star",
      '    if cell == "*":\n        return WHOLE\n',
      '    if cell == "*" or cell == "":\n        return WHOLE\n')

patch("vj_held_over_d",
      "                h = sum(min(n, max(0, M[l] - K[l])) for l, n in G.items())\n",
      "                h = sum(min(n, max(0, M[l] - K[l])) for l, n in D.items())\n")

patch("vl_exit_on_unmatched",
      "                 or s[\"bad_declarations\"]) else 0\n",
      "                 or s[\"bad_declarations\"] or s[\"unmatched\"]) else 0\n")
