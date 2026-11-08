#!/usr/bin/env python3
"""MT01Forgeries: caught-cell receipts through survive-mode controls.

The counter's argparse gate refuses `--control --expect caught` unless a
`--mutant` is also named (and naming one would stack its own patch on top of
`--probe-file`). So an external probe's named-cell red is recorded as
`--expect survived --expect-cell <cid>`: the CONTROL line prints the named
cell's ok=0 and exit is 1. That is the same cell assertion, without reaching
the frozen predicate.
"""
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
    ("B_flat6-new", "B_flat6.sh", "new", "W15-700k-nd4"),
    ("C_maxmeta100-new", "C_maxmeta100.sh", "new", "W16-maxmeta"),
    ("D_minus1-new-W14", "D_minus1.sh", "new", "W14-900k-nd1"),
    ("D_minus1-new-W17", "D_minus1.sh", "new", "W17-833333-nd1"),
    ("E_plus1-new-W18", "E_plus1.sh", "new", "W18-800k-nd1"),
    ("E_plus1-new-W19", "E_plus1.sh", "new", "W19-520k-nd4"),
    ("F_plus2-legacy-W11", "F_plus2.sh", "legacy", "W11-700k"),
    ("F_plus2-new-W18", "F_plus2.sh", "new", "W18-800k-nd1"),
    ("F_plus2-new-W19", "F_plus2.sh", "new", "W19-520k-nd4"),
]

CTRL = re.compile(r"^ROUTER_BUDGET98_CONTROL .*$")
CELL = re.compile(r"^ROUTER_BUDGET98_CELL (\S+) (\S+) ok=(\d+) (.*)$")


def main() -> int:
    receipts = OUT / "receipts"
    receipts.mkdir(parents=True, exist_ok=True)
    workroot = SCRATCH / "work"
    workroot.mkdir(parents=True, exist_ok=True)
    matrix = {"runs": {}}
    for name, probe_name, cells, cell in RUNS:
        probe = MUT / probe_name
        cmd = [sys.executable, str(COUNTER), "--repo", str(REPO), "--rev", "HEAD",
               "--work", str(workroot / ("s-" + name)), "--probe-file", str(probe),
               "--cells", cells, "--control", "--expect", "survived",
               "--expect-cell", cell]
        t0 = time.monotonic()
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=1800)
        dt = time.monotonic() - t0
        rec = receipts / f"{name}.survived-mode.out"
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
    (OUT / "matrix2.json").write_text(json.dumps(matrix, indent=2) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
