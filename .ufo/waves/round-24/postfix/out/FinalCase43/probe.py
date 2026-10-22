#!/usr/bin/env python3
"""FinalCase43 bounded probe: PG44-missing-unused-tree-promisor.

Uses the PINNED clone only (grid + auditor from the pinned commit).  Builds
the exact PG44 fixture with the pinned builder, then records:
  premise reality (is the unused tree really absent, really under the tip),
  the auditor's own two-root diagnosis sets (missing / opaque),
  the exit and document of the pinned auditor on that fixture,
  objects acquired before/after (no lazy fetch),
  function-level probes of the refusal gate: resolved / wrongtype citations
  keep their registered result, an unresolved citation is the only path that
  refuses.
No production writes: everything happens under this seat's scratch.
"""
import importlib.util
import json
import subprocess
import sys
from pathlib import Path

CLONE = Path("/fast/scratch/hyaku/kama-r24/postfix/FinalCase43/clone")
SCRATCH = Path("/fast/scratch/hyaku/kama-r24/postfix/FinalCase43")
ROOT = SCRATCH / "probe-root"
TMP = ROOT / "tmp"   # the fixture tree must live inside the grid root
OUT = SCRATCH / "out" / "probe.json"


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


G = load("promisor_grid", CLONE / "tests/report-audit/promisor-grid.py")
A = load("report_landing_audit", CLONE / "tools/report-landing-audit.py")

ev = {"pinned_commit": "92063cfc60e217fa7e2098c568578119b16a1b95",
      "grid_sha256": None, "auditor_sha256": None}


def sh(*a):
    return subprocess.run(a, capture_output=True, text=True).stdout


import hashlib
ev["grid_sha256"] = hashlib.sha256(
    (CLONE / "tests/report-audit/promisor-grid.py").read_bytes()).hexdigest()
ev["auditor_sha256"] = hashlib.sha256(
    (CLONE / "tools/report-landing-audit.py").read_bytes()).hexdigest()

ROOT.mkdir(parents=True, exist_ok=True)
TMP.mkdir(parents=True, exist_ok=True)

# ---- exact PG44 fixture, built by the pinned builder -------------------
built = G.BUILDERS["c_missing_unused_tree_promisor"](ROOT, TMP)
lane, fleet, shas = built["lane"], built["fleet"], built["shas"]
ev["premise"] = built["premise"]
ev["shas"] = {k: v for k, v in shas.items() if isinstance(v, str)}

unused_tree = shas.get("unused_tree")
ev["unused_tree_oid"] = unused_tree
# is the unused tree really absent (no lazy fetch)?
p = subprocess.run(["git", "--no-lazy-fetch", "-C", str(lane), "cat-file",
                    "-e", f"{unused_tree}^{{tree}}"], capture_output=True,
                   text=True, env=G.env())
ev["unused_tree_present"] = (p.returncode == 0)
ev["unused_tree_probe_stderr"] = p.stderr.strip()[:200]
# does the audited tip really reference it?
tip_tree = shas["tip_tree"]
p = subprocess.run(["git", "--no-lazy-fetch", "-C", str(lane), "cat-file",
                    "-p", tip_tree], capture_output=True, text=True,
                   env=G.env())
ev["tip_tree_listing"] = [l for l in p.stdout.split("\n") if "extra" in l]
ev["tip_tree_rc"] = p.returncode

# ---- the pinned auditor on that fixture --------------------------------
before = {"lane": G.object_inventory(lane), "fleet": G.object_inventory(fleet)}
code, out, err, timed_out = G.run_auditor(
    CLONE / "tools/report-landing-audit.py", lane, fleet, TMP, False)
after = {"lane": G.object_inventory(lane), "fleet": G.object_inventory(fleet)}
ev["auditor_run"] = {
    "argv": [sys.executable, "tools/report-landing-audit.py",
             "--lane-repo", str(lane), "--fleet-repo", str(fleet),
             "--rounds", "1", "--json", "--no-errata"],
    "exit": code, "timed_out": timed_out, "stderr": err.strip()[:500],
    "stdout_len": len(out),
    "objects_acquired": {k: sorted(after[k] - before[k]) for k in after},
}
try:
    doc = json.loads(out)
    ev["auditor_run"]["document"] = {
        "summary_status": doc["summary"]["status"],
        "defects": doc["summary"]["defects"],
        "uncorrected": doc["summary"]["uncorrected"],
        "by_kind": doc["summary"]["by_kind"],
        "results": [{"round": r["round"], "defects": r["defects"],
                     "required": r["required"],
                     "report_committed": r["report_committed"]}
                    for r in doc["results"]],
    }
except Exception as exc:  # noqa: BLE001
    ev["auditor_run"]["document_error"] = repr(exc)

# ---- the auditor's own two-root diagnosis ------------------------------
tip = A.resolve_branch(lane, "master")
fleet_tip = A.git(fleet, "rev-parse", "--verify", "HEAD^{commit}").strip()
stores = (A.build_store(lane, tip), A.build_store(fleet, fleet_tip))
lane_missing, lane_opaque = stores[0].missing()
fleet_missing, fleet_opaque = stores[1].missing()
ev["diagnosis"] = {
    "lane_root": tip,
    "fleet_root": fleet_tip,
    "lane_missing": sorted(lane_missing),
    "lane_opaque": sorted(lane_opaque),
    "fleet_missing": sorted(fleet_missing),
    "fleet_opaque": sorted(fleet_opaque),
    "unused_tree_in_lane_missing": unused_tree in lane_missing,
    "unused_tree_in_lane_opaque": unused_tree in lane_opaque,
}

# ---- function-level probes of the refusal gate -------------------------
probe = {}


def try_refuse(tag, status):
    try:
        A.refuse_unknown(1, status, stores)
        probe[tag] = {"raised": False}
    except A.EvalError as exc:
        probe[tag] = {"raised": True, "message": str(exc)[:300]}


resolved = A.lookup(stores, [shas["lane_commit"]])
probe["lookup_resolved_commit"] = resolved
try_refuse("refuse_resolved", resolved)

wrong = A.lookup(stores, [shas["f_blob"]], "^{commit}")
probe["lookup_wrongtype_blob_peeled"] = wrong
try_refuse("refuse_wrongtype", wrong)

absent = A.lookup(stores, [G.FAKE])
probe["lookup_absent_fabricated"] = absent
try_refuse("refuse_absent_fabricated", absent)

probe["unknown_citation_lookup"] = {
    "for_fake": A.unknown_citation(stores, G.FAKE) is not None,
    "for_unused_tree": A.unknown_citation(stores, unused_tree) is not None,
}
hole, hole_oid = A.opaque_hole(stores)
probe["opaque_hole"] = {"store": str(hole.path) if hole else None,
                         "oid": hole_oid}
ev["gate_probes"] = probe

OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(json.dumps(ev, indent=2, sort_keys=True), encoding="utf-8")
print(json.dumps(ev, indent=2, sort_keys=True))
