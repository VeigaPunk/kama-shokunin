#!/usr/bin/env python3
"""Write the pinned runner's own STUB_GRID and CANDIDATE fixture sources to
the scratch, byte-identical to the module constants."""
import hashlib
import importlib.util
import json
from pathlib import Path

CLONE = Path("/fast/scratch/hyaku/kama-r24/postfix/FinalPM03/clone")
RUNNER = CLONE / "tests/report-audit/promisor-mutants.py"
OUT = Path("/fast/scratch/hyaku/kama-r24/postfix/FinalPM03/stub")
OUT.mkdir(parents=True, exist_ok=True)

spec = importlib.util.spec_from_file_location("pinned_promisor_mutants", RUNNER)
pm = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pm)

grid = OUT / "stub-grid.py"
grid.write_text(pm.STUB_GRID, encoding="utf-8")
cand = OUT / "candidate.py"
cand.write_text(pm.CANDIDATE, encoding="utf-8")

print(json.dumps({
    "stub_grid": str(grid),
    "stub_grid_sha256": hashlib.sha256(pm.STUB_GRID.encode()).hexdigest(),
    "candidate": str(cand),
    "candidate_sha256": hashlib.sha256(pm.CANDIDATE.encode()).hexdigest(),
    "stub_modes": sorted(set(
        __import__("re").findall(r'mode == "([a-z0-9_]+)"', pm.STUB_GRID))),
}, indent=1))
