#!/usr/bin/env python3
"""Independent probe for the Ancestor family (PG21).

Builds three variants of the same fixture shape using the grid's own
builder (imported, not edited), runs the pinned current auditor on each,
and compares the substantive verdict:

  A  marked + ancestor missing   (== PG21 as registered)
  B  plain  + ancestor missing   (the plain twin PG21 never declares)
  C  marked + ancestor present  (the complete twin: what the omission
                                 question would decide if the ancestor were
                                 readable)

Also records the object inventory before/after each run, the full stderr,
and the parsed document, so the comparison is on observed facts.
"""
import json
import os
import subprocess
import sys
from pathlib import Path

GRID = Path("/fast/scratch/hyaku/kama-r24/falsify/CaseAncestor/repo/tests/report-audit")
sys.path.insert(0, str(GRID))
import promisor_grid_py as G  # noqa: E402

ROOT = Path("/fast/scratch/hyaku/kama-r24/falsify/CaseAncestor/out/twin-root")
AUDIT = Path("/fast/scratch/hyaku/kama-r24/falsify/CaseAncestor/repo/tools/report-landing-audit.py")


def inventory(repo):
    return G.object_inventory(repo)


def run_variant(name, built):
    tmp = built["lane"].parent
    before = {"lane": inventory(built["lane"]), "fleet": inventory(built["fleet"])}
    code, out, err, to = G.run_auditor(AUDIT, built["lane"], built["fleet"], tmp, False)
    after = {"lane": inventory(built["lane"]), "fleet": inventory(built["fleet"])}
    acquired = {k: sorted(after[k] - before[k]) for k in after}
    doc = None
    try:
        doc = json.loads(out)
    except ValueError:
        pass
    defects = []
    if doc:
        for res in doc.get("results", []):
            for d in res.get("defects", []):
                defects.append((d.get("kind"), d.get("token")))
    return {"variant": name, "exit": code, "timed_out": to,
            "acquired": acquired, "defects": sorted(defects),
            "stderr": err.strip(), "stdout_bytes": len(out),
            "premise": built["premise"], "shas": built["shas"]}


def main():
    ROOT.mkdir(parents=True, exist_ok=True)
    results = []
    variants = {
        "A-marked-ancestor-missing": dict(lane_mark="config", ancestor=True,
                                           drop=("ancestor",)),
        "B-plain-ancestor-missing": dict(ancestor=True, drop=("ancestor",)),
        "C-marked-ancestor-present": dict(lane_mark="config", ancestor=True),
        "D-plain-ancestor-present": dict(ancestor=True),
    }
    for i, (name, opt) in enumerate(variants.items()):
        tmp = ROOT / f"{i:02d}-{name}"
        tmp.mkdir(parents=True, exist_ok=True)
        built = G.build(ROOT, tmp, **opt)
        results.append(run_variant(name, built))
    print(json.dumps(results, indent=1, sort_keys=True))


if __name__ == "__main__":
    main()
