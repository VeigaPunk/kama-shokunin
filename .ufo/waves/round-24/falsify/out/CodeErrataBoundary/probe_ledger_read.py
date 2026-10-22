#!/usr/bin/env python3
"""Cross-check of the ledger READ path (load_errata), inside the errata
boundary: the ledger file's blob is missing from the lane store while the
ledger commit and the report are intact. Expected: exit 2 (never a verdict);
observed: whether the refusal names the missing ledger blob in the sibling
form 'unavailable required object: ... (tip tree ...) ... (<blob oid>)'.
"""
import json
import subprocess
import sys
from pathlib import Path

BASE = Path("/fast/scratch/hyaku/kama-r24/falsify/CodeErrataBoundary")
GRID_PATH = BASE / "tests/report-audit/promisor-grid.py"
AUDITOR = BASE / "tools/report-landing-audit.py"
ROOT = BASE / "fx"

import importlib.util
spec = importlib.util.spec_from_file_location("grid", GRID_PATH)
grid = importlib.util.module_from_spec(spec)
spec.loader.exec_module(grid)

tmp = ROOT / "A8_ledger_blob_missing"
if tmp.exists():
    import shutil
    shutil.rmtree(tmp)
tmp.mkdir(parents=True)
built = grid.build(ROOT, tmp, errata=True)
lane = built["lane"]
blob = grid.git(lane, "rev-parse",
                "HEAD:registry/report-landing-errata.tsv").strip()
grid.drop_object(lane, blob)
code, out, err, timed_out = grid.run_auditor(AUDITOR, lane, built["fleet"], tmp,
                                              use_errata=True)
obs = {"arm": "A8_ledger_blob_missing", "ledger_blob": blob,
       "exit": code, "stdout_bytes": len(out), "stderr": err.strip(),
       "timed_out": timed_out}
print(json.dumps(obs, indent=1, sort_keys=True))
(BASE / "out" / "A8_ledger_blob_missing.json").write_text(
    json.dumps(obs, indent=1, sort_keys=True), encoding="utf-8")
