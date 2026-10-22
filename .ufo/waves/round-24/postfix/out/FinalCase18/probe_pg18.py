#!/usr/bin/env python3
"""Independent re-derivation of the PG18-missing-fleet-report-plain cell.

Builds the pinned grid's own fixture for PG18 (no grid driver, no full
grid), runs the pinned tools/report-landing-audit.py against it and records
the FULL stdout/stderr/exit plus the premise and the object inventory
before/after.  The grid keeps only a 300 character stderr tail, so the
strong identity has to be re-derived here.
"""
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path("/fast/scratch/hyaku/kama-r24/postfix/FinalCase18")
CLONE = ROOT / "clone"
GRID = CLONE / "tests/report-audit/promisor-grid.py"
AUDIT = CLONE / "tools/report-landing-audit.py"
WORK = ROOT / "tmp-probe"

spec = importlib.util.spec_from_file_location("promisor_grid", GRID)
grid = importlib.util.module_from_spec(spec)
spec.loader.exec_module(grid)

WORK.mkdir(parents=True, exist_ok=True)
case = "PG18-missing-fleet-report-plain"
built = grid.BUILDERS["c_missing_fleet_report_plain"](str(WORK), str(WORK / "case"))
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

report_blob = shas["report_blob"]
fleet_tree = shas["fleet_tip_tree"]
names_any_of = [grid.resolve_token(n, shas)
                for n in ["$report_blob", ".ufo/reports/round-1/kama.md"]]
forbidden = ["partial clone (", "promisor pack"]

facts = grid.promisor_facts(fleet)
lane_facts = grid.promisor_facts(lane)
out_doc = None
try:
    out_doc = json.loads(out)
except ValueError:
    out_doc = None

evidence = {
    "case": case,
    "clone_commit": subprocess.run(["git", "-C", str(CLONE), "rev-parse", "HEAD"],
                                   capture_output=True, text=True).stdout.strip(),
    "auditor_path": str(AUDIT),
    "auditor_sha256": hashlib.sha256(AUDIT.read_bytes()).hexdigest(),
    "grid_sha256": hashlib.sha256(GRID.read_bytes()).hexdigest(),
    "argv": argv,
    "exit": proc.returncode,
    "stdout_len": len(out),
    "stdout_is_json": out_doc is not None,
    "stdout_head": out[:400],
    "stderr_len": len(err),
    "stderr_full": err,
    "stderr_starts_cne": err.startswith("could-not-evaluate:"),
    "stderr_has_internal_error": "could-not-evaluate: internal:" in err,
    "stderr_has_traceback": "Traceback (most recent call last)" in err,
    "stderr_has_forbidden_metadata": [f for f in forbidden if f in err],
    "stderr_mentions_report_blob_oid": report_blob in err,
    "stderr_mentions_report_path": ".ufo/reports/round-1/kama.md" in err,
    "stderr_mentions_fleet_tip_tree": fleet_tree in err,
    "stderr_mentions_lane_path": str(lane) in err,
    "stderr_mentions_fleet_path": str(fleet) in err,
    "names_any_of_resolved": names_any_of,
    "names_hit": [n for n in names_any_of if n and n in err],
    "objects_acquired": {k: sorted(after[k] - before[k]) for k in after},
    "objects_lost": {k: sorted(before[k] - after[k]) for k in after},
    "report_blob_oid": report_blob,
    "fleet_tip_tree_oid": fleet_tree,
    "report_blob_present_in_fleet": grid.object_exists(fleet, report_blob),
    "fleet_missing_objects": grid.missing_objects(fleet, "HEAD"),
    "lane_missing_objects": grid.missing_objects(lane, "refs/heads/master"),
    "fleet_promisor": facts,
    "lane_promisor": lane_facts,
    "premise": built["premise"],
}
print(json.dumps(evidence, indent=1, sort_keys=True))
