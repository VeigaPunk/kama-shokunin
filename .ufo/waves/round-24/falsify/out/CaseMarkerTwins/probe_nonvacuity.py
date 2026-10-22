#!/usr/bin/env python3
"""MarkerTwins non-vacuity probe (benign offline fixture).

Question: is the current arm's exit 0 on PG03/PG04 content-derived, or does
a promisor-marked store get a blanket clean verdict ("marker -> always
clean")?

Method: build the PG03 shape (lane marked) and the PG07 shape (plain) with
the pinned grid's own builders, then amend ONLY the fleet report of a COPY
of each fixture so the Landed section cites a fabricated 40-hex token.  The
audit must then fail, identically in the marked and the plain shape.

Nothing in production is touched; no expected cell is changed; no network,
no transport, no execution payload.  Run with
  TMPDIR=/fast/scratch/hyaku/kama-r24/falsify/CaseMarkerTwins/tmp
"""
import importlib.util
import json
import shutil
import subprocess
import sys
from pathlib import Path

CLONE = Path("/fast/scratch/hyaku/kama-r24/falsify/CaseMarkerTwins")
spec = importlib.util.spec_from_file_location(
    "pg", CLONE / "tests/report-audit/promisor-grid.py")
pg = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pg)
AUDIT = str(CLONE / "tools/report-landing-audit.py")
FAKE = pg.FAKE
ROOT = CLONE / "probe-nonvacuity"


def build_probe(case, builder):
    tmp = ROOT / case
    tmp.mkdir(parents=True, exist_ok=True)
    b = pg.BUILDERS[builder](ROOT, tmp)
    work = tmp / "work"
    work.mkdir()
    shutil.copytree(b["lane"], work / "lane", symlinks=True)
    shutil.copytree(b["fleet"], work / "fleet", symlinks=True)
    rel = ".ufo/reports/round-1/kama.md"
    p = work / "fleet" / rel
    p.write_text(p.read_text() + f"- {FAKE}\n")
    pg.git(work / "fleet", "add", "--", rel)
    pg.git(work / "fleet", "-c", "commit.gpgsign=false", "commit", "-q",
           "-m", "round-1: report", GIT_AUTHOR_NAME="fleet",
           GIT_COMMITTER_NAME="fleet", GIT_AUTHOR_DATE="@2000 +0000",
           GIT_COMMITTER_DATE="@2000 +0000")
    before = {"lane": pg.object_inventory(work / "lane"),
              "fleet": pg.object_inventory(work / "fleet")}
    r = subprocess.run(
        [sys.executable, AUDIT, "--lane-repo", str(work / "lane"),
         "--fleet-repo", str(work / "fleet"), "--rounds", "1", "--json",
         "--no-errata"], capture_output=True, env=pg.env(), cwd=str(tmp))
    after = {"lane": pg.object_inventory(work / "lane"),
             "fleet": pg.object_inventory(work / "fleet")}
    doc = json.loads(r.stdout.decode()) if r.stdout.strip() else None
    return {"exit": r.returncode, "stderr": r.stderr.decode().strip()[:200],
            "defects": pg.observed_defects(r.stdout.decode())[0],
            "acquired": {k: sorted(after[k] - before[k]) for k in after},
            "summary": doc["summary"] if doc else None,
            "promisor_lane": pg.promisor_facts(work / "lane")["promisor_backed"],
            "promisor_fleet": pg.promisor_facts(work / "fleet")["promisor_backed"]}


def main():
    shutil.rmtree(ROOT, ignore_errors=True)
    ROOT.mkdir(parents=True)
    marked = build_probe("probe-marked", "c_complete_lane_marker")
    plain = build_probe("probe-plain", "c_complete_lane_plain")
    markedF = build_probe("probe-marked-fleet", "c_complete_fleet_marker")
    for n, r in (("marked lane (PG03 shape)", marked),
                 ("plain lane (PG07 shape)", plain),
                 ("marked fleet (PG04 shape)", markedF)):
        print(f"{n:26s} exit={r['exit']} promisor_lane={r['promisor_lane']} "
              f"promisor_fleet={r['promisor_fleet']} acquired={r['acquired']}")
        print(f"    defects={r['defects']}")
    print("lane-marked defect set == plain defect set:",
          marked["defects"] == plain["defects"])
    print("fleet-marked defect set == plain defect set:",
          markedF["defects"] == plain["defects"])
    print("kinds:", {k: v for k, v in marked["summary"]["by_kind"].items() if v})
    return 0


if __name__ == "__main__":
    sys.exit(main())
