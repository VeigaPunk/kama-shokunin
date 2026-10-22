#!/usr/bin/env python3
"""Bounded PM11 falsification on the pinned source.

Drives the PINNED mutator's own APIs (apply_mutation / run_grid /
violated_rows / classify_row) on exactly two current-arm cells:
  PG48-opaque-unused-tree-no-unresolved-token   (primary target)
  PG47-opaque-tree-with-unresolved-fabricated-token (second declared
                                                    discriminator, in
                                                    PM11's expect_rows)

Runs: pristine auditor -> mutated auditor -> restored auditor (the pristine
bytes again).  No full grid, no 47-cell sensitivity path, no mutation of the
47-row expectation manifest.
"""
import hashlib
import importlib.util
import json
import os
import sys
from pathlib import Path

BASE = Path("/fast/scratch/hyaku/kama-r24/postfix/FinalPM11")
CLONE = BASE / "clone"
MUTATORS = CLONE / "tests/report-audit/promisor-mutants.py"
GRID = CLONE / "tests/report-audit/promisor-grid.py"
PRISTINE = BASE / "work/auditor-pristine.py"
MUTATED = BASE / "work/auditor-pm11.py"
CASES = ["PG48-opaque-unused-tree-no-unresolved-token",
         "PG47-opaque-tree-with-unresolved-fabricated-token"]
TIMEOUT = 600

spec = importlib.util.spec_from_file_location("pinned_mutants", MUTATORS)
mod = importlib.util.module_from_spec(spec)
sys.modules["pinned_mutants"] = mod
spec.loader.exec_module(mod)

mutant = [m for m in mod.MUTANTS if m["id"] == "PM11-any-hole-refusal"][0]


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def run(auditor, tag):
    tmp = BASE / f"tmp/{tag}"
    tmp.mkdir(parents=True, exist_ok=True)
    os.environ["TMPDIR"] = str(tmp)
    rc, rows, err, doc = mod.run_grid(GRID, auditor, "current", CASES,
                                       TIMEOUT)
    out = {
        "tag": tag,
        "auditor": str(auditor),
        "auditor_sha256": sha(auditor),
        "tmpdir": str(tmp),
        "argv": [sys.executable, str(GRID), "--arm", "current",
                 "--current", str(auditor), "--json"]
                + [x for c in CASES for x in ("--case", c)],
        "grid_rc": rc,
        "grid_stderr": err,
        "grid_exit_2": rc == 2,
        "doc_provenance": {k: doc.get(k) for k in
                           ("grid_sha256", "expectations_sha256",
                            "population_sha256", "population_size",
                            "auditor_sha256", "frozen_revision")},
        "rows": [],
    }
    for row in rows or []:
        out["rows"].append({
            "case": mod.row_name(row),
            "kind": row.get("kind"),
            "arm": row.get("arm"),
            "met": row.get("met"),
            "met_amended": row.get("met_amended"),
            "met_frozen": row.get("met_frozen"),
            "met_original": row.get("met_original"),
            "amended_problems": row.get("amended_problems"),
            "original_problems": row.get("original_problems"),
            "expected_exit": row.get("expected_exit"),
            "exit": row.get("exit"),
            "row_class": mod.classify_row(row),
            "kinds": row.get("kinds"),
            "expected_kinds": row.get("expected_kinds"),
            "defects": row.get("defects"),
            "twin": row.get("twin"),
            "twins": row.get("twins"),
            "objects_acquired": row.get("objects_acquired"),
            "stderr_tail": row.get("stderr_tail"),
            "document_is_none": row.get("document") is None,
        })
    bad = mod.violated_rows(rows or [])
    out["violated_rows"] = sorted({mod.row_name(r) for r in bad})
    out["violated_detail"] = [dict(mod.row_detail(r),
                                   case=mod.row_name(r),
                                   row_class=mod.classify_row(r))
                              for r in bad]
    out["harness_fault"] = mod.harness_fault(doc, rows or [], err)
    out["graded_rows_present"] = bool([r for r in (rows or [])
                                        if mod.graded(r)])
    return out


results = []
results.append(run(PRISTINE, "pristine"))
results.append(run(MUTATED, "mutated"))
results.append(run(PRISTINE, "restored"))

summary = {
    "pinned_commit": "92063cfc60e217fa7e2098c568578119b16a1b95",
    "mutator_sha256": sha(MUTATORS),
    "grid_sha256": sha(GRID),
    "expectations_sha256": sha(CLONE / "tests/report-audit/"
                                      "promisor-grid-expectations.json"),
    "pristine_auditor_sha256": sha(PRISTINE),
    "mutated_auditor_sha256": sha(MUTATED),
    "expectations_manifest_unchanged_after":
        sha(CLONE / "tests/report-audit/promisor-grid-expectations.json")
        == "d86b7bea9c49c3d2fcd026a3a1ffb502871d15a2c8db624eba9745e664f14cd1",
    "cases": CASES,
    "mutant_id": mutant["id"],
    "mutant_expect_rows": mutant["expect_rows"],
    "results": results,
}
print(json.dumps(summary, indent=1, sort_keys=True))
