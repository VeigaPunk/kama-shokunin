#!/usr/bin/env python3
"""FinalCase17 control probe (NOT a graded cell).

Single-variable control for the PG17 refusal: the same promisor-marked
fleet with NOTHING dropped must not refuse.  This shows the PG17 exit-2
refusal is caused by the dropped required report blob and not by the
promisor metadata, and that a complete marked fleet and its unmarked twin
still agree on the verdict document.

Premises: c_complete_fleet_config (fleet_mark=config, nothing dropped) and
c_complete_fleet_plain (nothing dropped, no mark).  Both are built with the
pinned grid's own builder.  No grid cell is executed by this script.
"""
import importlib.util
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

CLONE = Path("/fast/scratch/hyaku/kama-r24/postfix/FinalCase17/clone")
GRID = CLONE / "tests/report-audit/promisor-grid.py"
AUDIT = CLONE / "tools/report-landing-audit.py"

spec = importlib.util.spec_from_file_location("pggrid2", GRID)
grid = importlib.util.module_from_spec(spec)
spec.loader.exec_module(grid)


def run_case(builder, name, root):
    tmp = root / name
    tmp.mkdir(parents=True, exist_ok=True)
    built = grid.BUILDERS[builder](root, tmp)
    before = {k: sorted(grid.object_inventory(built[k]))
              for k in ("lane", "fleet")}
    argv = [sys.executable, str(AUDIT), "--lane-repo", str(built["lane"]),
            "--fleet-repo", str(built["fleet"]), "--rounds", "1", "--json",
            "--no-errata"]
    proc = subprocess.run(argv, capture_output=True, env=grid.env(),
                          cwd=str(tmp), timeout=60)
    after = {k: sorted(grid.object_inventory(built[k]))
             for k in ("lane", "fleet")}
    out = proc.stdout.decode(errors="replace")
    err = proc.stderr.decode(errors="replace")
    doc = None
    try:
        doc = json.loads(out)
    except ValueError:
        doc = None
    norm = None
    if doc is not None:
        norm = json.loads(json.dumps(doc, sort_keys=True)
                          .replace(str(built["fleet"]), "<fleet>")
                          .replace(str(built["lane"]), "<lane>"))
    defects = None
    if doc is not None:
        defects = doc.get("results", [{}])[0].get("defects")
    return {"case": name, "builder": builder, "argv": argv,
            "exit": proc.returncode,
            "stdout_bytes": len(out), "stderr": err[:600],
            "document": norm, "defects": defects,
            "objects_acquired": {k: sorted(set(after[k]) - set(before[k]))
                                 for k in after}}


def main():
    root = Path(tempfile.mkdtemp(prefix="fc17-control-",
                                  dir=os.environ["TMPDIR"]))
    marked = run_case("c_complete_fleet_config", "complete-promisor", root)
    plain = run_case("c_complete_fleet_plain", "complete-plain", root)
    verdict = {"grid_root": str(root),
               "cases": [marked, plain],
               "twin_comparison": {
                   "note": "both premises are complete: a verdict document "
                           "exists in both, so document equality IS the "
                           "declared comparable identity here",
                   "documents_present": [marked["document"] is not None,
                                         plain["document"] is not None],
                   "documents_equal": (marked["document"] is not None
                                       and marked["document"]
                                       == plain["document"]),
                   "exits": [marked["exit"], plain["exit"]],
               }}
    print(json.dumps(verdict, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
