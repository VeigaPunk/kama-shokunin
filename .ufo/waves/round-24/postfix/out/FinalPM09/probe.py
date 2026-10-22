#!/usr/bin/env python3
"""FinalPM09 bounded falsification probe.

Applies the EXACT registered operator PM09-peel-bare-full-hash-lookup from
the pinned mutator (tests/report-audit/promisor-mutants.py @ 92063cfc) to a
private copy of the pinned auditor (tools/report-landing-audit.py), using the
mutator's own apply_mutation / compiles / run_grid APIs.  The mutator's
main() sensitivity path is NOT invoked (it runs the 47-cell pristine grid).

Bounded sample: 2 grid cells (PG44-missing-unused-tree-promisor and
PG39-wrong-type-citation-promisor) on the pristine copy and on the mutant.
"""
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

BASE = Path("/fast/scratch/hyaku/kama-r24/postfix/FinalPM09")
CLONE = BASE / "clone"
OUT = BASE / "out"
TMPROOT = BASE / "tmp"
MUTATOR = CLONE / "tests/report-audit/promisor-mutants.py"
GRID = CLONE / "tests/report-audit/promisor-grid.py"
AUDITOR = CLONE / "tools/report-landing-audit.py"
MUTANT_ID = "PM09-peel-bare-full-hash-lookup"
CASES = ["PG44-missing-unused-tree-promisor", "PG39-wrong-type-citation-promisor"]
TIMEOUT = 1800

OUT.mkdir(parents=True, exist_ok=True)
TMPROOT.mkdir(parents=True, exist_ok=True)


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


spec = importlib.util.spec_from_file_location("promisor_mutants_pinned", MUTATOR)
pm = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pm)

mutant = next(m for m in pm.MUTANTS if m["id"] == MUTANT_ID)
source = AUDITOR.read_text(encoding="utf-8")

# unique applicability, exactly as the mutator's own --anchors reports it
anchors = []
for alt in mutant["alternatives"]:
    if alt["kind"] == "replace":
        anchors.append({"kind": "replace", "matches": source.count(alt["old"]),
                        "old": alt["old"], "new": alt["new"]})
    elif alt["kind"] == "regex":
        import re
        anchors.append({"kind": "regex",
                        "matches": len(re.findall(alt["pattern"], source, re.DOTALL))})
    else:
        anchors.append({"kind": "insert", "matches": source.count(alt["anchor"])})
applicable = [i for i, a in enumerate(anchors) if a["matches"] == 1]

mutated, info = pm.apply_mutation(source, mutant)
compiled = pm.compiles(mutated, MUTANT_ID) if mutated is not None else False

pristine_copy = OUT / "pristine-auditor.py"
mutant_copy = OUT / "mutant-PM09-auditor.py"
shutil.copyfile(AUDITOR, pristine_copy)
pristine_copy.chmod(0o755)
if mutated is None:
    print(json.dumps({"verdict": "could-not-evaluate",
                      "reason": "the operator did not apply", "anchors": anchors},
                     indent=1))
    sys.exit(2)
mutant_copy.write_text(mutated, encoding="utf-8")
mutant_copy.chmod(0o755)

runs = {}
for label, auditor_path in (("pristine", pristine_copy), ("mutant", mutant_copy)):
    tmpdir = TMPROOT / f"{label}"
    if tmpdir.exists():
        shutil.rmtree(tmpdir)
    tmpdir.mkdir(parents=True)
    os.environ["TMPDIR"] = str(tmpdir)
    rc, rows, err, doc = pm.run_grid(GRID, auditor_path, "current", CASES, TIMEOUT)
    (OUT / f"grid-{label}.json").write_text(
        json.dumps(doc, indent=1, sort_keys=True), encoding="utf-8")
    (OUT / f"grid-{label}.stderr.txt").write_text(err, encoding="utf-8")
    fault = pm.harness_fault(doc, rows, err)
    cur = [r for r in rows if r.get("arm") == "current"]
    runs[label] = {
        "auditor": str(auditor_path),
        "auditor_sha256": sha(auditor_path),
        "argv": [sys.executable, str(GRID), "--arm", "current", "--current",
                 str(auditor_path), "--json", "--case", CASES[0], "--case", CASES[1]],
        "TMPDIR": str(tmpdir),
        "grid_exit": rc,
        "stderr": err,
        "harness_fault": fault,
        "grid_reported_auditor_sha256": (doc.get("auditor_sha256") or {}),
        "grid_reported_grid_sha256": doc.get("grid_sha256"),
        "grid_reported_expectations_sha256": doc.get("expectations_sha256"),
        "grid_reported_population_sha256": doc.get("population_sha256"),
        "grid_reported_population_size": doc.get("population_size"),
        "violations": doc.get("violations"),
        "rows": [dict(pm.row_detail(r), case=pm.row_name(r),
                      arm=r.get("arm"), kind=r.get("kind"),
                      met=r.get("met"), met_amended=r.get("met_amended"),
                      met_frozen=r.get("met_frozen"),
                      twin_equal=r.get("twin_equal"),
                      twins=r.get("twins"),
                      leaked=r.get("leaked"), timed_out=r.get("timed_out"),
                      traceback=r.get("traceback"),
                      internal_error=r.get("internal_error"))
                 for r in cur],
        "violated_rows": [dict(pm.row_detail(r), case=pm.row_name(r),
                               classification=pm.classify_row(r))
                          for r in pm.violated_rows(cur)],
    }
    os.environ.pop("TMPDIR", None)

result = {
    "seat": "FinalPM09",
    "mutant": MUTANT_ID,
    "operator": mutant["alternatives"],
    "expect_rows": mutant["expect_rows"],
    "attribution_basis": mutant["attribution_basis"],
    "source_commit": "92063cfc60e217fa7e2098c568578119b16a1b95",
    "pinned_digests": {
        "auditor": sha(AUDITOR), "grid": sha(GRID), "mutator": sha(MUTATOR),
        "expectations": sha(CLONE / "tests/report-audit/promisor-grid-expectations.json"),
    },
    "anchors": anchors,
    "applicable_alternatives": applicable,
    "applied_alternative": info,
    "mutant_compiles": compiled,
    "mutant_sha256": sha(mutant_copy),
    "pristine_copy_sha256": sha(pristine_copy),
    "cases": CASES,
    "runs": runs,
}
(OUT / "result.json").write_text(json.dumps(result, indent=1, sort_keys=True),
                                 encoding="utf-8")
print(json.dumps(result, indent=1, sort_keys=True))
