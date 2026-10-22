#!/usr/bin/env python3
"""Bounded probe for the round-24 required-read paths of tools/report-landing-audit.py.

Scope (CodeRequiredReads leaf seat):
  * history / tree / SOURCES / report / errata read failures must never be
    catch-and-pass: the run must exit 2 (could-not-evaluate), never a verdict.
  * root_tree() is an error-identity helper: it must not create a verdict and
    must not act as an upfront gate.

This is NOT the grid: it builds a bounded set of fixture cells with the
pinned repository's own fixture builders (tests/report-audit/promisor-grid.py)
and runs the pinned auditor on each.  No network, no transport, no execution
payload, no full grid sweep.  Every git probe uses --no-lazy-fetch.
"""
from __future__ import annotations

import importlib.util
import json
import os
from pathlib import Path
import shutil
import sys
import tempfile

HERE = Path(__file__).resolve().parent
REPO = HERE.parent                      # the pinned scratch checkout
GRID_PATH = REPO / "tests/report-audit/promisor-grid.py"
AUDITOR = REPO / "tools/report-landing-audit.py"
ORACLE = Path("/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/"
              "round-24/oracle-snapshot-before-inspection.json")
SCRATCH = Path("/fast/scratch/hyaku/kama-r24/falsify/CodeRequiredReads")


def load_grid():
    spec = importlib.util.spec_from_file_location("promisor_grid", GRID_PATH)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def main():
    grid = load_grid()
    oracle = {c["case"]: c for c in json.loads(ORACLE.read_text())["cases"]}
    root = Path(tempfile.mkdtemp(prefix="probe-", dir=str(SCRATCH)))
    out = {"root": str(root), "auditor": str(AUDITOR), "cells": []}
    cells = [
        ("PG07-complete-lane-plain", None),
        ("PG13-missing-lane-blob-promisor", None),
        ("PG14-missing-lane-blob-plain", None),
        ("PG15-missing-lane-tree-promisor", None),
        ("PG16-missing-lane-tree-plain", None),
        ("PG45-missing-unused-tree-plain", None),
        ("PG17-missing-fleet-report-promisor", None),
        ("PG18-missing-fleet-report-plain", None),
        ("PG21-missing-ancestor-promisor", None),
        ("PG25-unknown-citation-plain", None),
        ("PROBE-errata-blob-missing", "custom"),
    ]
    try:
        for index, (case, mode) in enumerate(cells):
            tmp = Path(root, f"{index:03d}-{case}")
            tmp.mkdir(parents=True, exist_ok=True)
            if mode == "custom":
                # the errata ledger is present and authorized; only its blob
                # is missing.  A silent pass over the read would leave the
                # spliced citation uncorrected (exit 1) or corrected
                # (exit 0); the contract wants exit 2.
                built = grid.build(root, tmp, errata=True)
                lane = built["lane"]
                blob = grid.git(lane, "rev-parse",
                                "master:registry/report-landing-errata.tsv"
                                ).strip()
                built["shas"]["errata_blob"] = grid.drop_object(lane, blob)
                expect = {"case": case, "kind": "policy",
                          "frozen": {"exit": 2, "reason_class": "unavailable"},
                          "original": {"exit": 2,
                                       "reason_class": "unavailable"},
                          "names_any_of": ["registry/report-landing-errata.tsv"],
                          "reason_forbidden": ["partial clone (",
                                               "promisor pack"]}
            else:
                built = grid.BUILDERS[oracle[case]["builder"]](root, tmp)
                expect = oracle[case]
            lane, fleet = built["lane"], built["fleet"]
            before = {"lane": grid.object_inventory(lane),
                      "fleet": grid.object_inventory(fleet)}
            code, stdout, stderr, timed_out = grid.run_auditor(
                AUDITOR, lane, fleet, tmp, bool(built.get("errata")))
            after = {"lane": grid.object_inventory(lane),
                     "fleet": grid.object_inventory(fleet)}
            obs = {"arm": "current", "exit": code,
                   "traceback": "Traceback (most recent call last)" in stderr,
                   "timed_out": timed_out,
                   "leaked": bool(grid.survivors(tmp)),
                   "objects_acquired": {k: sorted(after[k] - before[k])
                                        for k in after},
                   "stderr": stderr, "stdout": stdout}
            names = [grid.resolve_token(n, built["shas"])
                     for n in expect.get("names_any_of", [])]
            forbidden = expect.get("reason_forbidden", [])
            live = expect.get("amended", expect["original"])
            problems = grid.grade(live, obs, stderr, stdout, built["shas"],
                                   names, forbidden)
            obs["case"] = case
            obs["builder"] = expect.get("builder")
            obs["expectation"] = live
            obs["problems"] = problems
            obs["met"] = not problems
            obs["shas"] = built["shas"]
            out["cells"].append(obs)
            print(json.dumps({
                "case": case, "exit": code, "expected_exit": live["exit"],
                "met": obs["met"], "problems": problems,
                "stderr": stderr.strip()[:600],
                "stdout_len": len(stdout.strip()),
                "acquired": obs["objects_acquired"],
                "traceback": obs["traceback"], "timeout": timed_out,
            }, sort_keys=True))
    finally:
        out_path = Path(sys.argv[1]) if len(sys.argv) > 1 else \
            HERE / "required_reads_probe.json"
        out_path.write_text(json.dumps(out, indent=1, sort_keys=True),
                            encoding="utf-8")
        print("wrote", out_path)
        shutil.rmtree(root, ignore_errors=True)


if __name__ == "__main__":
    main()
