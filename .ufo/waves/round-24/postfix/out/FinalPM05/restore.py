#!/usr/bin/env python3
"""FinalPM05 restoration probe: same bounded detector, restored bytes.

Runs the pinned grid (same two declared cells, current arm) against the
RESTORED pristine auditor of the private clone after the mutated run, and
records the outcome. The mutant was written to a separate file; the pinned
auditor bytes were never modified.
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
import os
import sys
from pathlib import Path

SCRATCH = Path("/fast/scratch/hyaku/kama-r24/postfix/FinalPM05")
CLONE = SCRATCH / "clone"
OUT = SCRATCH / "out"
TMP = SCRATCH / "tmp"
os.environ["TMPDIR"] = str(TMP)

MUTATOR = CLONE / "tests/report-audit/promisor-mutants.py"
GRID = CLONE / "tests/report-audit/promisor-grid.py"
PRISTINE = CLONE / "tools/report-landing-audit.py"
EXPECT = CLONE / "tests/report-audit/promisor-grid-expectations.json"
CELLS = ["PG26-cross-repo-found-promisor", "PG27-cross-repo-found-plain"]

spec = importlib.util.spec_from_file_location("pm_pinned", MUTATOR)
pm = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pm)

rc, rows, err, doc = pm.run_grid(GRID, PRISTINE, "current", CELLS, 600)
rows_out = []
for r in rows:
    d = pm.row_detail(r)
    d["class"] = pm.classify_row(r)
    d["graded"] = pm.graded(r)
    d["violated"] = (r.get("met") is False or r.get("twin_equal") is False)
    rows_out.append(d)

restored = {
    "grid_exit": rc,
    "stderr": err,
    "harness_fault": pm.harness_fault(doc, rows, err),
    "violated_rows": [pm.row_name(r) for r in pm.violated_rows(rows)],
    "rows": rows_out,
    "auditor_sha256_top": doc.get("auditor_sha256"),
    "expectations_sha256": doc.get("expectations_sha256"),
    "grid_sha256": doc.get("grid_sha256"),
    "population_sha256": doc.get("population_sha256"),
    "population_size": doc.get("population_size"),
    "auditor_sha256": hashlib.sha256(PRISTINE.read_bytes()).hexdigest(),
    "expectations_sha256_file": hashlib.sha256(
        EXPECT.read_bytes()).hexdigest(),
    "argv": [sys.executable, str(Path(__file__).resolve())],
}
(OUT / "grid-restored.json").write_text(
    json.dumps(doc, indent=1, sort_keys=True), encoding="utf-8")
(OUT / "restore-record.json").write_text(
    json.dumps(restored, indent=1, sort_keys=True), encoding="utf-8")
print(json.dumps(restored, indent=1, sort_keys=True))
