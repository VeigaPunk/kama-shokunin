#!/usr/bin/env python3
"""Independent manual probe for FinalCase44 (PG45-missing-unused-tree-plain).

Bounded: ONE fixture (the PG45 builder), the pinned current auditor only.
No grid grading, no full grid, no other cells.

Establishes, from the fixture's own bytes:
  P1 premise: the unused subtree is genuinely absent from the lane store
     and the lane is not promisor-marked (plain control).
  P2 the two-root diagnosis really OBSERVED the hole (opaque non-empty),
     so a clean verdict is a decision, not an invisible hole.
  P3 the audit read the tip commit/tree and did NOT need the hole.
  P4 objects_acquired == {} (no lazy fetch, no acquisition).
  P5 the only citation resolves locally.
"""
import importlib.util
import json
import os
import subprocess
import sys
from pathlib import Path

CLONE = Path("/fast/scratch/hyaku/kama-r24/postfix/FinalCase44/clone")
SCRATCH = Path("/fast/scratch/hyaku/kama-r24/postfix/FinalCase44/probe")
GRID = CLONE / "tests/report-audit/promisor-grid.py"
AUDIT = CLONE / "tools/report-landing-audit.py"

spec = importlib.util.spec_from_file_location("pgrid", GRID)
pg = importlib.util.module_from_spec(spec)
sys.modules["pgrid"] = pg
spec.loader.exec_module(pg)

SCRATCH.mkdir(parents=True, exist_ok=True)
root = Path(pg.make_root())
print("grid_root:", root)
built = pg.BUILDERS["c_missing_unused_tree_plain"](root, root / "case")
lane = built["lane"]
fleet = built["fleet"]
shas = built["shas"]
print("built lane:", lane, "fleet:", fleet)

premise = built["premise"]
print("PREMISE:", json.dumps(premise, indent=1, default=str))

# P1: the unused tree is really gone; the lane is not promisor-marked
oid = shas["unused_tree"]
probe = subprocess.run(
    ["git", "--no-lazy-fetch", "--no-replace-objects", "-C", str(lane),
     "cat-file", "-e", oid + "^{object}"], capture_output=True)
print("P1 unused_tree oid:", oid, "present:", probe.returncode == 0,
      "(expect False)")
facts = pg.promisor_facts(lane)
print("P1 lane promisor_facts:", json.dumps(facts, default=str))
cfg = subprocess.run(["git", "-C", str(lane), "config", "--list"],
                     capture_output=True).stdout.decode()
print("P1 lane config:", repr(cfg))

# P2: the auditor's own two-root diagnosis, observed directly
sys.path.insert(0, str(CLONE / "tools"))
import importlib.util as iu
aspec = iu.spec_from_file_location("audit", AUDIT)
aud = iu.module_from_spec(aspec)
aspec.loader.exec_module(aud)

tip = subprocess.run(["git", "-C", str(lane), "rev-parse", "refs/heads/master"],
                     capture_output=True).stdout.decode().strip()
missing, opaque = aud.missing_reachable(lane, tip)
print("P2 lane tip:", tip)
print("P2 missing(store-wide walk):", sorted(missing))
print("P2 opaque(root-scoped walk):", sorted(opaque))
print("P2 opaque contains the unused tree:",
      oid in opaque or any(o.startswith(oid) for o in opaque))
print("P2 opaque_hole(stores)->", aud.opaque_hole(
    (aud.build_store(lane, tip), aud.build_store(fleet, "HEAD"))))
print("P2 unknown_citation for the cited tip:",
      aud.unknown_citation(
          (aud.build_store(lane, tip), aud.build_store(fleet, "HEAD")), tip))

# P3/P4/P5: run the pinned current auditor on the fixture
before = {k: pg.object_inventory(v) for k, v in (("lane", lane),
                                                ("fleet", fleet))}
argv = [sys.executable, str(AUDIT), "--lane-repo", str(lane),
        "--fleet-repo", str(fleet), "--rounds", "1", "--json", "--no-errata"]
proc = subprocess.run(argv, capture_output=True, cwd=str(SCRATCH),
                      env=pg.env(), timeout=60)
after = {k: pg.object_inventory(v) for k, v in (("lane", lane),
                                               ("fleet", fleet))}
acq = {k: sorted(after[k] - before[k]) for k in after}
print("ARGV:", " ".join(argv))
print("EXIT:", proc.returncode)
print("STDOUT:", proc.stdout.decode()[:2000])
print("STDERR:", proc.stderr.decode()[:2000])
print("P4 objects_acquired:", json.dumps(acq))
doc = None
try:
    doc = json.loads(proc.stdout.decode())
except ValueError:
    pass
print("P5 document status:",
      json.dumps(doc["summary"], sort_keys=True) if doc else "NO DOCUMENT")
print("P5 defects:",
      json.dumps([d for r in (doc or {}).get("results", [])
                  for d in r.get("defects", [])]))
print("git version:", subprocess.run(["git", "--version"],
                                     capture_output=True).stdout.decode().strip())
print("audit sha256:", subprocess.run(
    ["sha256sum", str(AUDIT)], capture_output=True).stdout.decode().split()[0])
print("grid sha256:", subprocess.run(
    ["sha256sum", str(GRID)], capture_output=True).stdout.decode().split()[0])
