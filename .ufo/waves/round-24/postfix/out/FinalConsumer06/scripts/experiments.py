#!/usr/bin/env python3
"""FinalConsumer06 E1/E2: connect the selected-round invariant to BOTH
sides of the ledger accounting.

E1  the SAME invalid row moved to the SELECTED round 1: the selected-row
    validity check must still fire (no weakening).
E2  an UNSELECTED row whose correction is an object whose content cannot
    be served (a tag whose target commit was removed): the unselected row
    must not cause a REQUIRED READ (before: refuses the whole audit).

Writes raw JSON under out/FinalConsumer06/.
"""
import importlib.util
import json
import os
import subprocess
import sys
from pathlib import Path

BASE = Path("/fast/scratch/hyaku/kama-r24/postfix/FinalConsumer06")
CLONE = BASE / "clone"
DRIVER = CLONE / ".ufo/waves/round-24/fixes/StoreLocalPresence/proof-driver-replay-v3.py"
AFTER = CLONE / "tools/report-landing-audit.py"
BEFORE = BASE / "insp/before-report-landing-audit.py"
OUT = Path("/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-24/postfix/out/FinalConsumer06")
OUT.mkdir(parents=True, exist_ok=True)
os.environ["TMPDIR"] = str(BASE / "tmp")

spec = importlib.util.spec_from_file_location("replay3", DRIVER)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
ENV = {"GIT_CONFIG_GLOBAL": "/dev/null", "GIT_CONFIG_NOSYSTEM": "1",
       "PATH": "/usr/bin:/bin",
       "GIT_AUTHOR_NAME": "kama-shokunin", "GIT_COMMITTER_NAME": "kama-shokunin",
       "GIT_AUTHOR_EMAIL": "a@x", "GIT_COMMITTER_EMAIL": "a@x"}


def g(repo, *args):
    p = subprocess.run(["git", "--no-replace-objects", "--no-lazy-fetch",
                        "-C", str(repo), *args],
                       capture_output=True, env=ENV)
    return {"rc": p.returncode,
            "out": p.stdout.decode("utf-8", "replace").strip(),
            "err": p.stderr.decode("utf-8", "replace").strip()}


def run_tool(tool, lane, fleet, draft, errata):
    cmd = [sys.executable, str(tool), "--lane-repo", str(lane),
           "--fleet-repo", str(fleet), "--branch", "master", "--rounds", "1",
           "--report", f"1={draft}", "--json"]
    cmd += ["--errata", str(errata)] if errata else ["--no-errata"]
    p = subprocess.run(cmd, capture_output=True, timeout=60)
    rec = {"argv": cmd, "exit": p.returncode,
           "stderr": p.stderr.decode("utf-8", "replace").strip()[:600]}
    try:
        rec["doc"] = json.loads(p.stdout.decode("utf-8", "replace"))
    except Exception:
        rec["stdout"] = p.stdout.decode("utf-8", "replace")[:2000]
    return rec


def summarise(rec):
    doc = rec.get("doc", {})
    return {"exit": rec["exit"], "stderr": rec["stderr"],
            "summary": doc.get("summary"),
            "kinds": sorted({d["kind"] for res in doc.get("results", [])
                             for d in res["defects"]}),
            "errata_invalid": doc.get("errata_invalid"),
            "errata_unmatched": doc.get("errata_unmatched")}


def fresh(name):
    d = BASE / ("fx-" + name)
    subprocess.run(["rm", "-rf", str(d)], check=True)
    d.mkdir(parents=True)
    return mod.scenario(d, "unselected-invalid-correction") + (d,)


results = {}

# ---- E1: the same invalid row, but in the SELECTED round -------------------
lane, fleet, draft, errata, d = fresh("e1")
zero = "0" * 40
errata.write_text(f"1\tunresolved-full-hash\t{zero}\t{zero}\tev\n",
                  encoding="utf-8")
e1 = {"errata_text": errata.read_text(encoding="utf-8"),
      "draft_text": draft.read_text(encoding="utf-8"),
      "before": summarise(run_tool(BEFORE, lane, fleet, draft, errata)),
      "after": summarise(run_tool(AFTER, lane, fleet, draft, errata)),
      "after_no_ledger": summarise(run_tool(AFTER, lane, fleet, draft, None)),
      "before_no_ledger": summarise(run_tool(BEFORE, lane, fleet, draft, None))}
results["E1_selected_round_invalid_row"] = e1

# ---- E2: UNSELECTED row whose correction cannot be served ------------------
lane, fleet, draft, errata, d = fresh("e2")
tree = g(lane, "rev-parse", "HEAD^{tree}")["out"]
target = g(lane, "commit-tree", tree, "-m", "tag target")["out"]
g(lane, "tag", "-a", "-m", "hole", "v-hole", target)
tag_oid = g(lane, "rev-parse", "v-hole")["out"]
objpath = Path(lane, g(lane, "rev-parse", "--git-path", "objects")["out"],
               target[:2], target[2:])
removed = objpath.exists()
if removed:
    objpath.unlink()
errata.write_text(f"2\tunresolved-full-hash\t{zero}\t{tag_oid}\tev\n",
                  encoding="utf-8")
e2 = {"errata_text": errata.read_text(encoding="utf-8"),
      "draft_text": draft.read_text(encoding="utf-8"),
      "tag_oid": tag_oid, "target_oid": target,
      "target_loose_object_removed": removed,
      "tag_type_lane": g(lane, "cat-file", "-t", tag_oid),
      "tag_peel_lane": g(lane, "cat-file", "-t", tag_oid + "^{}"),
      "target_type_lane": g(lane, "cat-file", "-t", target),
      "before": summarise(run_tool(BEFORE, lane, fleet, draft, errata)),
      "after": summarise(run_tool(AFTER, lane, fleet, draft, errata)),
      "after_no_ledger": summarise(run_tool(AFTER, lane, fleet, draft, None)),
      "before_no_ledger": summarise(run_tool(BEFORE, lane, fleet, draft, None))}
results["E2_unselected_row_unservable_correction"] = e2

(OUT / "experiments-E1-E2.json").write_text(
    json.dumps(results, indent=1, sort_keys=True), encoding="utf-8")
print(json.dumps(results, indent=1, sort_keys=True))
