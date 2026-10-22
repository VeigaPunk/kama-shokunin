#!/usr/bin/env python3
"""FinalPM02: bounded postfix falsification of the registered operator
PM02-blanket-unknown-refusal against the pinned source
92063cfc60e217fa7e2098c568578119b16a1b95.

The driver uses the pinned mutator's own library API (apply_mutation,
compiles, run_grid, harness_fault, violated_rows, expected_match) and never
its default/main sensitivity path: exactly two grid cells are selected, so
no 47-cell pristine grid is run.
"""
import hashlib
import importlib.util
import json
import os
import sys
from pathlib import Path

BASE = Path("/fast/scratch/hyaku/kama-r24/postfix/FinalPM02")
CLONE = BASE / "clone"
OUT = Path("/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/"
           "round-24/postfix/out/FinalPM02")
OUT.mkdir(parents=True, exist_ok=True)

MUT_PATH = CLONE / "tests/report-audit/promisor-mutants.py"
GRID = CLONE / "tests/report-audit/promisor-grid.py"
AUDIT = CLONE / "tools/report-landing-audit.py"
MANIFEST = CLONE / "tests/report-audit/promisor-grid-expectations.json"
MUT_ID = "PM02-blanket-unknown-refusal"
CASES = ["PG22-unknown-citation-incomplete-promisor",
         "PG37-unused-missing-blob-with-fabricated-citation-plain"]
TIMEOUT = 900


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def load_mutator():
    spec = importlib.util.spec_from_file_location("promisor_mutants_pin", MUT_PATH)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def row_summary(row):
    keep = ("case", "kind", "arm", "exit", "expected_exit", "met",
            "met_amended", "met_original", "met_frozen", "twin", "twins",
            "twin_equal", "defects", "kinds", "raw_kinds", "row_class",
            "stderr_tail", "internal_error", "timed_out", "leaked",
            "traceback", "objects_acquired", "expected_kinds")
    out = {k: row.get(k) for k in keep}
    out["problems_amended"] = row.get("amended_problems")
    out["problems_original"] = row.get("original_problems")
    out["expectation"] = row.get("expectation")
    return out


def main():
    mod = load_mutator()
    source = AUDIT.read_text(encoding="utf-8")
    mutants = {m["id"]: m for m in mod.MUTANTS}
    mutant = mutants[MUT_ID]

    applicability = []
    for alt in mutant["alternatives"]:
        if alt["kind"] == "insert":
            count = source.count(alt["anchor"])
        elif alt["kind"] == "replace":
            count = source.count(alt["old"])
        else:
            count = len(mod.re.findall(alt["pattern"], source, mod.re.DOTALL))
        applicability.append({"kind": alt["kind"], "matches": count,
                               "anchor": alt.get("anchor")
                               or alt.get("old") or alt.get("pattern")})

    mutated, applied = mod.apply_mutation(source, mutant)
    compiles = bool(mutated) and mod.compiles(mutated, MUT_ID)
    mut_path = BASE / "mutant" / f"{MUT_ID}.py"
    mut_path.parent.mkdir(parents=True, exist_ok=True)
    if mutated:
        mut_path.write_text(mutated, encoding="utf-8")

    report = {
        "seat": "FinalPM02",
        "pinned_commit": "92063cfc60e217fa7e2098c568578119b16a1b95",
        "clone": str(CLONE),
        "operator": MUT_ID,
        "operator_semantic": mutant["semantic"],
        "operator_expect_rows": mutant["expect_rows"],
        "operator_execution": mutant["execution"],
        "operator_alternatives": applicability,
        "applied_alternative": applied,
        "mutant_compiles": compiles,
        "cells_selected": CASES,
        "manifest_sha256_before": sha256(MANIFEST),
        "auditor_pristine_sha256": sha256(AUDIT),
        "grid_sha256": sha256(GRID),
        "mutator_sha256": sha256(MUT_PATH),
        "mutant_sha256": sha256(mut_path) if mutated else None,
        "runs": [],
    }

    phases = [("pristine", AUDIT), ("mutant", mut_path)]
    for label, auditor in phases:
        tmpdir = BASE / "tmp" / label
        tmpdir.mkdir(parents=True, exist_ok=True)
        os.environ["TMPDIR"] = str(tmpdir)
        rc, rows, err, doc = mod.run_grid(GRID, auditor, "current", CASES,
                                          TIMEOUT)
        fault = mod.harness_fault(doc, rows, err)
        (OUT / f"grid-{label}.json").write_text(
            json.dumps(doc, indent=1, sort_keys=True), encoding="utf-8")
        (OUT / f"grid-{label}.stderr.txt").write_text(
            (err or "") + "\n", encoding="utf-8")
        phase = {
            "phase": label,
            "auditor": str(auditor),
            "auditor_sha256": sha256(auditor),
            "argv": [sys.executable, str(GRID), "--arm", "current",
                     "--current", str(auditor), "--json"]
                     + [x for c in CASES for x in ("--case", c)],
            "TMPDIR": str(tmpdir),
            "grid_exit": rc,
            "grid_stderr": err,
            "harness_fault": fault,
            "grid_reported_auditor_sha256":
                (doc.get("auditor_sha256") or {}).get("current"),
            "grid_reported_grid_sha256": doc.get("grid_sha256"),
            "expectations_sha256": doc.get("expectations_sha256"),
            "population_sha256": doc.get("population_sha256"),
            "population_size": doc.get("population_size"),
            "arm_summary": {
                arm: {k: v for k, v in res.items() if k != "rows"}
                for arm, res in (doc.get("arms") or {}).items()},
            "violated_rows": sorted({mod.row_name(r)
                                     for r in mod.violated_rows(rows)}),
            "graded_rows_present": bool([r for r in rows if mod.graded(r)]),
            "rows": [row_summary(r) for r in rows],
        }
        report["runs"].append(phase)

    # per-row comparison between the pristine and the mutated arm
    by_phase = {p["phase"]: {r["case"]: r for r in p["rows"]}
                for p in report["runs"]}
    def cross_class(p_exit, m_exit):
        """The final exit taxonomy, on the observed pristine -> mutant exit."""
        if p_exit not in (0, 1, 2) or m_exit not in (0, 1, 2):
            return "unclassified"
        if p_exit in (0, 1) and m_exit == 2:
            return "refusal-2"
        if p_exit == 2 and m_exit in (0, 1):
            return "actual-verdict"
        if p_exit == m_exit:
            return ("diagnostic-only" if p_exit == 2
                    else "same-verdict-exit")
        return "verdict-change"

    comparison = []
    for case in CASES:
        pr = by_phase["pristine"].get(case, {})
        mu = by_phase["mutant"].get(case, {})
        pexp, mexp = pr.get("expected_exit"), mu.get("expected_exit")
        pex, mex = pr.get("exit"), mu.get("exit")
        klass = cross_class(pex, mex)
        comparison.append({
            "case": case,
            "kind": pr.get("kind"),
            "pristine": {"exit": pex, "expected_exit": pexp,
                         "met": pr.get("met"),
                         "twin_equal": pr.get("twin_equal"),
                         "twins": pr.get("twins"),
                         "defects": pr.get("defects"),
                         "kinds": pr.get("kinds"),
                         "stderr_tail": pr.get("stderr_tail"),
                         "internal_error": pr.get("internal_error"),
                         "timed_out": pr.get("timed_out"),
                         "leaked": pr.get("leaked"),
                         "traceback": pr.get("traceback"),
                         "objects_acquired": pr.get("objects_acquired")},
            "mutant": {"exit": mex, "expected_exit": mexp,
                       "met": mu.get("met"),
                       "twin_equal": mu.get("twin_equal"),
                       "twins": mu.get("twins"),
                       "defects": mu.get("defects"),
                       "kinds": mu.get("kinds"),
                       "stderr_tail": mu.get("stderr_tail"),
                       "internal_error": mu.get("internal_error"),
                       "timed_out": mu.get("timed_out"),
                       "leaked": mu.get("leaked"),
                       "traceback": mu.get("traceback"),
                       "objects_acquired": mu.get("objects_acquired")},
            "exit_class": klass,
            "pinned_tool_class_pristine": mod.classify_row(
                {"expected_exit": pexp, "exit": pex}),
            "pinned_tool_class_mutant": mod.classify_row(
                {"expected_exit": mexp, "exit": mex}),
            "graded_row_failed_in_mutant": (mu.get("met") is False),
            "twin_failed_in_mutant": (mu.get("twin_equal") is False),
            "row_in_operator_expect_rows":
                mod.expected_match(case, mutant["expect_rows"]),
        })
    report["comparison"] = comparison
    report["manifest_sha256_after"] = sha256(MANIFEST)
    report["manifest_unchanged"] = (report["manifest_sha256_before"]
                                    == report["manifest_sha256_after"])
    (OUT / "report.json").write_text(
        json.dumps(report, indent=1, sort_keys=True, default=str) + "\n",
        encoding="utf-8")
    if mutated:
        (OUT / "PM02-blanket-unknown-refusal.py").write_text(
            mutated, encoding="utf-8")
    print(json.dumps({k: v for k, v in report.items()
                      if k not in ("runs", "comparison")},
                     indent=1, sort_keys=True, default=str))
    for c in comparison:
        print(json.dumps(c, indent=1, sort_keys=True, default=str))
    return 0


if __name__ == "__main__":
    sys.exit(main())
