#!/usr/bin/env python3
"""FinalCase28 probe 2: clean diagnosis instrumentation + required-hole
positive control on the blobless/unhydrated lane surface.

Corrects probe 1's contamination: the positive control is taken AFTER the
audit-time invocation list is snapshotted, and every invocation records its
calling site.
"""
from __future__ import annotations

import contextlib
import importlib.util
import io
import json
import os
import subprocess
import sys
import traceback
from pathlib import Path

CLONE = Path("/fast/scratch/hyaku/kama-r24/postfix/FinalCase28/clone")
SCRATCH = Path("/fast/scratch/hyaku/kama-r24/postfix/FinalCase28/probe2")
AUDIT = CLONE / "tools" / "report-landing-audit.py"
GRID = CLONE / "tests" / "report-audit" / "promisor-grid.py"
KEEP = Path("/fast/scratch/hyaku/kama-r24/postfix/FinalCase28/tmp/"
            "promisor-grid-m0oxq6ay/current/000")
OUT = {}


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


pg = load(GRID, "pg_grid2")
aud = load(AUDIT, "pg_audit2")

# ------------------------------------------------- C2: diagnosis accounting
calls = []
orig_missing = aud.RepoStore.missing


def spy_missing(self):
    stack = [f"{f.name}:{f.lineno}" for f in traceback.extract_stack()[:-1]]
    calls.append({"path": str(self.path), "callers": stack[-4:]})
    return orig_missing(self)


aud.RepoStore.missing = spy_missing
unc_calls = []
orig_unc = aud.unknown_citation


def spy_unc(stores, token):
    res = orig_unc(stores, token)
    unc_calls.append({"token": token, "store": str(res.path) if res else None})
    return res


aud.unknown_citation = spy_unc
op_calls = []
orig_op = aud.opaque_hole


def spy_op(stores):
    res = orig_op(stores)
    op_calls.append({"store": str(res[0].path) if res[0] else None,
                     "oid": res[1]})
    return res


aud.opaque_hole = spy_op

lane, fleet = KEEP / "lane", KEEP / "fleet"
buf = io.StringIO()
with contextlib.redirect_stdout(buf):
    status = aud.main(["--lane-repo", str(lane), "--fleet-repo", str(fleet),
                       "--rounds", "1", "--json", "--no-errata"])
doc = json.loads(buf.getvalue())
audit_time_calls = list(calls)
audit_time_unc = list(unc_calls)
audit_time_op = list(op_calls)
# positive control AFTER the snapshot: ask the same lane explicitly
store = aud.build_store(lane, subprocess.run(
    ["git", "--no-lazy-fetch", "-C", str(lane), "rev-parse",
     "refs/heads/master^{commit}"], capture_output=True).stdout.decode().strip())
missing_set, opaque_set = store.missing()
OUT["C2_PG28_diagnosis_accounting"] = {
    "audit_exit": status,
    "audit_summary_status": doc["summary"]["status"],
    "audit_defects": doc["summary"]["defects"],
    "repo_store_missing_calls_during_audit": audit_time_calls,
    "repo_store_missing_called": bool(audit_time_calls),
    "unknown_citation_calls_during_audit": audit_time_unc,
    "opaque_hole_calls_during_audit": audit_time_op,
    "positive_control_missing_set": sorted(missing_set),
    "positive_control_opaque_set": sorted(opaque_set),
    "positive_control_note": "asked explicitly after the audit snapshot; the "
                             "hole exists and the audit never consulted it",
}

# --------- E2: absent citation on the same surface: registered result kept
root = SCRATCH
root.mkdir(parents=True, exist_ok=True)
tmp = root / "e2"
tmp.mkdir(parents=True, exist_ok=True)
calls.clear(); unc_calls.clear(); op_calls.clear()
built = pg.build(root, tmp, lane_mark="config", sources=False,
                 blobless_lane=True, fake_landed=True)
before = {"lane": pg.object_inventory(built["lane"]),
          "fleet": pg.object_inventory(built["fleet"])}
code, out, err, timed_out = pg.run_auditor(AUDIT, built["lane"], built["fleet"],
                                            tmp, False)
after = {"lane": pg.object_inventory(built["lane"]),
         "fleet": pg.object_inventory(built["fleet"])}
edoc = json.loads(out) if out.strip() else None
OUT["E2_absent_citation_blobless_surface"] = {
    "exit": code,
    "stderr": err[-400:],
    "timed_out": timed_out,
    "summary_status": edoc["summary"]["status"] if edoc else None,
    "defects": sorted((d["kind"], d["token"])
                       for r in (edoc["results"] if edoc else [])
                       for d in r["defects"]),
    "objects_acquired": {k: sorted(after[k] - before[k]) for k in after},
    "repo_store_missing_calls_during_audit": list(calls),
    "unknown_citation_calls_during_audit": list(unc_calls),
    "opaque_hole_calls_during_audit": list(op_calls),
}

# ------- F: required hole on the same surface: the refusal must be real
tmpf = root / "f1"
tmpf.mkdir(parents=True, exist_ok=True)
builtf = pg.build(root, tmpf, lane_mark="config", blobless_lane=True)
beforef = {"lane": pg.object_inventory(builtf["lane"]),
           "fleet": pg.object_inventory(builtf["fleet"])}
codef, outf, errf, tof = pg.run_auditor(AUDIT, builtf["lane"], builtf["fleet"],
                                        tmpf, False)
afterf = {"lane": pg.object_inventory(builtf["lane"]),
          "fleet": pg.object_inventory(builtf["fleet"])}
OUT["F_required_hole_on_blobless_surface"] = {
    "fixture_lane_missing": builtf["premise"]["lane_missing"],
    "fixture_lane_promisor": builtf["premise"]["lane_promisor"],
    "exit": codef,
    "stderr": errf.strip()[-400:],
    "stdout_len": len(outf),
    "stdout_has_verdict_document": bool(outf.strip()),
    "timed_out": tof,
    "objects_acquired": {k: sorted(afterf[k] - beforef[k]) for k in afterf},
}

print(json.dumps(OUT, indent=1, sort_keys=True))
