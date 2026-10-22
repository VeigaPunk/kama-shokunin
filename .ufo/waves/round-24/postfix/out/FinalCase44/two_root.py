#!/usr/bin/env python3
"""FinalCase44: two-root structural probe + unselected-hole control.

The two-root diagnosis has two walks:
  W1 store-wide  (roots = EVERY present object)  -> `missing`
  W2 root-scoped (roots = the pinned root ONLY)  -> `opaque`
The design claim: an object referenced by a present object but NOT
reachable from the audited root is `missing` but NOT `opaque`, so it cannot
hide a cited name behind the audit's root and cannot gate the verdict.

U-1  unselected-branch hole (a blob on a branch the audit does not read)
     -> missing but NOT opaque; verdict clean; no refusal.
U-2  the unused-tree hole of PG45 -> missing AND opaque (it IS under the
     tip root), yet with no unresolved citation the verdict is clean:
     the opacity is only consulted on the unresolved-token path.
U-3  the SAME unused-tree hole with a resolved citation (PG45 itself)
     -> clean, byte-identical to a hole-free lane.
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

aspec = importlib.util.spec_from_file_location("audit", AUDIT)
aud = importlib.util.module_from_spec(aspec)
sys.modules["audit"] = aud
aspec.loader.exec_module(aud)

root = Path(pg.make_root())
print("control_root:", root)


def probe(label, opt, note):
    tmp = root / label
    built = pg.build(root, tmp, **opt)
    lane, fleet = built["lane"], built["fleet"]
    tip = subprocess.run(["git", "-C", str(lane), "rev-parse",
                           "refs/heads/master"],
                          capture_output=True).stdout.decode().strip()
    missing, opaque = aud.missing_reachable(lane, tip)
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
    print(f"== {label}  ({note})")
    print("   premise lane_missing:", built["premise"]["lane_missing"])
    print("   W1 store-wide missing:", sorted(missing))
    print("   W2 root-scoped opaque:", sorted(opaque))
    print("   missing-but-not-opaque (unreachable garbage):",
          sorted(set(missing) - set(opaque)))
    print("   EXIT:", proc.returncode)
    print("   STDERR:", proc.stderr.decode().strip()[:250] or "(empty)")
    print("   document_present:", doc is not None, "defects:",
          json.dumps(defects), "status:",
          (doc or {}).get("summary", {}).get("status"))
    print("   objects_acquired:", json.dumps(acq))
    return {"label": label, "exit": proc.returncode,
            "stderr": proc.stderr.decode().strip()[:250],
            "document": doc is not None, "defects": defects,
            "missing": sorted(missing), "opaque": sorted(opaque),
            "acquired": acq, "argv": argv}


res = []
res.append(probe("U-1-unselected-branch-hole",
                 {"unselected_hole": True, "drop": ("unselected_blob",)},
                 "blob on a branch the audit does not read"))
res.append(probe("U-2-unused-tree-hole-PG45",
                 {"unused_tree": True, "drop": ("unused_tree",)},
                 "the PG45 hole: under the tip root, so opaque"))
res.append(probe("U-3-hole-free-lane",
                 {}, "no hole at all: the reference verdict"))
Path("/fast/scratch/hyaku/kama-r24/postfix/FinalCase44/out/two-root.json"
     ).write_text(json.dumps(res, indent=1), encoding="utf-8")
print("wrote two-root.json")
