#!/usr/bin/env python3
"""FinalCase41 mechanism probe: the two refusal roots, exercised directly.

Uses the PINNED auditor's own functions (missing_reachable / unknown_citation
/ opaque_hole) on the PG42 fixture and on the no-hole control, to show which
root (if any) fires for the fabricated token 0123...4567.
"""
import importlib.util
import json
from pathlib import Path

CLONE = Path("/fast/scratch/hyaku/kama-r24/postfix/FinalCase41/clone")
AUD = CLONE / "tools/report-landing-audit.py"
PG42_FIX = Path("/fast/scratch/hyaku/kama-r24/postfix/FinalCase41/tmp/"
                "promisor-grid-mb2e4lnc/current/000")
CONTROL = Path("/fast/scratch/hyaku/kama-r24/postfix/FinalCase41/control")

spec = importlib.util.spec_from_file_location("aud", AUD)
aud = importlib.util.module_from_spec(spec)
spec.loader.exec_module(aud)

FAKE = "0123456789abcdef0123456789abcdef01234567"


def probe(label, lane, fleet):
    lane = Path(lane).resolve()
    fleet = Path(fleet).resolve()
    tip = aud.resolve_branch(lane, "master")
    fleet_tip = aud.git(fleet, "rev-parse", "--verify", "HEAD^{commit}").strip()
    stores = (aud.build_store(lane, tip), aud.build_store(fleet, fleet_tip))
    detail = {}
    for name, store in zip(("lane", "fleet"), stores):
        missing, opaque = store.missing()
        detail[name] = {"root": store.root,
                        "missing_ids": sorted(missing),
                        "opaque_ids": sorted(opaque)}
    detail["unknown_citation(fake)"] = [
        s.path for s in [aud.unknown_citation(stores, FAKE)] if s is not None]
    hole, hole_oid = aud.opaque_hole(stores)
    detail["opaque_hole"] = {"store": str(hole.path) if hole else None,
                             "oid": hole_oid}
    detail["label"] = label
    return detail


out = {
    "PG42_grid_fixture": probe("PG42", PG42_FIX / "lane", PG42_FIX / "fleet"),
    "control_with_hole": probe("control-with-hole", CONTROL /
                               "with_unused_hole/lane",
                               CONTROL / "with_unused_hole/fleet"),
    "control_without_hole": probe("control-without-hole", CONTROL /
                                  "without_unused_hole/lane",
                                  CONTROL / "without_unused_hole/fleet"),
}
print(json.dumps(out, indent=1, sort_keys=True))
