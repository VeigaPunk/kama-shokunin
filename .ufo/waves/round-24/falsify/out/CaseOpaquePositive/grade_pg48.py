#!/usr/bin/env python3
"""Exact grader verdict for PG48 under (a) the shipped auditor and
(b) the eager blanket-precondition probe, plus the precise PM11
expect_rows vs actually-failed-rows question.

Uses the shipped grader (promisor-grid.grade) so the verdict strings are
the grader's own, not a paraphrase.
"""
import importlib.util
import json
import os
import subprocess
import sys
from pathlib import Path

REPO = Path("/fast/scratch/hyaku/kama-r24/falsify/CaseOpaquePositive/repo")
SCRATCH = Path("/fast/scratch/hyaku/kama-r24/falsify/CaseOpaquePositive")


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


g = load(REPO / "tests/report-audit/promisor-grid.py", "pggrid")

table = json.loads(
    (REPO / "tests/report-audit/promisor-grid-expectations.json")
    .read_text(encoding="utf-8"))
case = next(c for c in table["cases"]
            if c["case"] == "PG48-opaque-unused-tree-no-unresolved-token")
live = case.get("amended", case["original"])
names = [g.resolve_token(n, {}) for n in case.get("names_any_of", [])]
forbidden = case.get("reason_forbidden", [])

env = dict(os.environ)
env["TMPDIR"] = str(SCRATCH / "tmp")


def run(auditor):
    p = subprocess.run(
        [sys.executable, str(REPO / "tests/report-audit/promisor-grid.py"),
         "--arm", "current", "--current", str(auditor),
         "--case", "PG48-opaque-unused-tree-no-unresolved-token", "--json"],
        capture_output=True, env=env, cwd=str(REPO), timeout=600)
    doc = json.loads(p.stdout.decode())
    row = doc["arms"]["current"]["rows"][0]
    # re-grade with the shipped grader to obtain the exact problem strings
    obs = {"arm": "current", "exit": row["exit"],
           "traceback": row["traceback"], "timed_out": row["timed_out"],
           "leaked": row["leaked"],
           "objects_acquired": row["objects_acquired"],
           "stderr_tail": row["stderr_tail"]}
    out = None
    if row["document"] is not None:
        out = json.dumps(row["document"])
    problems = g.grade(live, obs, row["stderr_tail"], out or "", {},
                       names, forbidden)
    return row, problems


row_a, prob_a = run(REPO / "tools/report-landing-audit.py")
row_b, prob_b = run(SCRATCH / "eager-blanket-audit.py")

print(json.dumps({
    "amended_expectation_for_PG48": live,
    "names_any_of": case.get("names_any_of", []),
    "reason_forbidden": forbidden,
    "shipped_auditor": {
        "exit": row_a["exit"], "met_amended": row_a["met_amended"],
        "grader_problems": prob_a,
        "stderr_tail": row_a["stderr_tail"][:200],
    },
    "eager_blanket_probe": {
        "exit": row_b["exit"], "met_amended": row_b["met_amended"],
        "grader_problems": prob_b,
        "stderr_tail": row_b["stderr_tail"][:300],
    },
    "grid_reporting_key_analysis": {
        "current_arm_amended_view_met_field": 0,
        "current_arm_amended_view_total_field": 1,
        "current_arm_amended_view_unmet_field": [],
        "current_arm_violations": 0,
        "current_arm_violating_cases": [],
        "per_row_met_amended": row_a["met_amended"],
        "note": "amended_view_* are computed from a frozen-arm-only filter, "
                "so on the current arm amended_view_met is always 0 while "
                "amended_view_unmet is always []",
    },
}, indent=1))
