#!/usr/bin/env python3
"""A/B the pinned candidate against the one-line errata-boundary correction.

Correction (scratch copy only; production is untouched):
  tools/report-landing-audit.py:583  invalid = [e for e in errata if e["kind"]
  in RESOLVABLE and (...)]
becomes
  invalid = [e for e in errata if e["round"] in selected and e["kind"] in
  RESOLVABLE and (...)]
i.e. errata-invalid is scoped to the audited rounds, exactly like
errata-unmatched (line 553) and like the refusal loop (line 563).
"""
import json
import subprocess
import sys
from pathlib import Path

BASE = Path("/fast/scratch/hyaku/kama-r24/falsify/CodeErrataBoundary")
PINNED = BASE / "tools/report-landing-audit.py"
FIXED = BASE / "out/audit.errata-scoped.py"
ARMS = ("A1_control_pg34_plain",
        "A2_counterexample_unavailable_rescued",
        "A3_pg29_errata_corrected_plain",
        "A4_pg30_errata_corrected_promisor",
        "A5_unselected_round_unresolvable_correction",
        "A6_unavailable_correction_unselected_round",
        "A7_unavailable_correction_selected_round")
rows = []
for arm in ARMS:
    fx = BASE / "fx" / arm
    row = {"arm": arm}
    for tag, auditor in (("pinned", PINNED), ("scoped", FIXED)):
        argv = [sys.executable, str(auditor), "--lane-repo", str(fx / "lane"),
                "--fleet-repo", str(fx / "fleet"), "--rounds", "1", "--json"]
        p = subprocess.run(argv, capture_output=True, cwd=str(BASE))
        row[tag] = {"exit": p.returncode,
                    "stdout_bytes": len(p.stdout),
                    "stderr": p.stderr.decode().strip()[:400]}
        try:
            doc = json.loads(p.stdout)
            row[tag]["summary"] = doc["summary"]
            row[tag]["uncorrected"] = sorted(
                (d["kind"], d["token"]) for r in doc["results"]
                for d in r["defects"] if not d.get("corrected_by"))
        except ValueError:
            row[tag]["summary"] = None
    rows.append(row)
    print(json.dumps(row, sort_keys=True), flush=True)
(BASE / "out" / "ab_pinned_vs_scoped.json").write_text(
    json.dumps(rows, indent=1, sort_keys=True), encoding="utf-8")
