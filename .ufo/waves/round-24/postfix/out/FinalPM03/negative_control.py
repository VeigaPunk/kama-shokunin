#!/usr/bin/env python3
"""Negative control on the PINNED runner's main(argv), driven by the runner's
own STUB_GRID and CANDIDATE fixtures.  No repository, no fixture, no grid.

Cases:
  unmet           the mutant's ONLY failed row is complete-state PG01
                  (PG01-complete-lane-promisor-config) -> outside PM03's
                  expect_rows envelope
  traceback_row  the mutant's row carries a traceback
  internal_row   the mutant's row carries the canonical internal_error flag
  missing_metadata the mutant's row has no comparison metadata (expected_exit
                  absent) -> unclassified, no guessed credit
"""
import json
import os
import subprocess
import sys
from pathlib import Path

S = Path("/fast/scratch/hyaku/kama-r24/postfix/FinalPM03")
RUNNER = S / "clone/tests/report-audit/promisor-mutants.py"
GRID = S / "stub/stub-grid.py"
CAND = S / "stub/candidate.py"
OUT = S / "out"
MID = "PM03-skip-required-object-availability"

results = []
for mode in ("unmet", "traceback_row", "internal_row", "missing_metadata"):
    env = dict(os.environ,
               GRID_STUB_MODE=mode,
               GRID_STUB_LOG=str(S / f"out/canary-{mode}.log"),
               TMPDIR=str(S / "tmp/stub"),
               PYTHONDONTWRITEBYTECODE="1")
    argv = [sys.executable, str(RUNNER), "--grid", str(GRID),
            "--current", str(CAND), "--only", MID, "--json"]
    proc = subprocess.run(argv, capture_output=True, env=env, timeout=300)
    doc = {}
    try:
        doc = json.loads(proc.stdout.decode("utf-8", "replace"))
    except (ValueError, UnicodeDecodeError):
        doc = {}
    rows = doc.get("rows") or []
    entry = {
        "mode": mode,
        "argv": argv,
        "exit": proc.returncode,
        "stderr": proc.stderr.decode("utf-8", "replace").strip(),
        "rows": [{k: r.get(k) for k in ("mutant", "status", "killed", "reason",
                                       "failed_rows", "unexpected_rows",
                                       "applied_alternative", "classes",
                                       "availability_credit", "verdict_change",
                                       "diagnostic_only", "same_verdict_exit",
                                       "unclassified", "auditor_sha256",
                                       "failed_row_detail")}
                 for r in rows],
        "doc_top": {k: doc.get(k) for k in ("killed", "killed_ids", "surviving",
                                           "could_not_evaluate", "evaluated",
                                           "pristine")},
        "provenance": doc.get("provenance"),
    }
    results.append(entry)
    print(f"== mode={mode} exit={proc.returncode}")
    print(json.dumps(entry, indent=1, sort_keys=True))

(OUT / "negative-control.json").write_text(
    json.dumps(results, indent=1, sort_keys=True), encoding="utf-8")
