#!/usr/bin/env python3
"""FinalCase28 bounded falsification probes for PG28-unhydrated-blobless-lane.

Everything is read-only against the pinned clone except the fixtures this
script builds under its own scratch.  No network, no lazy fetch (every git
read that could touch a promisor remote carries --no-lazy-fetch), origins are
kept in place.
"""
from __future__ import annotations

import contextlib
import hashlib
import importlib.util
import io
import json
import os
import subprocess
import sys
from pathlib import Path

CLONE = Path("/fast/scratch/hyaku/kama-r24/postfix/FinalCase28/clone")
SCRATCH = Path("/fast/scratch/hyaku/kama-r24/postfix/FinalCase28/probe")
AUDIT = CLONE / "tools" / "report-landing-audit.py"
GRID = CLONE / "tests" / "report-audit" / "promisor-grid.py"
KEEP = Path("/fast/scratch/hyaku/kama-r24/postfix/FinalCase28/tmp/"
            "promisor-grid-m0oxq6ay/current/000")

OUT = {}


def sha256(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def git(repo, *args, stdin=None):
    """Every call isolates lazy fetch and replace refs."""
    p = subprocess.run(["git", "--no-lazy-fetch", "--no-replace-objects",
                        "-C", str(repo), *args],
                       input=stdin, capture_output=True,
                       env={k: v for k, v in os.environ.items()
                            if not k.startswith("GIT_")})
    return p.returncode, p.stdout.decode(errors="replace"), \
        p.stderr.decode(errors="replace")


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


pg = load(GRID, "pg_grid")
aud = load(AUDIT, "pg_audit")

# ------------------------------------------------------------- A: premise
lane = KEEP / "lane"
fleet = KEEP / "fleet"
origin = KEEP / "lane-origin"
rc_cfg, cfg, _ = git(lane, "config", "--null", "--list")
facts = pg.promisor_facts(lane)
rc_missing, miss_out, _ = git(lane, "--no-lazy-fetch", "-c",
                              "core.commitGraph=false", "rev-list", "--objects",
                              "--missing=print", "--no-object-names",
                              "refs/heads/master")
lane_missing = sorted(l[1:] for l in miss_out.split("\n") if l.startswith("?"))
rc_fmiss, fmiss_out, _ = git(fleet, "--no-lazy-fetch", "-c",
                             "core.commitGraph=false", "rev-list", "--objects",
                             "--missing=print", "--no-object-names", "HEAD")
fleet_missing = sorted(l[1:] for l in fmiss_out.split("\n") if l.startswith("?"))
rc_url, url, _ = git(lane, "config", "--get", "remote.origin.url")
rc_o, origin_head, _ = git(origin, "rev-parse", "HEAD")
OUT["A_premise"] = {
    "kept_fixture": str(KEEP),
    "lane_promisor_backed": facts["promisor_backed"],
    "lane_promisor_facts": {k: v for k, v in facts.items() if k != "promisor_backed"},
    "lane_missing_no_lazy_fetch": lane_missing,
    "lane_missing_count": len(lane_missing),
    "fleet_missing_no_lazy_fetch": fleet_missing,
    "lane_remote_origin_url": url.strip(),
    "origin_present": origin.is_dir(),
    "origin_head": origin_head.strip(),
    "origin_reachable_local": rc_o == 0,
    "lane_worktree_empty_no_checkout": not any(lane.iterdir()),
    "auditor_sha256": sha256(AUDIT),
    "grid_sha256": sha256(GRID),
    "manifest_sha256": sha256(CLONE / "tests" / "report-audit" /
                               "promisor-grid-expectations.json"),
}

# ------------------------------------------------- B: direct auditor run
proc = subprocess.run([sys.executable, str(AUDIT), "--lane-repo", str(lane),
                       "--fleet-repo", str(fleet), "--rounds", "1", "--json",
                       "--no-errata"], capture_output=True)
OUT["B_direct_auditor"] = {
    "argv": [sys.executable, str(AUDIT), "--lane-repo", str(lane),
             "--fleet-repo", str(fleet), "--rounds", "1", "--json",
             "--no-errata"],
    "exit": proc.returncode,
    "stderr": proc.stderr.decode(errors="replace"),
    "stdout_sha256": hashlib.sha256(proc.stdout).hexdigest(),
    "stdout_len": len(proc.stdout),
}

# ------------------------- C: is the missing-object diagnosis a precondition?
asked = []
orig_missing = aud.RepoStore.missing


def spy_missing(self):
    asked.append(str(self.path))
    return orig_missing(self)


aud.RepoStore.missing = spy_missing
buf = io.StringIO()
with contextlib.redirect_stdout(buf):
    status = aud.main(["--lane-repo", str(lane), "--fleet-repo", str(fleet),
                        "--rounds", "1", "--json", "--no-errata"])
doc = json.loads(buf.getvalue())
# positive control for the instrument: ask the store explicitly, on the same
# lane, after the audit.  The hole exists; the audit never asked.
store = aud.build_store(lane, git(lane, "rev-parse",
                                  "refs/heads/master^{commit}")[1].strip())
missing_set, opaque_set = store.missing()
OUT["C_diagnosis_precondition"] = {
    "in_process_status": status,
    "in_process_summary_status": doc["summary"]["status"],
    "in_process_defects": doc["summary"]["defects"],
    "diagnosis_invocations_during_audit": asked,
    "diagnosis_invoked": bool(asked),
    "positive_control_missing_set_for_lane": sorted(missing_set),
    "positive_control_opaque_set_for_lane": sorted(opaque_set),
    "positive_control_lane_missing_count": len(missing_set),
    "note": "the same lane, asked after the audit, yields the missing set; "
            "the audit did not consult it",
}

# ------------------ D: the PRE-hydration absence assertion (grid harness)
hydrate_calls = []
orig_hydrate = pg.hydrate


def spy_hydrate(clone, src):
    hydrate_calls.append({
        "clone": str(clone),
        "missing_at_hydration_time":
            pg.missing_objects(clone, "refs/heads/master"),
        "objects_before_hydration": len(pg.object_inventory(clone)),
    })
    return orig_hydrate(clone, src)


pg.hydrate = spy_hydrate
root = SCRATCH / "D"
root.mkdir(parents=True, exist_ok=True)


def build_at(sub, **opt):
    tmp = root / sub
    tmp.mkdir(parents=True, exist_ok=True)
    return pg.build(root, tmp, **opt)


# D1: a genuine partial clone that IS hydrated
try:
    genuine = build_at("d1", lane_mark="config", sources=False,
                       blobless_lane=True, hydrate_lane=True)
    d1 = {"raised": None, "premise_lane_missing_after":
          genuine["premise"]["lane_missing"]}
except Exception as exc:                                  # noqa: BLE001
    d1 = {"raised": f"{type(exc).__name__}: {exc}"}
d1["hydrate_calls"] = list(hydrate_calls)
d1["initial_missing_established_before_hydration"] = bool(
    hydrate_calls
    and hydrate_calls[0]["missing_at_hydration_time"])

# D2: a COMPLETE clone that claims to be blobless (negative control)
hydrate_calls.clear()
try:
    build_at("d2", lane_mark="config", sources=False, blobless_lane=True,
             hydrate_lane=True, complete_clone=True)
    d2 = {"raised": None, "violation": "the complete clone was accepted"}
except pg.ContractViolation as exc:
    d2 = {"raised": "ContractViolation", "reason": exc.reason,
          "message": str(exc)}
except Exception as exc:                                  # noqa: BLE001
    d2 = {"raised": f"{type(exc).__name__}: {exc}"}
d2["hydrate_calls"] = list(hydrate_calls)
d2["hydration_never_attempted"] = not hydrate_calls

# D3: the PG28 surface itself: unhydrated partial clone, no hydration
hydrate_calls.clear()
try:
    pg28 = build_at("d3", lane_mark="config", sources=False,
                    blobless_lane=True)
    d3 = {"raised": None,
          "premise_lane_missing": pg28["premise"]["lane_missing"],
          "premise_lane_promisor": pg28["premise"]["lane_promisor"]}
except Exception as exc:                                  # noqa: BLE001
    d3 = {"raised": f"{type(exc).__name__}: {exc}"}
d3["hydrate_calls"] = list(hydrate_calls)
OUT["D_pre_hydration_assertion"] = {"D1_genuine_hydrated": d1,
                                    "D2_complete_clone_control": d2,
                                    "D3_pg28_unhydrated": d3}

# ------------- E: absent citation on the blobless/unhydrated lane surface
# The registered result must survive: an unrelated hole must not turn into a
# refusal, and an absent citation must stay a finding, not a refusal.
hydrate_calls.clear()
try:
    fake_case = build_at("e1", lane_mark="config", sources=False,
                          blobless_lane=True, fake_landed=True)
    e_lane, e_fleet = fake_case["lane"], fake_case["fleet"]
    before = {"lane": pg.object_inventory(e_lane),
              "fleet": pg.object_inventory(e_fleet)}
    code, out, err, timed_out = pg.run_auditor(AUDIT, e_lane, e_fleet,
                                                root / "e1", False)
    after = {"lane": pg.object_inventory(e_lane),
             "fleet": pg.object_inventory(e_fleet)}
    acquired = {k: sorted(after[k] - before[k]) for k in after}
    edoc = json.loads(out) if out.strip() else None
    e1 = {"exit": code, "timed_out": timed_out, "stderr": err[-400:],
          "objects_acquired": acquired,
          "defects": sorted((d["kind"], d["token"])
                            for r in (edoc["results"] if edoc else [])
                            for d in r["defects"]),
          "summary_status": edoc["summary"]["status"] if edoc else None}
except Exception as exc:                                  # noqa: BLE001
    e1 = {"raised": f"{type(exc).__name__}: {exc}"}
OUT["E_absent_citation_on_blobless_surface"] = e1

print(json.dumps(OUT, indent=1, sort_keys=True))
