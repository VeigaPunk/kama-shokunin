#!/usr/bin/env python3
"""FinalCase02 probe 2: run the PINNED auditor directly on the rebuilt PG02
fixture (no grid), capture exit/stdout/stderr and the object inventory
before/after."""
import hashlib
import importlib.util
import json
import subprocess
import sys
from pathlib import Path

BASE = Path("/fast/scratch/hyaku/kama-r24/postfix/FinalCase02")
CLONE = BASE / "clone"
GRID = CLONE / "tests/report-audit/promisor-grid.py"
AUDIT = CLONE / "tools/report-landing-audit.py"

spec = importlib.util.spec_from_file_location("pg", GRID)
pg = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pg)

root = Path(sys.argv[1])
tmp = Path(sys.argv[2])
built = pg.c_complete_fleet_config(root, tmp)
lane, fleet = built["lane"], built["fleet"]

before = {"lane": pg.object_inventory(lane), "fleet": pg.object_inventory(fleet)}
code, out, err, timed_out = pg.run_auditor(AUDIT, lane, fleet, tmp, False)
after = {"lane": pg.object_inventory(lane), "fleet": pg.object_inventory(fleet)}
acquired = {k: sorted(after[k] - before[k]) for k in after}
surv = pg.survivors(tmp)

doc = pg.normalise_document(out, built)
res = {
    "argv": [sys.executable, str(AUDIT), "--lane-repo", str(lane),
             "--fleet-repo", str(fleet), "--rounds", "1", "--json",
             "--no-errata"],
    "auditor_path": str(AUDIT),
    "auditor_sha256": hashlib.sha256(AUDIT.read_bytes()).hexdigest(),
    "exit": code, "timed_out": timed_out,
    "stderr": err,
    "stdout_len": len(out),
    "stdout_sha256": hashlib.sha256(out.encode()).hexdigest(),
    "objects_acquired": acquired,
    "inventory_before": {k: len(v) for k, v in before.items()},
    "inventory_after": {k: len(v) for k, v in after.items()},
    "survivors": surv,
    "normalised_document": doc,
    "premise": built["premise"],
    "lane": str(lane), "fleet": str(fleet),
    "fleet_has_lane_commit": pg.object_exists(fleet, built["shas"]["lane_commit"]),
    "lane_has_report_blob": pg.object_exists(lane, built["shas"]["report_blob"]),
}
print(json.dumps(res, indent=1, sort_keys=True))
Path(sys.argv[3]).write_text(out, encoding="utf-8")
