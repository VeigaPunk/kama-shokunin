#!/usr/bin/env python3
"""FinalCase19 control probe (NOT a registered cell): discrimination controls
for PG19-missing-fleet-tree-promisor.

Goal: show that the refusal observed in the registered cell is caused by the
ABSENT fleet tip tree object, not by the promisor metadata and not by a
blanket precondition, and that with the same object present the audit
returns an ordinary verdict document instead of a refusal.

Controls (all built with the pinned grid's own builder, in this seat's own
scratch, never in production):
  C1  complete promisor-marked twin  (fleet_mark=config, no drop)
  C2  the registered PG19 fixture with the fleet tip tree object RESTORED
      (hydrated) -- a labelled copy, never the registered cell itself
Both are audited with the pinned tools/report-landing-audit.py and the same
argv the grid uses.
"""
import importlib.util
import json
from pathlib import Path
import shutil

CLONE = Path("/fast/scratch/hyaku/kama-r24/postfix/FinalCase19/clone")
GRID = CLONE / "tests/report-audit/promisor-grid.py"
AUDIT = CLONE / "tools/report-landing-audit.py"
TMP = Path("/fast/scratch/hyaku/kama-r24/postfix/FinalCase19/tmp")
OUT = Path("/fast/scratch/hyaku/kama-r24/postfix/FinalCase19/out")

spec = importlib.util.spec_from_file_location("pgrid", GRID)
grid = importlib.util.module_from_spec(spec)
spec.loader.exec_module(grid)

root = Path(grid.tempfile.mkdtemp(prefix="control-", dir=str(TMP)))
result = {"root": str(root), "controls": {}}

# ---- C1: complete promisor-marked twin (no object removed) -------------
tmp1 = root / "C1"
tmp1.mkdir(parents=True)
built1 = grid.build(root, tmp1, fleet_mark="config")
lane1, fleet1 = built1["lane"], built1["fleet"]
shas1 = built1["shas"]
before = {"lane": grid.object_inventory(lane1),
          "fleet": grid.object_inventory(fleet1)}
code, out, err, timed_out = grid.run_auditor(AUDIT, lane1, fleet1, tmp1, False)
after = {"lane": grid.object_inventory(lane1),
         "fleet": grid.object_inventory(fleet1)}
try:
    doc = json.loads(out)
except ValueError:
    doc = None
result["controls"]["C1-complete-promisor-twin"] = {
    "fleet_tip_tree": shas1.get("fleet_tip_tree"),
    "lane_tip_tree": grid.git(lane1, "rev-parse", "HEAD^{tree}").strip(),
    "exit": code, "timed_out": timed_out,
    "stderr": err.strip(),
    "stdout_len": len(out.strip()),
    "document_summary": (doc or {}).get("summary") if doc else None,
    "document_defects": [d for r in (doc or {}).get("results", [])
                         for d in r.get("defects", [])],
    "objects_acquired": {k: sorted(after[k] - before[k]) for k in after},
    "stdout_C1": out,
}

# ---- C2: the registered PG19 fixture with the tip tree restored ---------
tmp2 = root / "C2"
tmp2.mkdir(parents=True)
built2 = grid.build(root, tmp2, fleet_mark="config", drop=("fleet_tip_tree",))
lane2, fleet2 = built2["lane"], built2["fleet"]
tree_oid = built2["shas"]["fleet_tip_tree"]
src = (Path(grid.git_dir(fleet1), "objects", tree_oid[:2],
             tree_oid[2:]))
dst = Path(grid.git_dir(fleet2), "objects", tree_oid[:2], tree_oid[2:])
dst.parent.mkdir(parents=True, exist_ok=True)
shutil.copyfile(src, dst)
present = grid.git(fleet2, "cat-file", "-t", tree_oid).strip()
before = {"lane": grid.object_inventory(lane2),
          "fleet": grid.object_inventory(fleet2)}
code2, out2, err2, timed_out2 = grid.run_auditor(AUDIT, lane2, fleet2, tmp2,
                                                  False)
after = {"lane": grid.object_inventory(lane2),
         "fleet": grid.object_inventory(fleet2)}
try:
    doc2 = json.loads(out2)
except ValueError:
    doc2 = None
result["controls"]["C2-hydrated-PG19-fixture"] = {
    "hydrated_object": tree_oid,
    "object_type_after_hydration": present,
    "exit": code2, "timed_out": timed_out2,
    "stderr": err2.strip(),
    "stdout_len": len(out2.strip()),
    "document_summary": (doc2 or {}).get("summary") if doc2 else None,
    "document_defects": [d for r in (doc2 or {}).get("results", [])
                         for d in r.get("defects", [])],
    "objects_acquired": {k: sorted(after[k] - before[k]) for k in after},
    "document_equals_C1": (doc2 == doc) if (doc2 and doc) else None,
    "normalised_equals_C1": (grid.normalise_document(out2, built2)
                             == grid.normalise_document(out, built1)),
    "stdout_C1": out,
    "stdout_C2": out2,
}

shutil.rmtree(root, ignore_errors=True)
OUT.mkdir(parents=True, exist_ok=True)
(OUT / "control-probe.json").write_text(
    json.dumps(result, indent=1, sort_keys=True) + "\n", encoding="utf-8")
print(json.dumps(result, indent=1, sort_keys=True))
