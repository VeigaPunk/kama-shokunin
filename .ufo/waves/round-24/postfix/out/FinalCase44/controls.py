#!/usr/bin/env python3
"""FinalCase44 control experiments (bounded, diagnostic).

Three local fixture variants built from the PINNED grid builder in my own
scratch.  These are NOT registered cells: they are new-source regression
controls that probe the two-root diagnosis clause of the assignment.

  C-A  PG45 fixture + a fabricated full-hash citation in Notes
       (unresolved citation) -> does the missing unused tree turn the
       audit into a refusal?
  C-B  PG45 fixture + a wrong-type (blob) landed citation
       -> a conclusive wrong-type must keep its registered finding even
       though an opaque hole exists.
  C-C  PG45 fixture unchanged, run TWICE -> determinism of the verdict
       document and of the no-acquisition observation.

Nothing here edits expectations, data or the manifest.  The auditor is the
pinned tools/report-landing-audit.py (sha256 b9be4f42...).
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


def run(label, opt, root):
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
    print(f"== {label} opt={opt}")
    print("   premise lane_missing:", built["premise"]["lane_missing"],
          "lane_promisor:", built["premise"]["lane_promisor"])
    print("   EXIT:", proc.returncode)
    print("   STDERR:", proc.stderr.decode().strip()[:400] or "(empty)")
    print("   stdout_is_json_document:", doc is not None)
    print("   defects:", json.dumps(defects))
    print("   status:", (doc or {}).get("summary", {}).get("status"))
    print("   objects_acquired:", json.dumps(acq))
    print("   ARGV:", " ".join(argv))
    return {"label": label, "exit": proc.returncode,
            "stderr": proc.stderr.decode().strip()[:400],
            "document": doc is not None, "defects": defects,
            "acquired": acq, "argv": argv}


root = Path(pg.make_root())
print("control_root:", root)
out = []
# C-A: missing unused tree + fabricated full-hash citation in Notes
out.append(run("C-A-unused-tree-plus-fabricated-notes",
               {"unused_tree": True, "fake_notes": True,
                "drop": ("unused_tree",)}, root))
# C-B: missing unused tree + conclusive wrong-type landed citation
out.append(run("C-B-unused-tree-plus-wrong-type",
               {"unused_tree": True, "wrong_type": True,
                "drop": ("unused_tree",)}, root))
# C-C: the PG45 fixture itself, twice
out.append(run("C-C-pg45-run1", {"unused_tree": True,
                                 "drop": ("unused_tree",)}, root))
out.append(run("C-C-pg45-run2", {"unused_tree": True,
                                 "drop": ("unused_tree",)}, root))
# C-D: control - missing unused tree with NOTHING unresolved and NO wrong type
#      but with the tree PRESENT (no drop): establishes that the drop is the
#      only difference between C-C and a hole-free lane.
out.append(run("C-D-complete-lane-plain-equivalent", {}, root))
Path("/fast/scratch/hyaku/kama-r24/postfix/FinalCase44/out/controls.json").write_text(
    json.dumps(out, indent=1, default=str), encoding="utf-8")
print("wrote controls.json")
