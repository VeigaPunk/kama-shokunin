#!/usr/bin/env python3
"""Bounded probe of the pinned auditor's per-store lookup on the kept PG06
and PG08 fixtures.

Question: on a fleet store that carries promisor metadata but is complete,
and a lane store that does not hold the fleet-side objects, does the lookup
mistake ABSENCE in one store for UNREADABILITY in the other?

Evidence wanted, per store: the bare answer for the cited lane commit, the
peeled answer, and the store's own missing/opaque diagnosis.
"""
import importlib.util
import json
from pathlib import Path

CLONE = Path("/fast/scratch/hyaku/kama-r24/postfix/FinalCase06/clone")
AUDIT = CLONE / "tools/report-landing-audit.py"
ROOT = Path("/fast/scratch/hyaku/kama-r24/postfix/FinalCase06/tmp/run1/"
            "promisor-grid-c4oim7xz/current")

spec = importlib.util.spec_from_file_location("aud_pinned", AUDIT)
aud = importlib.util.module_from_spec(spec)
spec.loader.exec_module(aud)

out = {}
for cell in ("000", "001"):
    lane = ROOT / cell / "lane"
    fleet = ROOT / cell / "fleet"
    tip = aud.resolve_branch(lane, "master")
    fleet_tip = aud.git(fleet, "rev-parse", "--verify", "HEAD^{commit}").strip()
    stores = (aud.build_store(lane, tip), aud.build_store(fleet, fleet_tip))
    # the token the fixture report cites: the lane commit
    token = tip
    bare = {s.path.name: aud.bare_objects(s, [token])[token][0] for s in stores}
    status = aud.lookup(stores, [token], "^{commit}")
    miss = {s.path.name: {"missing": sorted(s.missing()[0]),
                          "opaque": sorted(s.missing()[1])} for s in stores}
    out[cell] = {
        "lane": str(lane), "fleet": str(fleet),
        "cited_token": token,
        "bare_state_per_store": bare,
        "lookup_status": status,
        "unknown_citation_store": (
            str(aud.unknown_citation(stores, token).path)
            if aud.unknown_citation(stores, token) else None),
        "opaque_hole": [str(aud.opaque_hole(stores)[0].path)
                        if aud.opaque_hole(stores)[0] else None,
                        aud.opaque_hole(stores)[1]],
        "store_diagnosis": miss,
    }
print(json.dumps(out, indent=1, sort_keys=True))
Path("/fast/scratch/hyaku/kama-r24/postfix/FinalCase06/exp/lookup_probe.json"
     ).write_text(json.dumps(out, indent=1, sort_keys=True) + "\n")
