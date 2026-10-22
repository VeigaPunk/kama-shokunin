#!/usr/bin/env python3
"""Premise probe for FinalCase08: build the PG08 fixture exactly as the grid
does and record what each store holds.  No auditor is executed here."""
import json
import os
import subprocess
import sys
from pathlib import Path

CLONE = Path("/fast/scratch/hyaku/kama-r24/postfix/FinalCase08/clone")
import importlib.util  # noqa: E402

_spec = importlib.util.spec_from_file_location(
    "promisor_grid", CLONE / "tests" / "report-audit" / "promisor-grid.py")
G = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(G)

root = Path("/fast/scratch/hyaku/kama-r24/postfix/FinalCase08/fixture")
tmp = Path("/fast/scratch/hyaku/kama-r24/postfix/FinalCase08/fixture/case")
for p in (root, tmp):
    p.mkdir(parents=True, exist_ok=True)

built = G.BUILDERS["c_complete_fleet_plain"](root, tmp)
lane, fleet = built["lane"], built["fleet"]
shas = built["shas"]
cited = shas["lane_commit"]
report_blob = shas["report_blob"]


def present(repo, oid):
    p = subprocess.run(["git", "--no-lazy-fetch", "-C", str(repo),
                        "cat-file", "--batch-check=%(objectname) %(objecttype)"],
                       input=f"{oid}\n", capture_output=True, text=True)
    return p.stdout.strip()


out = {
    "fixture_root": str(root),
    "lane": str(lane),
    "fleet": str(fleet),
    "premise": built["premise"],
    "cited_lane_commit": cited,
    "cited_in_lane": present(lane, cited),
    "cited_in_fleet": present(fleet, cited),
    "report_blob": report_blob,
    "report_blob_in_fleet": present(fleet, report_blob),
    "report_blob_in_lane": present(lane, report_blob),
    "lane_promisor_facts": G.promisor_facts(lane),
    "fleet_promisor_facts": G.promisor_facts(fleet),
    "report_text": subprocess.run(
        ["git", "--no-lazy-fetch", "-C", str(fleet), "show",
         f"HEAD:{G.REL}"], capture_output=True, text=True).stdout,
    "builder_source": G.__file__,
}
print(json.dumps(out, indent=1, sort_keys=True))
