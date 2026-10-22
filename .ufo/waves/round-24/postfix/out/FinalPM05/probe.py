#!/usr/bin/env python3
"""FinalPM05 bounded probe: canonical operator PM05-ignore-second-repo.

Uses the PINNED mutator's own APIs (apply_mutation / compiles / run_grid /
violated_rows / classify_row) against a PRIVATE copy of the pinned auditor.
Never touches production. Runs only the declared cells PG26 and PG27 on the
current arm, once per tool (pristine, mutated).
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
import os
import re
import sys
from pathlib import Path

SCRATCH = Path("/fast/scratch/hyaku/kama-r24/postfix/FinalPM05")
CLONE = SCRATCH / "clone"
OUT = SCRATCH / "out"
OUT.mkdir(parents=True, exist_ok=True)
TMP = SCRATCH / "tmp"
TMP.mkdir(parents=True, exist_ok=True)
os.environ["TMPDIR"] = str(TMP)

MUTATOR = CLONE / "tests/report-audit/promisor-mutants.py"
GRID = CLONE / "tests/report-audit/promisor-grid.py"
PRISTINE = CLONE / "tools/report-landing-audit.py"
EXPECT = CLONE / "tests/report-audit/promisor-grid-expectations.json"
MUTANT_ID = "PM05-ignore-second-repo"
CELLS = ["PG26-cross-repo-found-promisor", "PG27-cross-repo-found-plain"]
GRID_TIMEOUT = 600


def sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def sha256_file(p: Path) -> str:
    return sha256_bytes(p.read_bytes())


spec = importlib.util.spec_from_file_location("pm_pinned", MUTATOR)
pm = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pm)

record: dict = {
    "seat": "FinalPM05",
    "pinned_commit": "92063cfc60e217fa7e2098c568578119b16a1b95",
    "scratch": str(SCRATCH),
    "tmpdir": str(TMP),
    "cells": CELLS,
    "grid_timeout_s": GRID_TIMEOUT,
    "argv": [sys.executable, str(Path(__file__).resolve())],
    "inputs": {
        "mutator": {"path": str(MUTATOR), "sha256": sha256_file(MUTATOR)},
        "grid": {"path": str(GRID), "sha256": sha256_file(GRID)},
        "pristine_auditor": {"path": str(PRISTINE),
                             "sha256": sha256_file(PRISTINE)},
        "expectations_manifest": {"path": str(EXPECT),
                                  "sha256": sha256_file(EXPECT)},
    },
}

# ---- 1. resolve the EXACT registered operator -------------------------
registered = [m for m in pm.MUTANTS if m["id"] == MUTANT_ID]
record["operator_resolved"] = bool(registered)
if not registered:
    print(json.dumps(record, indent=1))
    sys.exit(2)
mutant = registered[0]
record["operator"] = {
    "id": mutant["id"],
    "semantic": mutant["semantic"],
    "expect_rows": mutant["expect_rows"],
    "execution": mutant["execution"],
    "attribution_basis": mutant["attribution_basis"],
    "alternative_count": len(mutant["alternatives"]),
}

# ---- 2. unique applicability (same counting as --anchors) --------------
source = PRISTINE.read_text(encoding="utf-8")
counts = []
for alt in mutant["alternatives"]:
    if alt["kind"] == "replace":
        n = source.count(alt["old"])
    elif alt["kind"] == "regex":
        n = len(re.findall(alt["pattern"], source, re.DOTALL))
    else:
        n = source.count(alt["anchor"])
    counts.append({"kind": alt["kind"], "matches": n})
applicable = [i for i, c in enumerate(counts) if c["matches"] == 1]
record["applicability"] = {
    "alternatives": counts,
    "applicable": applicable,
    "each_alternative_matches_exactly_once":
        all(c["matches"] == 1 for c in counts),
    "canonical_selection_rule": "the pinned apply_mutation returns the "
                                "first applicable alternative in registry "
                                "order (same rule as --anchors "
                                "applicable_alternative = applicable[0])",
}
if not applicable:
    print(json.dumps(record, indent=1))
    sys.exit(2)

# ---- 3. apply the registered operator, check compilation ---------------
mutated, applied_index = pm.apply_mutation(source, mutant)
record["apply_mutation"] = {
    "applied_alternative_index": applied_index,
    "mutated_is_none": mutated is None,
    "is_canonical_first_applicable": applied_index == applicable[0],
}
if mutated is None:
    print(json.dumps(record, indent=1))
    sys.exit(2)
compiles = pm.compiles(mutated, mutant["id"])
record["apply_mutation"]["mutant_compiles"] = compiles
if not compiles:
    print(json.dumps(record, indent=1))
    sys.exit(2)
MUTANT_FILE = OUT / "mutant-report-landing-audit.py"
MUTANT_FILE.write_text(mutated, encoding="utf-8")
record["apply_mutation"]["mutant_path"] = str(MUTANT_FILE)
record["apply_mutation"]["mutant_sha256"] = sha256_file(MUTANT_FILE)
record["apply_mutation"]["mutant_bytes"] = len(
    MUTANT_FILE.read_bytes())
record["apply_mutation"]["pristine_bytes"] = len(PRISTINE.read_bytes())
# the applied delta, verbatim (small)
import difflib
diff = list(difflib.unified_diff(source.splitlines(True),
                                 mutated.splitlines(True),
                                 fromfile="pristine",
                                 tofile="mutant", n=1))
record["apply_mutation"]["diff"] = "".join(diff)

# ---- 4. bounded grid runs: pristine and mutated, same cells ------------
runs = {}
for label, auditor in (("pristine", PRISTINE), ("mutated", MUTANT_FILE)):
    rc, rows, err, doc = pm.run_grid(GRID, auditor, "current", CELLS,
                                      GRID_TIMEOUT)
    row_out = []
    for r in rows:
        d = pm.row_detail(r)
        d["class"] = pm.classify_row(r)
        d["graded"] = pm.graded(r)
        d["violated"] = (r.get("met") is False
                         or r.get("twin_equal") is False)
        row_out.append(d)
    runs[label] = {
        "grid_exit": rc,
        "stderr": err,
        "auditor_sha256": sha256_file(auditor),
        "grid_sha256_reported": doc.get("grid_sha256"),
        "expectations_sha256_reported": doc.get("expectations_sha256"),
        "population_sha256": doc.get("population_sha256"),
        "population_size": doc.get("population_size"),
        "harness_fault": pm.harness_fault(doc, rows, err),
        "rows": row_out,
        "violated_rows": [pm.row_name(r) for r in pm.violated_rows(rows)],
        "graded_row_names": sorted({pm.row_name(r) for r in rows
                                    if pm.graded(r)}),
    }
    (OUT / f"grid-{label}.json").write_text(
        json.dumps(doc, indent=1, sort_keys=True), encoding="utf-8")
record["runs"] = runs

# ---- 5. verdict --------------------------------------------------------
pristine_violated = runs["pristine"]["violated_rows"]
mutant_violated = runs["mutated"]["violated_rows"]
if runs["pristine"]["grid_exit"] != 0 or pristine_violated:
    record["verdict"] = "could-not-evaluate: pristine does not meet the grid"
elif runs["mutated"]["grid_exit"] == 2 or runs["mutated"]["harness_fault"]:
    record["verdict"] = "could-not-evaluate: mutated run faulted"
elif mutant_violated:
    record["verdict"] = "killed"
else:
    record["verdict"] = "survived"

# ---- 6. restoration evidence ------------------------------------------
record["restoration"] = {
    "production_auditor_sha256": sha256_file(
        Path("/home/vgpnk/Projects/shokunin/kama-shokunin/tools/"
             "report-landing-audit.py")),
    "clone_pristine_auditor_sha256": sha256_file(PRISTINE),
    "expectations_manifest_sha256_after": sha256_file(EXPECT),
    "pristine_bytes_unchanged": (PRISTINE.read_bytes()
                                  == Path("/home/vgpnk/Projects/shokunin/"
                                          "kama-shokunin/tools/"
                                          "report-landing-audit.py")
                                  .read_bytes()),
}
(OUT / "probe-record.json").write_text(json.dumps(record, indent=1,
                                                  sort_keys=True),
                                         encoding="utf-8")
print(json.dumps(record, indent=1, sort_keys=True))
sys.exit(0)
