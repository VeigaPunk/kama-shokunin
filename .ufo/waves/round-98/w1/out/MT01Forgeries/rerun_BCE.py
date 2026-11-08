#!/usr/bin/env python3
"""MT01Forgeries: final receipts for the three mutants whose bytes changed
after the first pass (B, C, E are now textually independent of the counter's
MUTANTS). Same counter invocation discipline as run_matrix/run_matrix2."""
import hashlib
import json
import re
import subprocess
import sys
import time
from pathlib import Path

OUT = Path("/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-98/w1/out/"
           "MT01Forgeries")
SCRATCH = Path("/fast/scratch/hyaku/kama-r98/MT01Forgeries")
REPO = SCRATCH / "repo"
COUNTER = REPO / "tools/round98-router-budget.py"
MUT = OUT / "mutants"

RUNS = [
    # name, probe, cells, mode(survived|caught), expect_cell
    ("B_flat6-legacy", "B_flat6.sh", "legacy", "survived", None),
    ("B_flat6-new", "B_flat6.sh", "new", "caught", "W15-700k-nd4"),
    ("C_maxmeta100-legacy", "C_maxmeta100.sh", "legacy", "survived", None),
    ("C_maxmeta100-new", "C_maxmeta100.sh", "new", "caught", "W16-maxmeta"),
    ("E_plus1-legacy", "E_plus1.sh", "legacy", "survived", None),
    ("E_plus1-r97set", "E_plus1.sh", "r97set", "survived", None),
    ("E_plus1-new-W18", "E_plus1.sh", "new", "caught", "W18-800k-nd1"),
    ("E_plus1-new-W19", "E_plus1.sh", "new", "caught", "W19-520k-nd4"),
]

CTRL = re.compile(r"^ROUTER_BUDGET98_CONTROL .*$")
CELL = re.compile(r"^ROUTER_BUDGET98_CELL (\S+) (\S+) ok=(\d+) (.*)$")


def main() -> int:
    receipts = OUT / "receipts"
    receipts.mkdir(parents=True, exist_ok=True)
    workroot = SCRATCH / "work"
    workroot.mkdir(parents=True, exist_ok=True)
    matrix = {"runs": {}}
    for name, probe_name, cells, mode, cell in RUNS:
        probe = MUT / probe_name
        cmd = [sys.executable, str(COUNTER), "--repo", str(REPO), "--rev", "HEAD",
               "--work", str(workroot / ("f-" + name)), "--probe-file", str(probe),
               "--cells", cells, "--control"]
        if mode == "caught":
            # the gate refuses --expect caught without --mutant; survived-mode still
            # prints the named cell's ok= and the caught= count.
            cmd += ["--expect", "survived"]
            if cell:
                cmd += ["--expect-cell", cell]
            rec = receipts / f"{name}.survived-mode.out"
        else:
            cmd += ["--expect", "survived"]
            rec = receipts / f"{name}.out"
        t0 = time.monotonic()
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=1800)
        dt = time.monotonic() - t0
        rec.write_text(f"$ {' '.join(cmd)}\n\n--- stdout ---\n{p.stdout}\n"
                       f"--- stderr ---\n{p.stderr}\n# exit={p.returncode} wall={dt:.1f}s\n")
        ctrl = [ln for ln in p.stdout.splitlines() if CTRL.match(ln)]
        cells_out = {}
        for ln in p.stdout.splitlines():
            m = CELL.match(ln)
            if m:
                cells_out[m.group(2)] = {"ok": int(m.group(3)), "detail": m.group(4)}
        matrix["runs"][name] = {
            "cmd": cmd, "exit": p.returncode, "wall_seconds": round(dt, 1),
            "probe_sha256": hashlib.sha256(probe.read_bytes()).hexdigest(),
            "control_line": ctrl[-1] if ctrl else "(no CONTROL line)",
            "cells": cells_out, "receipt": str(rec)}
        print(f"RUN {name} exit={p.returncode} wall={dt:.1f}s", flush=True)
        print(f"  {ctrl[-1] if ctrl else '(no CONTROL line)'}", flush=True)
        for cid, c in sorted(cells_out.items()):
            if c["ok"] == 0:
                print(f"  RED {cid} {c['detail']}", flush=True)
    (OUT / "matrix3.json").write_text(json.dumps(matrix, indent=2) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
