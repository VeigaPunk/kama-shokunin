#!/usr/bin/env python3
"""FinalCase02 probe: rebuild the exact PG02 fixture with the pinned grid's
own builder, then inspect its premise facts.  No auditor run here."""
import importlib.util
import json
import os
import subprocess
import sys
from pathlib import Path

CLONE = Path("/fast/scratch/hyaku/kama-r24/postfix/FinalCase02/clone")
GRID = CLONE / "tests/report-audit/promisor-grid.py"

spec = importlib.util.spec_from_file_location("pg", GRID)
pg = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pg)

root = Path(sys.argv[1])
tmp = Path(sys.argv[2])
tmp.mkdir(parents=True, exist_ok=True)

built = pg.c_complete_fleet_config(root, tmp)
lane, fleet = built["lane"], built["fleet"]
out = {"lane": str(lane), "fleet": str(fleet), "shas": built["shas"],
       "premise": built["premise"]}

# promisor facts per store
out["facts_lane"] = pg.promisor_facts(lane)
out["facts_fleet"] = pg.promisor_facts(fleet)

def g(repo, *args):
    p = subprocess.run(["git", "--no-lazy-fetch", "-C", str(repo), *args],
                       capture_output=True)
    return p.returncode, p.stdout.decode(errors="replace").strip(), \
        p.stderr.decode(errors="replace").strip()

# cross-store asymmetry: who holds what
out["lane_has_lane_commit"] = pg.object_exists(lane, built["shas"]["lane_commit"])
out["fleet_has_lane_commit"] = pg.object_exists(fleet, built["shas"]["lane_commit"])
out["lane_has_report_blob"] = pg.object_exists(lane, built["shas"]["report_blob"])
out["fleet_has_report_blob"] = pg.object_exists(fleet, built["shas"]["report_blob"])
out["lane_inventory_count"] = len(pg.object_inventory(lane))
out["fleet_inventory_count"] = len(pg.object_inventory(fleet))
out["lane_missing"] = pg.missing_objects(lane, "refs/heads/master")
out["fleet_missing"] = pg.missing_objects(fleet, "HEAD")
out["fleet_config"] = g(fleet, "config", "--local", "--list")
out["lane_config"] = g(lane, "config", "--local", "--list")
out["fleet_remotes"] = g(fleet, "remote", "-v")
out["report_text"] = g(fleet, "show", f"HEAD:{pg.REL}")[1]
print(json.dumps(out, indent=1, sort_keys=True))
