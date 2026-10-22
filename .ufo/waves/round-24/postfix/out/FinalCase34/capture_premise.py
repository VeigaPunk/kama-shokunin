#!/usr/bin/env python3
"""FinalCase34: capture premise + raw refusal evidence for the kept PG33/PG34
fixtures produced by the pinned grid (same argv as the grid's run_auditor)."""
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys

CLONE = Path("/fast/scratch/hyaku/kama-r24/postfix/FinalCase34/clone")
GRID = CLONE / "tests/report-audit/promisor-grid.py"
AUDITOR = CLONE / "tools/report-landing-audit.py"
ROOT = Path(sys.argv[1])
OUT = Path("/fast/scratch/hyaku/kama-r24/postfix/FinalCase34/out")

spec = importlib.util.spec_from_file_location("pg", GRID)
pg = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pg)

def _is_json(text):
    try:
        json.loads(text)
        return True
    except ValueError:
        return False


def _cited(text):
    import re
    return re.findall(r"\b[0-9a-f]{40}\b", text)


cases = {"000": "PG33-missing-cited-blob-promisor",
         "001": "PG34-missing-cited-blob-plain"}
report = {}
for d, name in sorted(cases.items()):
    base = ROOT / "current" / d
    lane, fleet = base / "lane", base / "fleet"
    premise = {
        "lane_promisor": pg.promisor_facts(lane),
        "fleet_promisor": pg.promisor_facts(fleet),
        "lane_missing_root": pg.missing_objects(lane, "refs/heads/master"),
        "fleet_missing_head": pg.missing_objects(fleet, "HEAD"),
        "lane_present_objects": len(pg.object_inventory(lane)),
        "fleet_present_objects": len(pg.object_inventory(fleet)),
        "lane_tip": pg.git(lane, "rev-parse", "HEAD").strip(),
        "fleet_head": pg.git(fleet, "rev-parse", "HEAD").strip(),
    }
    before = {"lane": pg.object_inventory(lane), "fleet": pg.object_inventory(fleet)}
    argv = [sys.executable, str(AUDITOR), "--lane-repo", str(lane),
            "--fleet-repo", str(fleet), "--rounds", "1", "--json", "--no-errata"]
    proc = subprocess.run(argv, capture_output=True, env=pg.env(), cwd=str(base))
    after = {"lane": pg.object_inventory(lane), "fleet": pg.object_inventory(fleet)}
    acquired = {k: sorted(after[k] - before[k]) for k in after}
    out = proc.stdout.decode(errors="replace")
    err = proc.stderr.decode(errors="replace")
    # the cited token in the report and the objects the lane actually lacks
    cited = pg.git(fleet, "show", f"HEAD:{pg.REL}").strip()
    report[name] = {
        "argv": argv, "cwd": str(base),
        "auditor_sha256": pg.hashlib.sha256(AUDITOR.read_bytes()).hexdigest(),
        "exit": proc.returncode,
        "stdout_raw": out, "stdout_bytes": len(out),
        "stdout_is_json": _is_json(out),
        "stderr_raw": err,
        "objects_acquired": acquired,
        "premise": premise,
        "report_text": cited,
        "cited_tokens": _cited(cited),
    }
    (OUT / f"raw-{name}.stdout.txt").write_text(out, encoding="utf-8")
    (OUT / f"raw-{name}.stderr.txt").write_text(err, encoding="utf-8")
(OUT / "premise-and-raw.json").write_text(
    json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
for name, r in report.items():
    print("==", name, "exit", r["exit"], "stdout_bytes", r["stdout_bytes"],
          "acquired", r["objects_acquired"])
    print("   stderr:", r["stderr_raw"].strip()[:500])
    print("   premise lane_missing_root:", r["premise"]["lane_missing_root"],
          "fleet_missing_head:", r["premise"]["fleet_missing_head"],
          "lane_promisor_backed:", r["premise"]["lane_promisor"]["promisor_backed"],
          "fleet_promisor_backed:", r["premise"]["fleet_promisor"]["promisor_backed"])
    print("   report:", r["report_text"].replace("\n", " | "))
