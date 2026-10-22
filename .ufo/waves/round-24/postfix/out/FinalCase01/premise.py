"""Read-only premise facts of kept grid fixtures, via the pinned grid's own
helpers (all object probes use --no-lazy-fetch)."""
import importlib.util
import json
import sys
from pathlib import Path

GRID = "/fast/scratch/hyaku/kama-r24/postfix/FinalCase01/clone/tests/report-audit/promisor-grid.py"
spec = importlib.util.spec_from_file_location("grid", GRID)
g = importlib.util.module_from_spec(spec)
spec.loader.exec_module(g)

root = Path(sys.argv[1])
cases = sys.argv[2:]
out = {}
for index, case in enumerate(cases):
    tmp = root / "current" / f"{index:03d}"
    lane, fleet = tmp / "lane", tmp / "fleet"
    out[case] = {
        "dir": str(tmp),
        "lane_promisor": g.promisor_facts(lane),
        "fleet_promisor": g.promisor_facts(fleet),
        "lane_missing": g.missing_objects(lane, "refs/heads/master"),
        "fleet_missing": g.missing_objects(fleet, "HEAD"),
        "fake_present": g.object_exists(lane, g.FAKE) or g.object_exists(fleet, g.FAKE),
        "lane_objects": len(g.object_inventory(lane)),
        "fleet_objects": len(g.object_inventory(fleet)),
        "lane_remote_url": g.git(lane, "config", "--get", "remote.origin.url", check=False).strip(),
        "absent_remote_exists": (tmp / "absent-remote.git").exists(),
        "lane_tip": g.git(lane, "rev-parse", "refs/heads/master").strip(),
        "lane_tip_in_fleet": g.object_exists(fleet, g.git(lane, "rev-parse", "refs/heads/master").strip()),
    }
print(json.dumps(out, indent=1, sort_keys=True))
