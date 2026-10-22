#!/usr/bin/env python3
"""FinalCase19 third probe (inspection, not a registered cell): the scoped
missing cache as the pinned auditor computes it on the PG19 fixture.

It asks the pinned tools/report-landing-audit.py itself:
  * which objects the fleet store cannot serve (missing set),
  * which of them are opaque behind the pinned root (scoped walk),
  * whether the absent fleet tip tree is the only missing id,
and it checks that the walk acquired nothing and never contacted a remote.
"""
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys

CLONE = Path("/fast/scratch/hyaku/kama-r24/postfix/FinalCase19/clone")
GRID = CLONE / "tests/report-audit/promisor-grid.py"
AUDIT = CLONE / "tools/report-landing-audit.py"
TMP = Path("/fast/scratch/hyaku/kama-r24/postfix/FinalCase19/tmp")
OUT = Path("/fast/scratch/hyaku/kama-r24/postfix/FinalCase19/out")


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


grid = load("pgrid", GRID)
audit = load("audit", AUDIT)

root = Path(grid.tempfile.mkdtemp(prefix="cache-", dir=str(TMP)))
tmp = root / "pg19"
tmp.mkdir(parents=True)
built = grid.build(root, tmp, fleet_mark="config", drop=("fleet_tip_tree",))
lane, fleet = built["lane"], built["fleet"]
shas = built["shas"]
tree_oid = shas["fleet_tip_tree"]

before = {"lane": grid.object_inventory(lane),
          "fleet": grid.object_inventory(fleet)}
fleet_root = grid.git(fleet, "rev-parse", "HEAD").strip()
lane_root = grid.git(lane, "rev-parse", "HEAD").strip()
missing, opaque = audit.missing_reachable(fleet, fleet_root)
lane_missing, lane_opaque = audit.missing_reachable(lane, lane_root)
after = {"lane": grid.object_inventory(lane),
         "fleet": grid.object_inventory(fleet)}

store = audit.build_store(fleet, fleet_root)
store_missing, store_opaque = store.missing()

result = {
    "fleet_tip_tree": tree_oid,
    "fleet_missing": sorted(missing),
    "fleet_opaque": sorted(opaque),
    "lane_missing": sorted(lane_missing),
    "lane_opaque": sorted(lane_opaque),
    "store_missing_cached": sorted(store_missing),
    "store_opaque_cached": sorted(store_opaque),
    "tip_tree_in_missing": tree_oid in missing,
    "tip_tree_in_opaque": tree_oid in opaque,
    "missing_count": len(missing),
    "objects_acquired": {k: sorted(after[k] - before[k]) for k in after},
    "fleet_objects": len(before["fleet"]),
}
# the remote the promisor mark points at must be untouched/absent
remote = grid.git(fleet, "config", "--get", "remote.origin.url").strip()
result["remote_origin_url"] = remote
result["remote_exists"] = Path(remote).exists()
shutil.rmtree(root, ignore_errors=True)
OUT.mkdir(parents=True, exist_ok=True)
(OUT / "scoped-cache-probe.json").write_text(
    json.dumps(result, indent=1, sort_keys=True) + "\n", encoding="utf-8")
print(json.dumps(result, indent=1, sort_keys=True))
