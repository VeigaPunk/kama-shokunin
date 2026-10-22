#!/usr/bin/env python3
"""FinalCase11 independent re-derivation of PG11-omission-fleet-promisor.

Uses the PINNED grid module (byte-pinned by sha256) to build the same fixture
the grid built, then records the premise facts and runs the PINNED auditor
directly with the argv the grid uses.  No cell of the grid is re-run; this is
inspection of the fixture premise plus one direct auditor invocation.
"""
import hashlib
import re
import json
import os
import subprocess
import sys
from pathlib import Path

CLONE = Path("/fast/scratch/hyaku/kama-r24/postfix/FinalCase11/clone")
import importlib.util  # noqa: E402

_spec = importlib.util.spec_from_file_location(
    "promisor_grid", CLONE / "tests" / "report-audit" / "promisor-grid.py")
G = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(G)

OUT = Path("/fast/scratch/hyaku/kama-r24/postfix/FinalCase11/out")
ROOT = Path("/fast/scratch/hyaku/kama-r24/postfix/FinalCase11/tmp/rederive")
AUDIT = CLONE / "tools" / "report-landing-audit.py"

grid_sha = hashlib.sha256((CLONE / "tests/report-audit/promisor-grid.py")
                          .read_bytes()).hexdigest()
aud_sha = hashlib.sha256(AUDIT.read_bytes()).hexdigest()
assert grid_sha == "30483830e0461898bd9b710603e755b08cf58e2a2a215a747098ebbe0383f270", grid_sha
assert aud_sha == "b9be4f428cd70842320c698794faffaa95571a60fc530df6a84d7d8cade3b26f", aud_sha

ROOT.mkdir(parents=True, exist_ok=True)
import shutil  # noqa: E402
shutil.rmtree(ROOT / "current", ignore_errors=True)
tmp = ROOT / "current" / "000"
tmp.mkdir(parents=True, exist_ok=True)

built = G.BUILDERS["c_omission_fleet_promisor"](ROOT, tmp)
lane, fleet, shas = built["lane"], built["fleet"], built["shas"]

premise = {
    "grid_sha256": grid_sha,
    "auditor_sha256": aud_sha,
    "builder": "c_omission_fleet_promisor",
    "lane": str(lane),
    "fleet": str(fleet),
    "premise": built["premise"],
    "shas": shas,
    "lane_log": G.git(lane, "log", "--format=%H %an %at %s", "master").split("\n"),
    "report_text": G.git(fleet, "show", f"HEAD:{G.REL}"),
    "report_first_add_at": G.git(fleet, "log", "--diff-filter=A", "--format=%at",
                                 "--", G.REL).split(),
    "lane_promisor_facts": G.promisor_facts(lane),
    "fleet_promisor_facts": G.promisor_facts(fleet),
    "lane_missing": G.missing_objects(lane, "refs/heads/master"),
    "fleet_missing": G.missing_objects(fleet, "HEAD"),
    "fleet_remote_url": G.git(fleet, "config", "--get", "remote.origin.url",
                              check=False).strip(),
    "fleet_remote_exists": Path(G.git(fleet, "config", "--get",
                                      "remote.origin.url",
                                      check=False).strip() or "/nonexistent").exists(),
    "lane_remote_url": G.git(lane, "config", "--get", "remote.origin.url",
                             check=False).strip(),
    "cited_hashes_in_report": re.findall(
        r"\b[0-9a-f]{7,40}\b", G.git(fleet, "show", f"HEAD:{G.REL}")),
    "omitted_present_in_lane": G.object_exists(lane, shas["omitted"]),
    "omitted_present_in_fleet": G.object_exists(fleet, shas["omitted"]),
    "lane_commit_present_in_fleet": G.object_exists(fleet, shas["lane_commit"]),
}

before = {"lane": G.object_inventory(lane), "fleet": G.object_inventory(fleet)}
argv = [sys.executable, str(AUDIT), "--lane-repo", str(lane),
        "--fleet-repo", str(fleet), "--rounds", "1", "--json", "--no-errata"]
proc = subprocess.run(argv, capture_output=True, env=G.env(), cwd=str(tmp))
after = {"lane": G.object_inventory(lane), "fleet": G.object_inventory(fleet)}
premise["auditor_argv"] = argv
premise["auditor_exit"] = proc.returncode
premise["auditor_stdout_bytes"] = len(proc.stdout)
premise["auditor_stderr"] = proc.stderr.decode(errors="replace")
premise["objects_acquired"] = {k: sorted(after[k] - before[k]) for k in after}
try:
    doc = json.loads(proc.stdout)
except ValueError:
    doc = None
premise["document"] = doc
if doc:
    premise["defects"] = [[d.get("kind"), d.get("token")]
                          for r in doc.get("results", [])
                          for d in r.get("defects", [])]
    premise["summary"] = doc.get("summary")
premise["cutoff_and_omitted_match"] = bool(
    doc and any(d.get("kind") == "landed-omitted"
                and d.get("token") == shas["omitted"]
                for r in doc["results"] for d in r.get("defects", [])))
premise["cited_is_lane_commit"] = shas["lane_commit"] in premise["cited_hashes_in_report"]
premise["omitted_pre_cutoff"] = True

(OUT / "rederive_pg11.json").write_text(
    json.dumps(premise, indent=1, sort_keys=True) + "\n", encoding="utf-8")
print(json.dumps({k: v for k, v in premise.items()
                  if k not in ("document", "shas")}, indent=1, sort_keys=True))
