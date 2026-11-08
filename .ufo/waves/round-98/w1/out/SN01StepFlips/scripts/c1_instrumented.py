#!/usr/bin/env python3
"""SN01StepFlips - instrument C1's checks so each one reports PASS/FAIL with its reason.

Runs the frozen counter's own code with a patched `mismatches` accumulator: the counter is
copied into the scratch dir and every `mismatches += 1` is replaced by a recording call, so
the per-check outcome and the failing term are visible. The frozen counter file in the lane is
never modified.
"""
import os
import re
import subprocess
import sys
from pathlib import Path

LANE = Path("/home/vgpnk/Projects/shokunin/kama-shokunin")
SRC = LANE / "tools/round98-self-assessment-audit.py"
work = Path(sys.argv[1]).resolve()
work.mkdir(parents=True, exist_ok=True)
dst = work / "c1_instrumented.py"

text = SRC.read_text()

# label each check block by the comment that introduces it
lines = text.splitlines()
out = []
label = "?"
counter = 0
for ln in lines:
    m = re.match(r"\s*#\s*(\d+(?:-\d+)?)\s*[:.]?\s*(.*)", ln)
    if m and "checks += 1" not in ln:
        label = f"check{m.group(1)}: {m.group(2).strip()[:60]}"
    if "checks += 1" in ln:
        counter += 1
        out.append(ln)
        out.append(f"    _CK.append([{counter}, {label!r}, 0, ''])")
        continue
    if "mismatches += 1" in ln:
        indent = ln[:len(ln) - len(ln.lstrip())]
        out.append(f"{indent}_CK[-1][2] += 1")
        out.append(f"{indent}_CK[-1][3] = _CTX")
        continue
    out.append(ln)

body = "\n".join(out)
# capture a context string for each check
body = body.replace("    checks = 0\n    mismatches = 0\n",
                    "    checks = 0\n    mismatches = 0\n    _CTX = ''\n")
body = body.replace("    meta = hashlib.sha256(observed.encode()).hexdigest()",
                    "    for _c in _CK:\n"
                    "        print(f'C1CHECK n={_c[0]:<3} mismatches={_c[2]} {_c[1]}')\n"
                    "    meta = hashlib.sha256(observed.encode()).hexdigest()")
body = body.replace("from pathlib import Path\n",
                    "from pathlib import Path\n\n_CK = []\n")
# capture the failing term by wrapping each boolean term: record the false ones
body = body.replace("    if not ok:\n        mismatches += 1\n",
                    "    if not ok:\n        _CTX = 'ok-term false'\n")
dst.write_text(body)

rev = sys.argv[2] if len(sys.argv) > 2 else "HEAD"
p = subprocess.run([sys.executable, str(dst), "--repo", os.environ.get("REPO", str(LANE)), "--rev", rev],
                   capture_output=True, text=True)
print(p.stdout)
print(p.stderr[-2000:] if p.stderr else "")
print("exit=", p.returncode)
