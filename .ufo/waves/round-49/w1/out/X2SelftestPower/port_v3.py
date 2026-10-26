#!/usr/bin/env python3
"""Port the two round-49 (v4) selftest cases, verbatim, into the v3 tool at
438127bc01ff3b99f98468549d58046f932490ef. Prints the diff and writes v3-ported.py."""
import difflib
import sys

V3 = "/fast/scratch/hyaku/kama-r49/X2SelftestPower/v3.py"
V4 = "/fast/scratch/hyaku/kama-r49/X2SelftestPower/v4-74558c71.py"
OUT = "/fast/scratch/hyaku/kama-r49/X2SelftestPower/v3-ported.py"

v3 = open(V3, encoding="utf-8").read()
v4 = open(V4, encoding="utf-8").read()

start = v4.index("    def t_launder_through_head():")
end = v4.index("    for name, fn in [", start)
block = v4[start:end]
assert "t_binding_v4" in block and block.count("    def t_") == 2, block[:200]

anchor = "    for name, fn in ["
assert v3.count(anchor) == 1
patched = v3.replace(anchor, block + anchor, 1)
old_reg = '                     ("preamble-graded", t_preamble_graded)]:'
new_reg = ('                     ("preamble-graded", t_preamble_graded),\n'
           '                     ("launder-through-head", t_launder_through_head), ("binding-v4", t_binding_v4)]:')
assert patched.count(old_reg) == 1
patched = patched.replace(old_reg, new_reg, 1)

open(OUT, "w", encoding="utf-8").write(patched)
diff = difflib.unified_diff(v3.splitlines(True), patched.splitlines(True),
                            "a/tools/append-only-audit.py@438127bc", "b/tools/append-only-audit.py@438127bc+2cases")
sys.stdout.write("".join(diff))
