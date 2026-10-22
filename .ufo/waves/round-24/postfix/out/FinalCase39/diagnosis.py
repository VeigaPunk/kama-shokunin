#!/usr/bin/env python3
"""Show the PINNED auditor's own two-root diagnosis on the probe fixtures.

missing_reachable(repo, root) returns (missing, opaque):
  missing = ids that present local objects reference but cannot serve
            (store-wide walk: every present object is a root)
  opaque  = the non-leaf holes behind the audited root (root-scoped walk)
For each probe it states what the diagnosis SAW before the verdict was
formed, so "no refusal" is attributable to the citation being conclusive,
not to the hole being invisible.
"""
import importlib.util
import json
from pathlib import Path

CLONE = Path("/fast/scratch/hyaku/kama-r24/postfix/FinalCase39/clone")
spec = importlib.util.spec_from_file_location(
    "rla", CLONE / "tools/report-landing-audit.py")
R = importlib.util.module_from_spec(spec)
spec.loader.exec_module(R)

BASE = Path("/fast/scratch/hyaku/kama-r24/postfix/FinalCase39/tmp1")
out = []
for d in sorted(BASE.glob("probe-*")):
    lane = d / "case/lane"
    fleet = d / "case/fleet"
    if not lane.is_dir():
        continue
    lane_tip = R.git(lane, "rev-parse", "--verify", "refs/heads/master^{commit}").strip()
    fleet_tip = R.git(fleet, "rev-parse", "--verify", "HEAD^{commit}").strip()
    lm, lo = R.missing_reachable(str(lane), lane_tip)
    fm, fo = R.missing_reachable(str(fleet), fleet_tip)
    rec = {"probe": d.name, "lane_tip": lane_tip, "fleet_tip": fleet_tip,
           "lane_missing_storewide": sorted(lm),
           "lane_opaque_rootscoped": sorted(lo),
           "fleet_missing_storewide": sorted(fm),
           "fleet_opaque_rootscoped": sorted(fo)}
    out.append(rec)
    print(json.dumps(rec, sort_keys=True))
Path("/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-24/postfix/"
     "out/FinalCase39/probe-diagnosis.json").write_text(
    json.dumps(out, indent=1, sort_keys=True) + "\n", encoding="utf-8")
