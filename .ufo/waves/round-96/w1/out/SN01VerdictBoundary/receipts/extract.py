#!/usr/bin/env python3
"""Extract the ROUTER_PY python block from the landed probe and instrument step counting.

Read-only against the lane repo (git show). Writes only into this seat's scratch.
"""
import hashlib
import subprocess
import sys
from pathlib import Path

LANE = Path("/home/vgpnk/Projects/shokunin/kama-shokunin")
REV = sys.argv[1] if len(sys.argv) > 1 else "HEAD"
OUT = Path(sys.argv[2]) if len(sys.argv) > 2 else Path("router_instrumented.py")

raw = subprocess.run(["git", "-C", str(LANE), "show", f"{REV}:tools/kama-probe.sh"],
                     capture_output=True, check=True).stdout
print("probe_sha256", hashlib.sha256(raw).hexdigest())

text = raw.decode("utf-8")
marker = "ROUTER_PY=$(cat <<'PY'\n"
i = text.index(marker) + len(marker)
j = text.index("\nPY\n)", i)
py = text[i:j]

# strip the module-level dispatcher (it exits at import time)
cut = py.index("try:\n    doc = json.load(open(sys.argv[1]))")
py = py[:cut]

# instrument: record the highest step count observed by any need() call
needle = """        def need(n):
            steps[0] += 1
            if steps[0] > MAX_STEPS:
                raise Unknown()"""
assert needle in py, "need() shape changed"
py = py.replace(needle, """        def need(n):
            steps[0] += 1
            _LAST[0] = steps[0]
            if steps[0] > MAX_STEPS:
                raise Unknown()""")
py = py.replace("SEEN = {}", "SEEN = {}\n_LAST = [0]")

OUT.write_text(py)
print("wrote", OUT, len(py), "bytes")
print("MAX_STEPS line:", [l for l in py.splitlines() if l.startswith("MAX_STEPS")])
