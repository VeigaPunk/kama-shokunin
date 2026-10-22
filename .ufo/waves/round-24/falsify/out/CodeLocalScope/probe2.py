#!/usr/bin/env python3
"""Counterfactual probe: does the exit-2 negative diagnosis depend on the
store-wide root set (every present commit/tree/tag) or would a refs-only
traversal suffice?

Shape: a present but REF-UNREACHABLE commit whose tree references a missing
blob, and the report CITES that missing blob.
  candidate (store-wide roots)  -> expected exit 2 (could-not-evaluate)
  counterfactual (refs-only)    -> would report exit 1, i.e. a false
                                   "proved absent" verdict
No production file is touched: the counterfactual patches the imported
module in this process only.
"""
import contextlib
import importlib.util
import io
import json
import os
import shutil
import sys
from pathlib import Path

WORK = Path("/fast/scratch/hyaku/kama-r24/falsify/CodeLocalScope/work")
GRID = WORK / "tests/report-audit/promisor-grid.py"
AUDITOR = WORK / "tools/report-landing-audit.py"
ROOT = Path("/fast/scratch/hyaku/kama-r24/falsify/CodeLocalScope/grid-root2")
OUT = Path(sys.argv[1])
OUT.mkdir(parents=True, exist_ok=True)
os.environ["TMPDIR"] = "/fast/scratch/hyaku/kama-r24/falsify/CodeLocalScope/tmp"


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


grid = load("grid", GRID)
aud = load("aud", AUDITOR)

REPORT = {"scenarios": {}}


def refs_only_roots(repo):
    """The candidate's present_roots restricted to ref-reachable objects."""
    reachable = set()
    for line in aud.git(repo, "rev-list", "--objects", "--all").split("\n"):
        if line.strip():
            reachable.add(line.split()[0])
    out = aud.git(repo, "cat-file", "--batch-all-objects",
                  "--batch-check=%(objectname) %(objecttype)")
    roots = []
    for line in out.split("\n"):
        name, _, kind = line.partition(" ")
        if kind in ("commit", "tree", "tag") and name in reachable:
            roots.append(name)
    return roots


def run_in_process(lane, fleet):
    """Run the auditor's own main() in this process (no subprocess)."""
    argv = ["--lane-repo", str(lane), "--fleet-repo", str(fleet),
            "--rounds", "1", "--json", "--no-errata"]
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        code = aud.main(argv)
    return {"exit": code, "stdout": out.getvalue().strip()[:400],
            "stderr": err.getvalue().strip()[:400]}


def build_fixture(name, cite_missing_blob, mark):
    root = ROOT / name
    if root.exists():
        shutil.rmtree(root)
    root.mkdir(parents=True)
    tmp = root / "t"
    built = grid.build(root, tmp, lane_mark=mark, unselected_hole=True,
                       fake_landed=True, drop=("unselected_blob",))
    lane, fleet = built["lane"], built["fleet"]
    shas = built["shas"]
    side = shas["unselected_blob"]
    # make the side commit REF-UNREACHABLE but still present
    grid.git(lane, "update-ref", "-d", "refs/heads/side")
    if cite_missing_blob:
        text = grid.report_text(cites=[shas["lane_commit"], side])
    else:
        text = grid.report_text(cites=[shas["lane_commit"], grid.FAKE])
    if grid.git(fleet, "show", f"HEAD:{grid.REL}") != text:
        grid.publish(fleet, text, 2100)
    tip = grid.git(lane, "rev-parse", "HEAD").strip()
    obs = {
        "cited_missing_blob": side if cite_missing_blob else grid.FAKE,
        "missing_blob_present": grid.object_exists(lane, side),
        "side_ref_exists": bool(grid.git(lane, "for-each-ref",
                                         "--format=%(refname)",
                                         "refs/heads/side").strip()),
        "candidate_roots": len(aud.present_roots(lane)),
        "refs_only_roots": len(refs_only_roots(lane)),
        "candidate_missing": sorted(aud.missing_reachable(lane, tip)[0]),
        "candidate_opaque": sorted(aud.missing_reachable(lane, tip)[1]),
    }
    return lane, fleet, obs


for label, cite_missing, mark in (
        ("G_refunreachable_cited_missing_blob_promisor", True, "config"),
        ("H_refunreachable_cited_missing_blob_plain", True, None),
        ("I_refunreachable_fabricated_token_uncited_hole_promisor",
         False, "config")):
    lane, fleet, obs = build_fixture(label, cite_missing, mark)
    obs["candidate"] = run_in_process(lane, fleet)
    original = aud.present_roots
    aud.present_roots = refs_only_roots
    try:
        obs["counterfactual_refs_only"] = run_in_process(lane, fleet)
    finally:
        aud.present_roots = original
    REPORT["scenarios"][label] = obs

(OUT / "counterfactual-result.json").write_text(
    json.dumps(REPORT, indent=1, sort_keys=True), encoding="utf-8")
print(json.dumps(REPORT, indent=1, sort_keys=True))
