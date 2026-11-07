#!/usr/bin/env python3
"""Round-93 C1 pre-freeze control battery (run from the lane root).

P0  the candidate drafted before the freeze (controls/c1-candidate-probe.sh): expected exit 0 cells
    (printed probe=override, so it can never meet the predicate itself).
F1  base probe + fail-closed: an undecided candidate counts as bad -> expected P02 fails (harm).
F2  candidate keyed by the path string instead of file identity -> expected R05 fails.
F3  base probe with a fresh 4 s deadline per file, no memo -> expected R03/R04 fail (8 s kill).
F4  base probe that checks only the first 8 candidates and grades on those -> expected P02 fails.
Usage: python3 .ufo/waves/round-93/controls/c1-forgeries.py <scratch>
"""
import re
import subprocess
import sys
from pathlib import Path

BASE = "5af794958b0fc08f574aa2e67650282269549b02"
C = Path(".ufo/waves/round-93/controls")
scratch = Path(sys.argv[1])
scratch.mkdir(parents=True, exist_ok=True)
base = subprocess.run(["git", "show", f"{BASE}:tools/kama-probe.sh"], capture_output=True, check=True).stdout.decode()
cand = (C / "c1-candidate-probe.sh").read_text()


def sub(text, old, new):
    assert text.count(old) == 1, old
    return text.replace(old, new)


forg = {
    "P0": (cand, "mismatches=0"),
    "F1": (sub(base, "missing|invalid) nbad=", "missing|invalid|-) nbad="), "P02-slow-then-ok ok=0"),
    "F2": (sub(cand, "key = (st.st_dev, st.st_ino, st.st_size, st.st_mtime_ns)", "key = path"), "R05-slow-aliases ok=0"),
    "F3": (sub(base, "def gguf_state(path):\n    try:",
               "def gguf_state(path):\n    global DEADLINE\n    DEADLINE = time.monotonic() + 4.0\n    try:"),
           "R04-slow-x2048 ok=0"),
    "F4": (sub(sub(base, '"${cand[@]}")', '"${cand[@]:0:8}")'),
               'if [ "$nbad" -lt "$ncand" ]', 'if [ "$nbad" -lt "$(( ncand < 8 ? ncand : 8 ))" ]'),
           "P02-slow-then-ok ok=0"),
}
fails = 0
for name, (text, want) in forg.items():
    pf = scratch / f"{name}.sh"
    pf.write_text(text)
    p = subprocess.run([sys.executable, "tools/round93-router-repeat.py", "--repo", ".", "--rev", BASE,
                        "--work", str(scratch / name), "--probe-file", str(pf)], capture_output=True, text=True)
    out = p.stdout
    summary = [l for l in out.splitlines() if l.startswith("ROUTER_REPEAT ")]
    got = want in out and (name != "P0" or p.returncode == 0 and "mismatches=0 positive_mismatches=0 probe=override" in out)
    if name != "P0":
        got = got and p.returncode == 1
    fails += 0 if got else 1
    print(f"C1_CONTROL {name} as_expected={int(got)} rc={p.returncode} want={want!r}")
    for l in out.splitlines():
        print(f"  {l}")
print(f"C1_CONTROLS total={len(forg)} as_expected={len(forg) - fails}")
sys.exit(0 if fails == 0 else 1)
