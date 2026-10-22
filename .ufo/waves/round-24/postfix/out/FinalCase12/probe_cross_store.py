#!/usr/bin/env python3
"""FinalCase12 out-of-grid control: does the per-store bare lookup / canonical
merge change the AUDIT's outcome when a citation exists in ONE store only?

Fixture: the plain lane (one commit l1) and a fleet whose round-1 report
cites l1 plus a blob that lives ONLY in the fleet.  The pinned auditor must
call that blob a proved local mismatch (a failed finding).  Mutant M1 (the
pre-commit merged-bare lookup) must instead mistake the LANE's absence for
an unreadable object and refuse.  Not a grid cell: an ad-hoc local fixture.
"""
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys

SCRATCH = Path("/fast/scratch/hyaku/kama-r24/postfix/FinalCase12")
CLONE = SCRATCH / "clone"
MYTMP = SCRATCH / "tmp"


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


pg = load("pg", CLONE / "tests/report-audit/promisor-grid.py")

root = Path(pg.tempfile.mkdtemp(prefix="fc12-cross-", dir=str(MYTMP)))
tmp = root / "case"
tmp.mkdir(parents=True, exist_ok=True)
built = pg.BUILDERS["c_omission_lane_plain"](root, tmp)
lane, fleet = built["lane"], built["fleet"]
l1 = built["shas"]["lane_commit"]

blob = pg.git(fleet, "hash-object", "-w", "--stdin",
              data=b"fleet only blob\n").strip()
text = pg.report_text([l1], [], landed_blob=blob)
Path(fleet, ".ufo/reports/round-1").mkdir(parents=True, exist_ok=True)
Path(fleet, ".ufo/reports/round-1/kama.md").write_text(text, encoding="utf-8")
pg.git(fleet, "add", "--", ".ufo/reports/round-1/kama.md")
pg.git(fleet, "-c", "commit.gpgsign=false", "commit", "-q", "-m",
       "round-1: report with a fleet-only blob",
       GIT_AUTHOR_NAME="fleet", GIT_COMMITTER_NAME="fleet",
       GIT_AUTHOR_DATE="@2100 +0000", GIT_COMMITTER_DATE="@2100 +0000")

report = {"root": str(root), "lane": str(lane), "fleet": str(fleet),
          "cited_lane_commit": l1, "fleet_only_blob": blob, "runs": {}}
for label, auditor in (
        ("pinned", CLONE / "tools/report-landing-audit.py"),
        ("M1-precommit-lookup",
         SCRATCH / "mutant-M1-precommit-lookup.py")):
    argv = [sys.executable, str(auditor), "--lane-repo", str(lane),
            "--fleet-repo", str(fleet), "--rounds", "1", "--json",
            "--no-errata"]
    p = subprocess.run(argv, capture_output=True, env=pg.env(),
                       cwd=str(tmp), timeout=120)
    out = p.stdout.decode(errors="replace")
    err = p.stderr.decode(errors="replace")
    doc = None
    try:
        doc = json.loads(out)
    except ValueError:
        pass
    report["runs"][label] = {
        "argv": argv, "exit": p.returncode,
        "stderr": err.strip(),
        "defects": sorted((d.get("kind"), d.get("token"))
                          for r in ((doc or {}).get("results", []))
                          for d in r.get("defects", [])),
        "summary": (doc or {}).get("summary"),
        "has_verdict_document": doc is not None,
    }

(SCRATCH / "out/cross-store-control.json").write_text(
    json.dumps(report, indent=1, sort_keys=False) + "\n", encoding="utf-8")
print(json.dumps(report, indent=1))
shutil.rmtree(root, ignore_errors=True)
