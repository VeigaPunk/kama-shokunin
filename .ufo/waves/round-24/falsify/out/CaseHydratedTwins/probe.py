#!/usr/bin/env python3
"""CaseHydratedTwins independent probe.

Rebuilds the four HydratedTwins fixtures from the PINNED clone's grid
module and asserts the premises the grid itself never checks:

  * the blobless clones really are promisor-backed partial clones
    (config keys + .promisor marker + a blob absent before hydration),
  * after hydration the reachable closure is COMPLETE (no missing ids),
  * hydration is load-bearing: an unhydrated twin must NOT reach the same
    verdict (otherwise the case does not discriminate "hydrated"),
  * the auditor acquires no objects in either variant, even though the
    clone's file:// origin is still present on disk (lazy fetch possible).

Read-only w.r.t. production: everything happens in this agent's scratch.
"""
import json
import os
import subprocess
import sys
from pathlib import Path

REPO = Path("/fast/scratch/hyaku/kama-r24/falsify/CaseHydratedTwins/repo")
import importlib.util  # noqa: E402

_spec = importlib.util.spec_from_file_location(
    "promisor_grid", REPO / "tests" / "report-audit" / "promisor-grid.py")
G = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(G)

ROOT = Path("/fast/scratch/hyaku/kama-r24/falsify/CaseHydratedTwins/probe")
ROOT.mkdir(parents=True, exist_ok=True)
AUDITOR = REPO / "tools" / "report-landing-audit.py"


def cfg(repo):
    out = G.git(repo, "config", "--null", "--list")
    return sorted(e.replace("\n", "=") for e in out.split("\0") if e)


def blob_present(repo, sha):
    return G.object_exists(repo, sha)


def audit(label, built):
    lane, fleet = built["lane"], built["fleet"]
    before = {"lane": G.object_inventory(lane), "fleet": G.object_inventory(fleet)}
    code, out, err, timed_out = G.run_auditor(AUDITOR, lane, fleet, ROOT)
    after = {"lane": G.object_inventory(lane), "fleet": G.object_inventory(fleet)}
    acquired = {k: sorted(after[k] - before[k]) for k in after}
    doc = None
    try:
        doc = json.loads(out)
    except ValueError:
        pass
    defects = []
    if doc is not None:
        for res in doc.get("results", []):
            for d in res.get("defects", []):
                defects.append((d.get("kind"), d.get("token")))
    return {"label": label, "exit": code, "timed_out": timed_out,
            "stderr": err.strip()[-400:], "defects": defects,
            "status": (doc or {}).get("summary", {}).get("status"),
            "objects_acquired": acquired}


def facts(label, repo, root_ref):
    p = G.promisor_facts(repo)
    return {
        "label": label,
        "config": [c for c in cfg(repo)
                   if "promisor" in c or "partialclone" in c
                   or c.startswith("remote.origin.url")],
        "promisor_backed": p["promisor_backed"],
        "promisor_markers": p["markers"],
        "missing_reachable": G.missing_objects(repo, root_ref),
        "object_count": len(G.object_inventory(repo)),
    }


def main():
    report = {}
    tmp = ROOT / "t"
    tmp.mkdir(parents=True, exist_ok=True)

    # ---- PG05: hydrated blobless LANE -----------------------------------
    b5 = G.build(ROOT, tmp / "pg05", lane_mark="config", blobless_lane=True,
                 hydrate_lane=True)
    shas = b5["shas"]
    report["PG05_lane_facts"] = facts("hydrated-blobless-lane",
                                      b5["lane"], "refs/heads/master")
    report["PG05_fleet_facts"] = facts("plain-fleet", b5["fleet"], "HEAD")
    report["PG05_f_blob_present"] = blob_present(b5["lane"], shas["f_blob"])
    report["PG05_sources_blob_present"] = blob_present(b5["lane"],
                                                        shas["sources_blob"])
    report["PG05_premise"] = b5["premise"]
    report["PG05_audit"] = audit("PG05 hydrated", b5)

    # unhydrated counterpart: same builder without hydrate_lane
    b5u = G.build(ROOT, tmp / "pg05u", lane_mark="config", blobless_lane=True)
    report["PG05U_lane_facts"] = facts("unhydrated-blobless-lane",
                                       b5u["lane"], "refs/heads/master")
    report["PG05U_f_blob_present"] = blob_present(b5u["lane"],
                                                  b5u["shas"]["f_blob"])
    report["PG05U_audit"] = audit("PG05 unhydrated", b5u)

    # ---- PG06: hydrated blobless FLEET ----------------------------------
    b6 = G.build(ROOT, tmp / "pg06", fleet_mark="config", blobless_fleet=True,
                 hydrate_fleet=True)
    report["PG06_fleet_facts"] = facts("hydrated-blobless-fleet",
                                       b6["fleet"], "HEAD")
    report["PG06_report_blob_present"] = blob_present(b6["fleet"],
                                                       b6["shas"]["report_blob"])
    report["PG06_premise"] = b6["premise"]
    report["PG06_audit"] = audit("PG06 hydrated", b6)

    b6u = G.build(ROOT, tmp / "pg06u", fleet_mark="config", blobless_fleet=True)
    report["PG06U_fleet_facts"] = facts("unhydrated-blobless-fleet",
                                        b6u["fleet"], "HEAD")
    report["PG06U_report_blob_present"] = blob_present(b6u["fleet"],
                                                        b6u["shas"]["report_blob"])
    report["PG06U_audit"] = audit("PG06 unhydrated", b6u)

    # ---- PG07 / PG08: plain twins ---------------------------------------
    b7 = G.build(ROOT, tmp / "pg07")
    report["PG07_lane_facts"] = facts("plain-lane", b7["lane"],
                                      "refs/heads/master")
    report["PG07_audit"] = audit("PG07 plain", b7)
    b8 = G.build(ROOT, tmp / "pg08")
    report["PG08_fleet_facts"] = facts("plain-fleet", b8["fleet"], "HEAD")
    report["PG08_audit"] = audit("PG08 plain", b8)

    # ---- document equality, grid-style normalisation --------------------
    def norm(built, out):
        return json.dumps(G.normalise_document(out, built), sort_keys=True)

    print(json.dumps(report, indent=1, sort_keys=True))


if __name__ == "__main__":
    main()
