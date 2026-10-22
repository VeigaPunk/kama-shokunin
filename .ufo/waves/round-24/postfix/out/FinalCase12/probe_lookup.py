#!/usr/bin/env python3
"""FinalCase12 unit-level probe of lookup() on the PG12 fixture stores.

Shows, for the PINNED implementation and for mutant M1 (the pre-commit
merged-bare implementation), what each store proves about the lane-only
tokens and what the merged lookup returns.
"""
import importlib.util
import json
from pathlib import Path
import shutil
import sys

SCRATCH = Path("/fast/scratch/hyaku/kama-r24/postfix/FinalCase12")
CLONE = SCRATCH / "clone"
MYTMP = SCRATCH / "tmp"


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


pg = load("pg", CLONE / "tests/report-audit/promisor-grid.py")
pinned = load("pinned_audit", CLONE / "tools/report-landing-audit.py")
m1 = load("m1_audit", SCRATCH / "mutant-M1-precommit-lookup.py")

root = Path(pg.tempfile.mkdtemp(prefix="fc12-unit-", dir=str(MYTMP)))
tmp = root / "pg12"
tmp.mkdir(parents=True, exist_ok=True)
built = pg.BUILDERS["c_omission_marker_lane"](root, tmp)
lane, fleet = built["lane"], built["fleet"]
shas = built["shas"]
tip = pg.git(lane, "rev-parse", "refs/heads/master").strip()
fleet_tip = pg.git(fleet, "rev-parse", "HEAD^{commit}").strip()

tokens = [shas["lane_commit"], shas["omitted"]]
stores = (pinned.build_store(lane, tip), pinned.build_store(fleet, fleet_tip))

out = {"root": str(root), "lane": str(lane), "fleet": str(fleet),
       "tip": tip, "fleet_tip": fleet_tip, "tokens": tokens,
       "per_store_bare": {}, "results": {}}

for s, name in zip(stores, ("lane", "fleet")):
    out["per_store_bare"][name] = {
        t: list(pinned.bare_objects(s, [t])[t]) for t in tokens}

out["results"]["pinned_peel_commit"] = pinned.lookup(stores, tokens, "^{commit}")
out["results"]["pinned_no_peel"] = pinned.lookup(stores, tokens)
out["results"]["m1_peel_commit"] = m1.lookup(stores, tokens, "^{commit}")
out["results"]["m1_no_peel"] = m1.lookup(stores, tokens)

# the cross-store case the merge is about: a token that exists in ONE store
# only, as a non-commit, looked up with the commit peel.
fleet_only_blob = pg.git(fleet, "hash-object", "-w", "--stdin",
                         data=b"fleet only blob\n").strip()
stores2 = (pinned.build_store(lane, tip), pinned.build_store(fleet, fleet_tip))
out["results"]["fleet_only_blob_pinned"] = pinned.lookup(
    stores2, [fleet_only_blob], "^{commit}")
out["results"]["fleet_only_blob_m1"] = m1.lookup(
    stores2, [fleet_only_blob], "^{commit}")
out["fleet_only_blob"] = fleet_only_blob

(SCRATCH / "out/lookup-unit.json").write_text(
    json.dumps(out, indent=1, sort_keys=False) + "\n", encoding="utf-8")
print(json.dumps(out, indent=1))
shutil.rmtree(root, ignore_errors=True)
