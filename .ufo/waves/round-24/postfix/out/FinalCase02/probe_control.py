#!/usr/bin/env python3
"""FinalCase02 discrimination control (NOT a graded cell): same builder
family and the same fleet promisor marking as PG02, but the report also
cites a fabricated 40-hex token that no store holds.  If the auditor's
citation path is live, this must produce a verdict document with defects
(exit 1), not the clean exit 0 of PG02."""
import importlib.util
import json
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
built = pg.build(root, tmp, fleet_mark="config", fake_landed=True)
lane, fleet = built["lane"], built["fleet"]
before = {"lane": pg.object_inventory(lane), "fleet": pg.object_inventory(fleet)}
code, out, err, timed_out = pg.run_auditor(AUDIT, lane, fleet, tmp, False)
after = {"lane": pg.object_inventory(lane), "fleet": pg.object_inventory(fleet)}
doc = pg.normalise_document(out, built)
print(json.dumps({
    "note": "manual discrimination control, NOT a graded grid cell",
    "builder": "build(fleet_mark='config', fake_landed=True)",
    "argv": [sys.executable, str(AUDIT), "--lane-repo", str(lane),
             "--fleet-repo", str(fleet), "--rounds", "1", "--json",
             "--no-errata"],
    "exit": code, "timed_out": timed_out, "stderr": err,
    "objects_acquired": {k: sorted(after[k] - before[k]) for k in after},
    "defects": pg.observed_defects(out),
    "document": doc,
    "premise": built["premise"],
}, indent=1, sort_keys=True))
