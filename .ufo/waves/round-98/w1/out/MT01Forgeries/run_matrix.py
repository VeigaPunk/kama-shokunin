#!/usr/bin/env python3
"""MT01Forgeries: run the round-98 C2 counter against MY probe mutants.

Every run is `--control` (natural pass only), so no burners and no clock-based
decision. Receipts land in out/receipts/<run>.out; the survive/catch matrix is
built from the counter's own ROUTER_BUDGET98_CONTROL and ROUTER_BUDGET98_CELL
lines.
"""
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
PROBE = REPO / "tools/kama-probe.sh"
MUT = OUT / "mutants"

RUNS = [
    # name, probe, cells, expect, expect_cell
    ("pristine-new", PROBE, "new", "survived", None),
    ("A_kv2x-legacy", MUT / "A_kv2x.sh", "legacy", "survived", None),
    ("A_kv2x-new", MUT / "A_kv2x.sh", "new", "survived", None),
    ("B_flat6-legacy", MUT / "B_flat6.sh", "legacy", "survived", None),
    ("B_flat6-new", MUT / "B_flat6.sh", "new", "caught", "W15-700k-nd4"),
    ("C_maxmeta100-legacy", MUT / "C_maxmeta100.sh", "legacy", "survived", None),
    ("C_maxmeta100-new", MUT / "C_maxmeta100.sh", "new", "caught", "W16-maxmeta"),
    ("D_minus1-legacy", MUT / "D_minus1.sh", "legacy", "survived", None),
    ("D_minus1-new-W14", MUT / "D_minus1.sh", "new", "caught", "W14-900k-nd1"),
    ("D_minus1-new-W17", MUT / "D_minus1.sh", "new", "caught", "W17-833333-nd1"),
    ("E_plus1-legacy", MUT / "E_plus1.sh", "legacy", "survived", None),
    ("E_plus1-r97set", MUT / "E_plus1.sh", "r97set", "survived", None),
    ("E_plus1-new-W18", MUT / "E_plus1.sh", "new", "caught", "W18-800k-nd1"),
    ("E_plus1-new-W19", MUT / "E_plus1.sh", "new", "caught", "W19-520k-nd4"),
    ("F_plus2-legacy-W11", MUT / "F_plus2.sh", "legacy", "caught", "W11-700k"),
    ("F_plus2-new-W18", MUT / "F_plus2.sh", "new", "caught", "W18-800k-nd1"),
    ("F_plus2-new-W19", MUT / "F_plus2.sh", "new", "caught", "W19-520k-nd4"),
]

CTRL = re.compile(r"^ROUTER_BUDGET98_CONTROL .*$")
CELL = re.compile(r"^ROUTER_BUDGET98_CELL (\S+) (\S+) ok=(\d+) (.*)$")


def main() -> int:
    receipts = OUT / "receipts"
    receipts.mkdir(parents=True, exist_ok=True)
    workroot = SCRATCH / "work"
    workroot.mkdir(parents=True, exist_ok=True)
    matrix = {"probe_sha256": None, "runs": {}}
    import hashlib
    matrix["probe_sha256"] = hashlib.sha256(PROBE.read_bytes()).hexdigest()
    for name, probe, cells, expect, cell in RUNS:
        cmd = [sys.executable, str(COUNTER), "--repo", str(REPO), "--rev", "HEAD",
               "--work", str(workroot / name), "--probe-file", str(probe),
               "--cells", cells, "--control", "--expect", expect]
        if cell:
            cmd += ["--expect-cell", cell]
        t0 = time.monotonic()
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=1800)
        dt = time.monotonic() - t0
        rec = receipts / f"{name}.out"
        rec.write_text(f"$ {' '.join(cmd)}\n\n--- stdout ---\n{p.stdout}\n"
                       f"--- stderr ---\n{p.stderr}\n# exit={p.returncode} wall={dt:.1f}s\n")
        ctrl = [ln for ln in p.stdout.splitlines() if CTRL.match(ln)]
        cells_out = {}
        for ln in p.stdout.splitlines():
            m = CELL.match(ln)
            if m:
                cells_out[m.group(2)] = {"ok": int(m.group(3)), "detail": m.group(4)}
        summary = ctrl[-1] if ctrl else "(no CONTROL line)"
        matrix["runs"][name] = {
            "cmd": cmd, "exit": p.returncode, "wall_seconds": round(dt, 1),
            "probe": str(probe), "cells_arg": cells,
            "probe_sha256": hashlib.sha256(Path(probe).read_bytes()).hexdigest(),
            "control_line": summary, "cells": cells_out,
            "receipt": str(rec),
        }
        print(f"RUN {name} exit={p.returncode} wall={dt:.1f}s", flush=True)
        print(f"  {summary}", flush=True)
        for cid, c in sorted(cells_out.items()):
            if c["ok"] == 0:
                print(f"  RED {cid} {c['detail']}", flush=True)
    (OUT / "matrix.json").write_text(json.dumps(matrix, indent=2) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
