#!/usr/bin/env python3
"""FinalCase44: hole-type discrimination controls (C-E, C-F, C-G).

Question: is the PG45 clean verdict a PRINCIPLED token-scoped decision, or
a blanket "any hole is tolerated" gate?  These three fixtures hold the
CITATION constant (a fabricated unresolved token) and vary only the HOLE:

  C-E  missing BLOB (unused) + fabricated landed citation  -> PG37's shape
  C-F  missing TREE (unused) + fabricated landed citation
  C-G  missing TREE (unused) + fabricated NOTES citation   -> C-A's shape

If the auditor gates on hole TYPE (blob hole tolerated, tree hole gates),
the two-root diagnosis is principled.  If all three behave the same, the
verdict would be a blanket rule.

These are diagnostic new-source controls, NOT graded cells: built directly
from the pinned builder, run manually, no grid, no expectation edited.
"""
import importlib.util
import json
import subprocess
import sys
from pathlib import Path

CLONE = Path("/fast/scratch/hyaku/kama-r24/postfix/FinalCase44/clone")
GRID = CLONE / "tests/report-audit/promisor-grid.py"
AUDIT = CLONE / "tools/report-landing-audit.py"

spec = importlib.util.spec_from_file_location("pgrid", GRID)
pg = importlib.util.module_from_spec(spec)
sys.modules["pgrid"] = pg
spec.loader.exec_module(pg)

root = Path(pg.make_root())
print("control_root:", root)
results = []
for label, opt in (
    ("C-E-unused-BLOB-hole-plus-fabricated-landed",
     {"unused_file": True, "fake_landed": True,
      "drop": ("unused_blob",)}),
    ("C-F-unused-TREE-hole-plus-fabricated-landed",
     {"unused_tree": True, "fake_landed": True,
      "drop": ("unused_tree",)}),
    ("C-G-unused-TREE-hole-plus-fabricated-notes",
     {"unused_tree": True, "fake_notes": True,
      "drop": ("unused_tree",)}),
    ("C-H-no-hole-plus-fabricated-landed",
     {"fake_landed": True}),
):
    tmp = root / label
    built = pg.build(root, tmp, **opt)
    lane, fleet = built["lane"], built["fleet"]
    before = {k: pg.object_inventory(v) for k, v in (("lane", lane),
                                                    ("fleet", fleet))}
    argv = [sys.executable, str(AUDIT), "--lane-repo", str(lane),
            "--fleet-repo", str(fleet), "--rounds", "1", "--json",
            "--no-errata"]
    proc = subprocess.run(argv, capture_output=True, cwd=str(tmp),
                          env=pg.env(), timeout=60)
    after = {k: pg.object_inventory(v) for k, v in (("lane", lane),
                                                   ("fleet", fleet))}
    acq = {k: sorted(after[k] - before[k]) for k in after}
    doc = None
    try:
        doc = json.loads(proc.stdout.decode())
    except ValueError:
        pass
    defects = [d for r in (doc or {}).get("results", [])
               for d in r.get("defects", [])]
    # what the auditor's own two-root diagnosis sees in the lane
    tip = subprocess.run(["git", "-C", str(lane),
                           "rev-parse", "refs/heads/master"],
                          capture_output=True).stdout.decode().strip()
    sys.path.insert(0, str(CLONE / "tools"))
    import importlib.util as iu
    if "audit" not in sys.modules:
        aspec = iu.spec_from_file_location("audit", AUDIT)
        aud = iu.module_from_spec(aspec)
        sys.modules["audit"] = aud
        aspec.loader.exec_module(aud)
    aud = sys.modules["audit"]
    missing, opaque = aud.missing_reachable(lane, tip)
    print(f"== {label}")
    print("   premise lane_missing:", built["premise"]["lane_missing"])
    print("   diagnosis missing:", sorted(missing), "opaque:", sorted(opaque))
    print("   EXIT:", proc.returncode)
    print("   STDERR:", proc.stderr.decode().strip()[:300] or "(empty)")
    print("   document_present:", doc is not None, "defects:",
          json.dumps(defects))
    print("   status:", (doc or {}).get("summary", {}).get("status"))
    print("   objects_acquired:", json.dumps(acq))
    results.append({"label": label, "exit": proc.returncode,
                    "stderr": proc.stderr.decode().strip()[:300],
                    "document": doc is not None, "defects": defects,
                    "missing": sorted(missing), "opaque": sorted(opaque),
                    "acquired": acq})
Path("/fast/scratch/hyaku/kama-r24/postfix/FinalCase44/out/hole-controls.json"
     ).write_text(json.dumps(results, indent=1), encoding="utf-8")
print("wrote hole-controls.json")
