#!/usr/bin/env python3
"""Discrimination control for PG18-missing-fleet-report-plain.

The graded cell's refusal must be caused by the MISSING REQUIRED REPORT
OBJECT, not by a blanket missing-object precondition (oracle-amendment-1
prospective_expected[1..3]).  This control rebuilds the SAME fixture family
with the removal switched off (report object PRESENT) and runs the same
pinned auditor against it.

The input state is DELIBERATELY DIFFERENT from the graded cell (the report
blob exists here and is absent there).  It is a discrimination experiment,
not a twin equality comparison and not a grid cell.
"""
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path("/fast/scratch/hyaku/kama-r24/postfix/FinalCase18")
CLONE = ROOT / "clone"
GRID = CLONE / "tests/report-audit/promisor-grid.py"
AUDIT = CLONE / "tools/report-landing-audit.py"
WORK = ROOT / "tmp-control"

spec = importlib.util.spec_from_file_location("promisor_grid", GRID)
grid = importlib.util.module_from_spec(spec)
spec.loader.exec_module(grid)

WORK.mkdir(parents=True, exist_ok=True)
built = grid.build(str(WORK), str(WORK / "case"))
lane, fleet = built["lane"], built["fleet"]
shas = built["shas"]
before = {"lane": grid.object_inventory(lane), "fleet": grid.object_inventory(fleet)}
argv = [sys.executable, str(AUDIT), "--lane-repo", str(lane),
        "--fleet-repo", str(fleet), "--rounds", "1", "--json", "--no-errata"]
proc = subprocess.run(argv, capture_output=True, env=grid.env(), cwd=str(WORK),
                      timeout=grid.TIMEOUT)
after = {"lane": grid.object_inventory(lane), "fleet": grid.object_inventory(fleet)}
out = proc.stdout.decode(errors="replace")
err = proc.stderr.decode(errors="replace")
doc = None
try:
    doc = json.loads(out)
except ValueError:
    pass
print(json.dumps({
    "control": "PG18 fixture family WITHOUT the report-blob removal "
               "(DIFFERENT INPUT STATE: report object present)",
    "auditor_sha256": hashlib.sha256(AUDIT.read_bytes()).hexdigest(),
    "argv": argv,
    "exit": proc.returncode,
    "stdout_len": len(out),
    "stdout_is_json": doc is not None,
    "stderr_full": err,
    "defects": None if doc is None else [
        (d.get("kind"), d.get("token")) for r in doc.get("results", [])
        for d in r.get("defects", [])],
    "report_blob_oid": shas["report_blob"],
    "report_blob_present": grid.object_exists(fleet, shas["report_blob"]),
    "objects_acquired": {k: sorted(after[k] - before[k]) for k in after},
    "fleet_promisor_backed": grid.promisor_facts(fleet)["promisor_backed"],
}, indent=1, sort_keys=True))
