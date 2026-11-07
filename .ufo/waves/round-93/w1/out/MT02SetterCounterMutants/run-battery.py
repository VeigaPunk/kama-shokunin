#!/usr/bin/env python3
"""Run the committed C2 battery (points-at-mutant copy) against every mutant.

- cwd is the lane root so the battery's `--repo .` / `.ufo/...` paths resolve as committed.
- C2_COUNTER selects the counter file under test.
- Each battery invocation gets its own scratch subdir; receipts land in logs/<id>.out.
"""
import os
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

LANE = Path("/home/vgpnk/Projects/shokunin/kama-shokunin")
OUT = LANE / ".ufo/waves/round-93/w1/out/MT02SetterCounterMutants"
SCR = Path("/fast/scratch/hyaku/kama-r93/MT02SetterCounterMutants")
ARCHIVE = SCR / "b12177.tar.gz"
BATTERY = OUT / "c2-forgeries-MT02.py"
BAT = SCR / "bat"
BAT.mkdir(parents=True, exist_ok=True)

ids = [p.stem for p in sorted((OUT / "mutants").glob("*.py"))]
if len(sys.argv) > 1:
    ids = [x[:-3] if x.endswith(".py") else x for x in sys.argv[1:]]
jobs = int(os.environ.get("MT02_JOBS", "4"))


def run(mid):
    env = dict(os.environ, C2_COUNTER=str(OUT / f"mutants/{mid}.py"), TMPDIR=str(SCR))
    t0 = time.time()
    p = subprocess.run([sys.executable, str(BATTERY), str(BAT / mid), str(ARCHIVE)],
                       cwd=str(LANE), env=env, capture_output=True, text=True)
    dt = time.time() - t0
    log = OUT / f"logs/{mid}.out"
    log.write_text(f"# cmd: C2_COUNTER={OUT}/mutants/{mid}.py python3 {BATTERY} {BAT/mid} {ARCHIVE}  (cwd={LANE})\n"
                   f"# exit={p.returncode} wall={dt:.2f}s\n" + p.stdout + ("\n# stderr:\n" + p.stderr if p.stderr else ""))
    return mid, p.returncode, dt, p.stdout, p.stderr


results = {}
with ThreadPoolExecutor(max_workers=jobs) as ex:
    for mid, rc, dt, out, err in ex.map(run, ids):
        results[mid] = (rc, dt, out, err)
        print(f"{mid:32s} rc={rc} {dt:6.2f}s", flush=True)

print("done", len(results))
