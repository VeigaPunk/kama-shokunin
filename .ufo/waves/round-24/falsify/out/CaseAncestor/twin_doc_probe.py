#!/usr/bin/env python3
"""Marked vs unmarked document comparison for the Ancestor family.

For each of the two ancestor shapes (missing / present) build a marked and
an unmarked repository from the grid's own builder, run the pinned current
auditor, and compare the verdict documents after the grid's own path
normalisation (the lane/fleet paths are replaced by placeholders).
"""
import json
import os
import sys
from pathlib import Path

GRID = Path("/fast/scratch/hyaku/kama-r24/falsify/CaseAncestor/repo/tests/report-audit")
sys.path.insert(0, str("/fast/scratch/hyaku/kama-r24/falsify/CaseAncestor/out"))
import promisor_grid_py as G  # noqa: E402

ROOT = Path("/fast/scratch/hyaku/kama-r24/falsify/CaseAncestor/out/twin-doc")
AUDIT = Path("/fast/scratch/hyaku/kama-r24/falsify/CaseAncestor/repo/tools/report-landing-audit.py")


def one(name, opt, i):
    tmp = ROOT / f"{i:02d}-{name}"
    tmp.mkdir(parents=True, exist_ok=True)
    built = G.build(ROOT, tmp, **opt)
    before = {k: G.object_inventory(built[k]) for k in ("lane", "fleet")}
    code, out, err, to = G.run_auditor(AUDIT, built["lane"], built["fleet"], tmp, False)
    after = {k: G.object_inventory(built[k]) for k in ("lane", "fleet")}
    acquired = {k: sorted(after[k] - before[k]) for k in after}
    doc = G.normalise_document(out, built)
    defects = []
    if doc:
        for res in doc["results"]:
            for d in res.get("defects", []):
                defects.append((d.get("kind"), d.get("token")))
    return {"name": name, "exit": code, "document": doc,
            "defects": sorted(defects), "acquired": acquired,
            "stderr": err.strip(), "stdout_bytes": len(out),
            "premise": built["premise"], "shas": built["shas"]}


def main():
    ROOT.mkdir(parents=True, exist_ok=True)
    res = []
    res.append(one("missing-marked", dict(lane_mark="config", ancestor=True,
                                           drop=("ancestor",)), 0))
    res.append(one("missing-unmarked", dict(ancestor=True,
                                             drop=("ancestor",)), 1))
    res.append(one("present-marked", dict(lane_mark="config", ancestor=True), 2))
    res.append(one("present-unmarked", dict(ancestor=True), 3))

    out = {"variants": res, "comparisons": {}}
    for a, b in (("missing-marked", "missing-unmarked"),
                 ("present-marked", "present-unmarked")):
        da = next(v for v in res if v["name"] == a)
        db = next(v for v in res if v["name"] == b)
        out["comparisons"][f"{a}|{b}"] = {
            "same_exit": da["exit"] == db["exit"],
            "exits": [da["exit"], db["exit"]],
            "same_document": da["document"] == db["document"],
            "both_documents_none": da["document"] is None and db["document"] is None,
            "same_defects": da["defects"] == db["defects"],
            "defects": [da["defects"], db["defects"]],
            "acquired": [da["acquired"], db["acquired"]],
            "stderr_equal": da["stderr"] == db["stderr"],
        }
    print(json.dumps(out, indent=1, sort_keys=True))


if __name__ == "__main__":
    main()
