#!/usr/bin/env python3
"""CaseLaneTree probe 3: is the PG15 PREMISE robust when the promisor origin
is live?

`CaseFleetBlobless` reported that the harness helper `promisor-grid.py`
git() (lines ~99-104) is fetch-capable (no --no-lazy-fetch, no timeout), so a
probe or build step that reads a missing object in a promisor-marked clone can
materialise it and void the premise.  PG15's shipped origin path is
nonexistent, so the shipped fixture cannot show this either way.

Here the origin is replaced by a LOCAL bare repository that really serves the
lane history, and the grid's OWN builder is then run.  Question: does the
grid's own build/premise machinery materialise the missing tip tree, and does
the PG15 premise (missing tree present) survive?

Local file transport only.  Offline.  Nothing outside the scratch tree is
written; no production file is edited (the harness is used through a
monkey-patch in this probe process only).
"""
import importlib.util
import json
import shutil
import subprocess
from pathlib import Path

REPO = Path(__file__).resolve().parent / "repo"
_spec = importlib.util.spec_from_file_location(
    "promisor_grid", REPO / "tests" / "report-audit" / "promisor-grid.py")
G = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(G)

BASE = Path("/fast/scratch/hyaku/kama-r24/falsify/CaseLaneTree/probe3")
if BASE.exists():
    shutil.rmtree(BASE)
BASE.mkdir(parents=True)
OUT = Path(__file__).resolve().parent / "out"
CURRENT = REPO / G.AUDIT
res = {}

# ---- a servable origin built from the deterministic fixture history
tmp0 = BASE / "origin-src"
tmp0.mkdir()
complete = G.build(BASE, tmp0)
tree_oid = complete["shas"]["tip_tree"]
remote = BASE / "trap-remote.git"
subprocess.run(["git", "init", "-q", "--bare", str(remote)], check=True,
               env=G.env())
for key in ("uploadpack.allowAnySHA1InWant", "uploadpack.allowReachableSHA1InWant"):
    subprocess.run(["git", "-C", str(remote), "config", key, "true"],
                   check=True, env=G.env())
subprocess.run(["git", "-C", str(complete["lane"]), "push", "-q", str(remote),
                "master:refs/heads/master"], check=True, env=G.env())
res["origin_serves_the_missing_tree"] = tree_oid in G.object_inventory(remote)

# ---- monkey-patch the marking helper so the shipped builder points its
# promisor remote at the live origin instead of a nonexistent path
orig_mark = G.mark_config


def patched_mark(repo, tmp):
    orig_mark(repo, tmp)
    subprocess.run(["git", "-C", str(repo), "config", "remote.origin.url",
                    str(remote)], check=True, env=G.env())


G.mark_config = patched_mark

# ---- run the grid's own PG15 builder
tmp = BASE / "pg15-live"
tmp.mkdir()
built = G.BUILDERS["c_missing_lane_tree_promisor"](BASE, tmp)
lane, fleet = built["lane"], built["fleet"]
lane_inv = G.object_inventory(lane)
remote_inv = G.object_inventory(remote)

res["build"] = {
    "premise_lane_missing": built["premise"]["lane_missing"],
    "premise_lane_promisor": built["premise"]["lane_promisor"],
    "tip_tree_present_in_lane_after_build": tree_oid in lane_inv,
    "tip_tree_present_in_origin": tree_oid in remote_inv,
    "objects_in_lane": len(lane_inv),
    "origin_url": subprocess.run(
        ["git", "-C", str(lane), "config", "remote.origin.url"],
        capture_output=True, env=G.env()).stdout.decode().strip(),
}

# ---- and the auditor on that (live-origin) fixture
proc = subprocess.run(
    [__import__("sys").executable, str(CURRENT), "--lane-repo", str(lane),
     "--fleet-repo", str(fleet), "--rounds", "1", "--json", "--no-errata"],
    capture_output=True, env=G.env(), cwd=str(tmp), timeout=60)
res["audit_on_live_origin_fixture"] = {
    "exit": proc.returncode,
    "stderr": proc.stderr.decode(errors="replace").strip(),
    "stdout_empty": not proc.stdout.strip(),
    "objects_acquired_lane": sorted(G.object_inventory(lane) - lane_inv),
    "objects_acquired_origin": sorted(G.object_inventory(remote) - remote_inv),
    "tree_still_missing_in_lane": tree_oid not in G.object_inventory(lane),
}

(OUT / "probe3.json").write_text(json.dumps(res, indent=1, sort_keys=True) + "\n")
print(json.dumps(res, indent=1))
