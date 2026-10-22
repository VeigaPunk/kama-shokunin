#!/usr/bin/env python3
"""FinalCase41 control: does an UNUSED missing blob change the verdict?

Two locally built fixtures from the PINNED grid builder, identical except
that the second keeps the notes/unused.txt blob that PG42 drops.  The pinned
auditor is run directly with the grid's own environment (no inherited GIT_*,
no user/system config).  Everything stays under this seat's scratch.
"""
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys

CLONE = Path("/fast/scratch/hyaku/kama-r24/postfix/FinalCase41/clone")
GRID = CLONE / "tests/report-audit/promisor-grid.py"
AUD = CLONE / "tools/report-landing-audit.py"
ROOT = Path("/fast/scratch/hyaku/kama-r24/postfix/FinalCase41/control")

spec = importlib.util.spec_from_file_location("pg", GRID)
pg = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pg)

variants = {
    "with_unused_hole": dict(unused_file=True, fake_notes=True,
                              drop=("unused_blob",)),
    "without_unused_hole": dict(unused_file=True, fake_notes=True),
}
out = {}
for name, opt in variants.items():
    tmp = ROOT / name
    tmp.mkdir(parents=True, exist_ok=True)
    built = pg.build(ROOT, tmp, **opt)
    before = {"lane": pg.object_inventory(built["lane"]),
              "fleet": pg.object_inventory(built["fleet"])}
    argv = [sys.executable, str(AUD), "--lane-repo", str(built["lane"]),
            "--fleet-repo", str(built["fleet"]), "--rounds", "1", "--json",
            "--no-errata"]
    proc = subprocess.run(argv, capture_output=True, env=pg.env(),
                          cwd=str(tmp), timeout=60)
    after = {"lane": pg.object_inventory(built["lane"]),
             "fleet": pg.object_inventory(built["fleet"])}
    doc = pg.normalise_document(proc.stdout.decode(errors="replace"), built)
    out[name] = {
        "argv": argv,
        "exit": proc.returncode,
        "stderr_tail": proc.stderr.decode(errors="replace").strip()[-400:],
        "stdout_bytes": len(proc.stdout),
        "acquired": {k: sorted(after[k] - before[k]) for k in after},
        "document": doc,
        "lane_commit": built["shas"].get("lane_commit"),
        "unused_blob": built["shas"].get("unused_blob"),
    }
out["_meta"] = {
    "auditor_sha256": hashlib.sha256(AUD.read_bytes()).hexdigest(),
    "grid_sha256": hashlib.sha256(GRID.read_bytes()).hexdigest(),
    "documents_equal": (out["with_unused_hole"]["document"]
                        == out["without_unused_hole"]["document"]),
}
print(json.dumps(out, indent=1, sort_keys=True))
