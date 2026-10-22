#!/usr/bin/env python3
"""Re-run the candidate auditor on the kept fixtures and record the exact
exit code, stdout bytes and stderr text (the grid's exit-2 form check:
typed could-not-evaluate, no verdict document, content-derived reason)."""
import json
import subprocess
import sys
from pathlib import Path

BASE = Path("/fast/scratch/hyaku/kama-r24/falsify/CodeErrataBoundary")
AUDITOR = BASE / "tools/report-landing-audit.py"
out = {}
for arm in ("A1_control_pg34_plain",
            "A2_counterexample_unavailable_rescued",
            "A6_unavailable_correction_unselected_round",
            "A7_unavailable_correction_selected_round"):
    fx = BASE / "fx" / arm
    argv = [sys.executable, str(AUDITOR), "--lane-repo", str(fx / "lane"),
            "--fleet-repo", str(fx / "fleet"), "--rounds", "1", "--json"]
    p = subprocess.run(argv, capture_output=True, cwd=str(BASE))
    out[arm] = {"exit": p.returncode,
                "stdout_bytes": len(p.stdout),
                "stdout_is_json": p.stdout.strip().startswith(b"{"),
                "stderr": p.stderr.decode().strip()}
    print(arm, json.dumps(out[arm]), flush=True)
(BASE / "out" / "exit2_form.json").write_text(
    json.dumps(out, indent=1, sort_keys=True), encoding="utf-8")
