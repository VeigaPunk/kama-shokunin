#!/usr/bin/env python3
"""Bounded probe of the pinned promisor-grid builder for PG06.

Two questions, both answered from the pinned source only:
  A) Is the fleet's PRE-hydration absence genuinely established (a non-empty
     missing set that contains the report blob, computed before hydration)?
  B) Is that pre-hydration clause load-bearing for the FLEET path, or could
     the final hydrated emptiness stand in for it?  The negative control
     ignores the clone filter; the builder must then fail with the
     'initial-empty' clause (pre-hydration), never with 'still-missing'
     (post-hydration).

The pinned grid module is imported and monkeypatched in memory only; the
repository is never modified.
"""
import importlib.util
import json
import os
from pathlib import Path
import shutil
import sys

CLONE = Path("/fast/scratch/hyaku/kama-r24/postfix/FinalCase06/clone")
GRID = CLONE / "tests/report-audit/promisor-grid.py"
ROOT = Path("/fast/scratch/hyaku/kama-r24/postfix/FinalCase06/exp/run")
LOG = Path("/fast/scratch/hyaku/kama-r24/postfix/FinalCase06/exp/probe.json")

spec = importlib.util.spec_from_file_location("pg_pinned", GRID)
pg = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pg)

orig_missing = pg.missing_objects
orig_hydrate = pg.hydrate
hydrated = set()
calls = []


def rec_missing(repo, r):
    m = orig_missing(repo, r)
    calls.append({"event": "missing_objects", "repo": str(repo), "root": r,
                  "hydrated_already": str(repo) in hydrated,
                  "n_missing": len(m), "missing": m})
    return m


def rec_hydrate(clone, origin):
    pre = orig_missing(clone, "HEAD")
    calls.append({"event": "hydrate_entry", "repo": str(clone),
                  "missing_at_hydration_entry": pre,
                  "n_missing": len(pre)})
    r = orig_hydrate(clone, origin)
    hydrated.add(str(clone))
    return r


pg.missing_objects = rec_missing
pg.hydrate = rec_hydrate

result = {"grid_sha256": __import__("hashlib").sha256(
    GRID.read_bytes()).hexdigest()}

if ROOT.exists():
    shutil.rmtree(ROOT)
ROOT.mkdir(parents=True)

# ---- A: the registered PG06 builder -------------------------------------
tmp = ROOT / "pg06"
built = pg.BUILDERS["c_hydrated_blobless_fleet"](ROOT, tmp)
report_blob = built["shas"]["report_blob"]
pre = [c for c in calls if c["event"] == "missing_objects"
       and not c["hydrated_already"] and c["repo"].endswith("/fleet")]
post = [c for c in calls if c["event"] == "missing_objects"
        and c["hydrated_already"] and c["repo"].endswith("/fleet")]
hyd = [c for c in calls if c["event"] == "hydrate_entry"]
result["A_pre_hydration_missing_calls"] = pre
result["A_post_hydration_missing_calls"] = post
result["A_hydrate_entries"] = hyd
result["A_report_blob"] = report_blob
result["A_pre_hydration_nonempty"] = bool(pre) and all(
    c["n_missing"] > 0 for c in pre)
result["A_report_blob_in_pre_missing"] = any(
    report_blob in c["missing"] for c in pre)
result["A_hydration_entry_still_missing_report_blob"] = any(
    report_blob in c["missing_at_hydration_entry"] for c in hyd)
result["A_post_hydration_empty"] = all(c["n_missing"] == 0 for c in post)
result["A_premise_fleet_missing"] = built["premise"]["fleet_missing"]
result["A_premise_lane_missing"] = built["premise"]["lane_missing"]
result["A_premise_fleet_promisor"] = built["premise"]["fleet_promisor"]
result["A_premise_lane_promisor"] = built["premise"]["lane_promisor"]

# ---- B: negative control, the FLEET filter ignored ------------------------
calls.clear()
neg = {"builder": "build(fleet_mark=config, blobless_fleet=True, "
                  "hydrate_fleet=True, complete_clone=True)"}
try:
    pg.build(ROOT, ROOT / "pg06-neg", fleet_mark="config",
             blobless_fleet=True, hydrate_fleet=True, complete_clone=True)
    neg["outcome"] = "NO VIOLATION: the builder accepted a complete clone "\
                     "as a hydrated blobless one"
    neg["contract_reason"] = None
except pg.ContractViolation as exc:
    neg["outcome"] = "ContractViolation"
    neg["contract_reason"] = exc.reason
    neg["message"] = str(exc)
except Exception as exc:  # noqa: BLE001 - recorded as-is
    neg["outcome"] = type(exc).__name__
    neg["contract_reason"] = None
    neg["message"] = str(exc)
neg["missing_calls"] = calls
neg["hydrate_called"] = any(c["event"] == "hydrate_entry" for c in calls)
result["B_negative_control"] = neg

LOG.write_text(json.dumps(result, indent=1, sort_keys=True) + "\n")
print(json.dumps({k: v for k, v in result.items()
                  if k not in ("A_pre_hydration_missing_calls",
                               "A_post_hydration_missing_calls",
                               "A_hydrate_entries")}, indent=1,
                 sort_keys=True))
print("---- pre-hydration fleet missing sets ----")
for c in result["A_pre_hydration_missing_calls"]:
    print(" ", c["root"], "n=", c["n_missing"], c["missing"])
print("---- hydrate entries ----")
for c in result["A_hydrate_entries"]:
    print(" ", c["repo"], "missing_at_entry=", c["missing_at_hydration_entry"])
print("---- post-hydration fleet missing sets ----")
for c in result["A_post_hydration_missing_calls"]:
    print(" ", c["root"], "n=", c["n_missing"], c["missing"])
sys.exit(0)
