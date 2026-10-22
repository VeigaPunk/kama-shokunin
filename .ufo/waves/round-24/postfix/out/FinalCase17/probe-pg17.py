#!/usr/bin/env python3
"""FinalCase17 manual probe: PG17 (promisor) and PG18 (plain twin) premises,
rebuilt with the PINNED grid's own builders, then the PINNED auditor run
directly so the FULL stderr/stdout and the exit code are observable.

This is a probe, not a graded cell: the graded cells were executed once by
the pinned grid driver (grid-pg17-pg18.stdout.json).

Rules honoured: the fixture origins stay in place, no origin is deleted or
repointed, git runs with the grid's own isolation (no inherited GIT_*,
GIT_CONFIG_GLOBAL=/dev/null), and the object inventory is taken before and
after every auditor run.
"""
import hashlib
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

spec = importlib.util.spec_from_file_location("pggrid", GRID)
grid = importlib.util.module_from_spec(spec)
spec.loader.exec_module(grid)


def probe(builder, name, root):
    tmp = root / name
    tmp.mkdir(parents=True, exist_ok=True)
    built = grid.BUILDERS[builder](root, tmp)
    lane, fleet = built["lane"], built["fleet"]
    before = {k: sorted(grid.object_inventory(built[k]))
              for k in ("lane", "fleet")}
    argv = [sys.executable, str(AUDIT), "--lane-repo", str(lane),
            "--fleet-repo", str(fleet), "--rounds", "1", "--json",
            "--no-errata"]
    proc = subprocess.run(argv, capture_output=True, env=grid.env(),
                          cwd=str(tmp), timeout=60)
    after = {k: sorted(grid.object_inventory(built[k]))
             for k in ("lane", "fleet")}
    acquired = {k: sorted(set(after[k]) - set(before[k])) for k in after}
    shas = built["shas"]
    err = proc.stderr.decode(errors="replace")
    out = proc.stdout.decode(errors="replace")
    remotes = {
        "lane": grid.git(lane, "remote", "-v").strip(),
        "fleet": grid.git(fleet, "remote", "-v").strip(),
    }
    fleet_config = grid.git(fleet, "config", "--local", "--list").strip()
    return {
        "case": name,
        "builder": builder,
        "argv": argv,
        "exit": proc.returncode,
        "stdout_bytes": len(out),
        "stdout_repr": out[:400],
        "stderr_full": err,
        "stderr_len": len(err),
        "stderr_starts_with_cne": err.startswith("could-not-evaluate:"),
        "stderr_has_internal": "could-not-evaluate: internal:" in err,
        "stderr_has_metadata_refusal": ("partial clone (" in err
                                         or "promisor pack" in err),
        "stderr_names_report_path": ".ufo/reports/round-1/kama.md" in err,
        "stderr_names_report_blob_oid": bool(shas.get("report_blob")) and
                                        shas["report_blob"] in err,
        "report_blob_oid": shas.get("report_blob"),
        "fleet_tip_tree_oid": shas.get("fleet_tip_tree"),
        "objects_acquired": acquired,
        "lane_objects_before_after": [len(before["lane"]), len(after["lane"])],
        "fleet_objects_before_after": [len(before["fleet"]),
                                       len(after["fleet"])],
        "remotes": remotes,
        "fleet_local_config": fleet_config,
        "tmp": str(tmp),
    }


def main():
    base = os.environ["TMPDIR"]
    root = Path(tempfile.mkdtemp(prefix="fc17-probe-", dir=base))
    results = []
    for builder, name in (("c_missing_fleet_report_promisor", "PG17"),
                          ("c_missing_fleet_report_plain", "PG18")):
        results.append(probe(builder, name, root))
    a, b = results
    same_exit = a["exit"] == b["exit"]
    strip = lambda s: s.replace(a["tmp"], "<tmp>").replace(b["tmp"], "<tmp>")
    same_reason = strip(a["stderr_full"]) == strip(b["stderr_full"])
    verdict = {
        "grid_root": str(root),
        "cases": results,
        "twin_comparison": {
            "note": "both arms REFUSE: no verdict document exists in either "
                    "arm, so document equality is not asserted and not "
                    "denied; the comparable identity is exit + refusal shape",
            "same_exit": same_exit,
            "same_stderr_modulo_paths": same_reason,
            "stderr_a": strip(a["stderr_full"]),
            "stderr_b": strip(b["stderr_full"]),
            "document_a": None,
            "document_b": None,
        },
    }
    print(json.dumps(verdict, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
