#!/usr/bin/env python3
"""FinalPM10 bounded probe.

Applies the EXACT registered operator PM10-ignore-opaque-nonleaf-missing
from the pinned mutator (tests/report-audit/promisor-mutants.py @ 92063cfc)
to a private copy of the pinned auditor (tools/report-landing-audit.py @ the
same commit), then runs ONLY the selected current-arm grid cells on the
pristine and the mutated auditor.  The mutator's own default/main
sensitivity path is NOT invoked (it runs the 47-cell pristine grid).

Everything written stays under this seat's scratch and out dir.
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
import os
import shutil
import sys
from pathlib import Path

SEAT = Path("/fast/scratch/hyaku/kama-r24/postfix/FinalPM10")
CLONE = SEAT / "clone"
OUT = SEAT / "out"
TMPROOT = SEAT / "tmp"
MUTATOR = CLONE / "tests/report-audit/promisor-mutants.py"
GRID = CLONE / "tests/report-audit/promisor-grid.py"
AUDITOR = CLONE / "tools/report-landing-audit.py"
MUTANT_ID = "PM10-ignore-opaque-nonleaf-missing"
CELLS = ["PG47-opaque-tree-with-unresolved-fabricated-token",
         "PG46-opaque-tree-hides-cited-blob"]
GRID_TIMEOUT = 600


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_mutator():
    spec = importlib.util.spec_from_file_location("promisor_mutants", MUTATOR)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    TMPROOT.mkdir(parents=True, exist_ok=True)
    mut = load_mutator()

    # --- operator selection: exactly one registered operator, exactly the
    # named one; no re-anchoring, no retargeting.
    ids = [m["id"] for m in mut.MUTANTS]
    if ids.count(MUTANT_ID) != 1:
        print(f"could-not-evaluate: {MUTANT_ID} is not uniquely registered",
              file=sys.stderr)
        return 2
    spec = next(m for m in mut.MUTANTS if m["id"] == MUTANT_ID)
    if len(spec["alternatives"]) != 1:
        print("could-not-evaluate: the operator has more than one "
              "alternative", file=sys.stderr)
        return 2
    alt = spec["alternatives"][0]
    anchor = alt["anchor"]
    source = AUDITOR.read_text(encoding="utf-8")
    anchor_count = source.count(anchor)
    if anchor_count != 1:
        print(f"could-not-evaluate: the anchor occurs {anchor_count} times",
              file=sys.stderr)
        return 2

    mutated, alt_index = mut.apply_mutation(source, spec)
    if mutated is None:
        print(f"could-not-evaluate: {alt_index}", file=sys.stderr)
        return 2
    if not mut.compiles(mutated, MUTANT_ID):
        print("could-not-evaluate: the mutant does not compile", file=sys.stderr)
        return 2

    work = OUT / "work"
    work.mkdir(exist_ok=True)
    pristine_path = work / "report-landing-audit.pristine.py"
    mutant_path = work / "report-landing-audit.PM10.py"
    pristine_path.write_text(source, encoding="utf-8")
    mutant_path.write_text(mutated, encoding="utf-8")
    pristine_digest = sha256_file(pristine_path)
    mutant_digest = sha256_file(mutant_path)
    pinned_auditor_digest = sha256_file(AUDITOR)

    report = {
        "seat": "FinalPM10",
        "pin": "92063cfc60e217fa7e2098c568578119b16a1b95",
        "operator": MUTANT_ID,
        "operator_alternatives": len(spec["alternatives"]),
        "applied_alternative_index": alt_index,
        "anchor": anchor,
        "anchor_occurrences_in_pinned_auditor": anchor_count,
        "mutant_compiles": True,
        "expect_rows": spec["expect_rows"],
        "attribution_basis": spec["attribution_basis"],
        "cells_run_per_tool": CELLS,
        "arm": "current",
        "pinned_auditor_sha256": pinned_auditor_digest,
        "pristine_copy_sha256": pristine_digest,
        "mutant_sha256": mutant_digest,
        "pristine_bytes_identical_to_pinned": pristine_digest
        == pinned_auditor_digest,
        "grid_sha256": sha256_file(GRID),
        "mutator_sha256": sha256_file(MUTATOR),
        "expectations_manifest_sha256": sha256_file(
            CLONE / "tests/report-audit/promisor-grid-expectations.json"),
        "runs": [],
    }

    for label, path in (("pristine", pristine_path), ("mutant", mutant_path)):
        tmpdir = TMPROOT / f"{label}-grid"
        if tmpdir.exists():
            shutil.rmtree(tmpdir)
        tmpdir.mkdir(parents=True)
        os.environ["TMPDIR"] = str(tmpdir)
        rc, rows, err, doc = mut.run_grid(GRID, path, "current", CELLS,
                                          GRID_TIMEOUT)
        raw = OUT / f"grid-{label}.json"
        raw.write_text(json.dumps(doc, indent=1, sort_keys=True), encoding="utf-8")
        fault = mut.harness_fault(doc, rows, err)
        bad = mut.violated_rows(rows)
        graded_rows = [r for r in rows if mut.graded(r)]
        report["runs"].append({
            "tool": label,
            "tool_path": str(path),
            "tool_sha256": sha256_file(path),
            "tmpdir": str(tmpdir),
            "grid_argv": [sys.executable, str(GRID), "--arm", "current",
                          "--current", str(path), "--json",
                          "--case", CELLS[0], "--case", CELLS[1]],
            "grid_exit": rc,
            "grid_stderr": err,
            "harness_fault": fault,
            "graded_rows": len(graded_rows),
            "row_names": [mut.row_name(r) for r in rows],
            "violated_rows": [
                dict(mut.row_detail(r),
                     classification=mut.classify_row(r),
                     arm=r.get("arm"), case=r.get("case"),
                     kind=r.get("kind"), exit=r.get("exit"),
                     expected_exit=r.get("expected_exit"),
                     met=r.get("met"),
                     twin_equal=r.get("twin_equal"),
                     problems=r.get("problems"),
                     amended_problems=r.get("amended_problems"),
                     original_problems=r.get("original_problems"),
                     internal_error=r.get("internal_error"),
                     traceback=r.get("traceback"),
                     timed_out=r.get("timed_out"),
                     leaked=r.get("leaked"),
                     objects_acquired=r.get("objects_acquired"),
                     stderr_tail=r.get("stderr_tail"))
                for r in bad],
            "all_rows": [dict(mut.row_detail(r),
                              arm=r.get("arm"), case=r.get("case"),
                              kind=r.get("kind"), exit=r.get("exit"),
                              expected_exit=r.get("expected_exit"),
                              met=r.get("met"),
                              met_amended=r.get("met_amended"),
                              twin_equal=r.get("twin_equal"),
                              problems=r.get("problems"),
                              amended_problems=r.get("amended_problems"),
                              original_problems=r.get("original_problems"),
                              internal_error=r.get("internal_error"),
                              traceback=r.get("traceback"),
                              timed_out=r.get("timed_out"),
                              leaked=r.get("leaked"),
                              objects_acquired=r.get("objects_acquired"),
                              stderr_tail=r.get("stderr_tail"))
                          for r in rows],
            "doc_arm_summary": {
                k: v for k, v in (doc.get("arms", {}).get("current") or {}).items()
                if k != "rows"},
        })

    (OUT / "pm10-probe.json").write_text(
        json.dumps(report, indent=1, sort_keys=True), encoding="utf-8")
    print(json.dumps(report, indent=1, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
