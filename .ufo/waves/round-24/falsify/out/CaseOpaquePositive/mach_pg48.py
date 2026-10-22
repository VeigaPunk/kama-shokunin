#!/usr/bin/env python3
"""Direct interrogation of the pinned auditor's own hole-diagnosis
machinery on the PG48 fixture (import the shipped module; no reimplementation).

Asks:
  - what does missing_reachable() report for the lane store?
  - is the missing subtree really referenced by the audited tip tree
    (i.e. would a blanket closure precondition have tripped)?
  - what does opaque_hole() return for this store?
  - what does the auditor's own lookup() say about the cited tokens?
"""
import importlib.util
import json
import shutil
import sys
from pathlib import Path

REPO = Path("/fast/scratch/hyaku/kama-r24/falsify/CaseOpaquePositive/repo")
GRID = REPO / "tests/report-audit/promisor-grid.py"
AUDIT = REPO / "tools/report-landing-audit.py"
ROOT = Path("/fast/scratch/hyaku/kama-r24/falsify/CaseOpaquePositive/mach-root")


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


g = load(GRID, "pggrid")
aud = load(AUDIT, "pgaudit")

shutil.rmtree(ROOT, ignore_errors=True)
ROOT.mkdir(parents=True)
tmp = ROOT / "A"
tmp.mkdir()
built = g.BUILDERS["c_opaque_unused_tree_clean"](ROOT, tmp)
lane, fleet, shas = built["lane"], built["fleet"], built["shas"]

missing, opaque = aud.missing_reachable(lane, "refs/heads/master")
missing_f, opaque_f = aud.missing_reachable(fleet, "HEAD")

# the audited tip tree: does it really reference the missing subtree?
tip_listing = aud.git(lane, "ls-tree", shas["lane_commit"])

store = aud.RepoStore(lane, "refs/heads/master")
store_f = aud.RepoStore(fleet, "HEAD")
hole, hole_oid = aud.opaque_hole([store, store_f])

# the auditor's own view of the tokens the report cites
cites = [shas["lane_commit"]]
status = aud.lookup([store, store_f], cites, "^{commit}")

print(json.dumps({
    "lane_missing": sorted(missing),
    "lane_opaque": sorted(opaque),
    "fleet_missing": sorted(missing_f),
    "fleet_opaque": sorted(opaque_f),
    "missing_subtree_oid": shas["missing_subtree"],
    "missing_subtree_in_missing_set": shas["missing_subtree"] in missing,
    "missing_subtree_in_opaque_set": shas["missing_subtree"] in opaque,
    "tip_tree_listing": tip_listing.strip().split("\n"),
    "tip_tree_references_missing_subtree":
        shas["missing_subtree"] in tip_listing,
    "opaque_hole_path": str(hole.path) if hole is not None else None,
    "opaque_hole_oid": hole_oid,
    "lookup_cited_lane_commit": status,
}, indent=1))
