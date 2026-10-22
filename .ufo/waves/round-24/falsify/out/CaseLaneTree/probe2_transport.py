#!/usr/bin/env python3
"""CaseLaneTree probe 2: is the PG15 refusal really independent of any
transport, and is the missing tree genuinely required?

Stage A (shim): every `git` the auditor spawns is recorded (argv) through a
PATH shim, so the exact command sequence is evidence.
Stage B (live trap): the promisor remote is replaced by a LOCAL bare
repository that actually serves the missing tree, so a lazy fetch would
succeed and would be observable (object acquired in the lane, remote ref
updated).  The auditor must still refuse with exit 2 and acquire nothing.
Stage C (control): without --no-lazy-fetch, the same lane DOES fetch, proving
the trap is live and the refusal in stage B is caused by the isolation, not
by a broken remote.

Local file transport only, no network.  Offline.  Nothing outside the
scratch tree is written.
"""
import importlib.util
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent / "repo"
_spec = importlib.util.spec_from_file_location(
    "promisor_grid", REPO / "tests" / "report-audit" / "promisor-grid.py")
G = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(G)

BASE = Path("/fast/scratch/hyaku/kama-r24/falsify/CaseLaneTree/probe2")
if BASE.exists():
    shutil.rmtree(BASE)
BASE.mkdir(parents=True)
OUT = Path(__file__).resolve().parent / "out"
CURRENT = REPO / G.AUDIT

result = {}

# ---------------------------------------------------------------- stage A
tmp = BASE / "a"
tmp.mkdir()
built = G.BUILDERS["c_missing_lane_tree_promisor"](BASE, tmp)
lane, fleet = built["lane"], built["fleet"]
tip_tree = built["shas"]["tip_tree"]

shim = BASE / "shim"
shim.mkdir()
log = BASE / "git-calls.log"
(shim / "git").write_text(
    "#!/bin/sh\n"
    "printf '%s\\n' \"$*\" >> \"$SHIM_LOG\"\n"
    f"exec {subprocess.run(['which', 'git'], capture_output=True).stdout.decode().strip()} \"$@\"\n"
)
(shim / "git").chmod(0o755)

env = G.env()
env["PATH"] = f"{shim}:{env['PATH']}"
env["SHIM_LOG"] = str(log)
argv = [sys.executable, str(CURRENT), "--lane-repo", str(lane),
        "--fleet-repo", str(fleet), "--rounds", "1", "--json", "--no-errata"]
proc = subprocess.run(argv, capture_output=True, env=env, cwd=str(tmp),
                      timeout=60)
calls = log.read_text().splitlines() if log.exists() else []
result["stage_a"] = {
    "exit": proc.returncode,
    "stderr": proc.stderr.decode(errors="replace").strip(),
    "git_calls": calls,
    "calls_without_no_lazy_fetch": [c for c in calls
                                     if "--no-lazy-fetch" not in c],
    "calls_with_fetch_or_transport": [c for c in calls
                                       if any(w in c for w in
                                              ("fetch", "clone", "upload-pack",
                                               "remote-", "http", "ext::"))],
}

# ---------------------------------------------------------------- stage B/C
tmp2 = BASE / "b"
tmp2.mkdir()
# a complete lane first, to obtain a servable copy of the missing tree
complete = G.build(BASE, tmp2)
comp_lane = complete["lane"]
comp_fleet = complete["fleet"]
tree_oid = complete["shas"]["tip_tree"]

# a local bare "promisor remote" that serves the lane history, so a lazy
# fetch would really hand over the missing tree
remote = BASE / "trap-remote.git"
subprocess.run(["git", "init", "-q", "--bare", str(remote)], check=True,
               env=G.env())
subprocess.run(["git", "-C", str(remote), "config",
                "uploadpack.allowAnySHA1InWant", "true"], check=True,
               env=G.env())
subprocess.run(["git", "-C", str(remote), "config",
                "uploadpack.allowReachableSHA1InWant", "true"], check=True,
               env=G.env())
subprocess.run(["git", "-C", str(comp_lane), "push", "-q", str(remote),
                "master:refs/heads/master"], check=True, env=G.env())

# the PG15 state: same history with the tip root tree removed, promisor
# metadata pointing at the live trap remote
lane2 = BASE / "b" / "lane2"
shutil.copytree(comp_lane, lane2)
obj = (lane2 / ".git" / "objects" / tree_oid[:2] / tree_oid[2:])
obj.unlink()
subprocess.run(["git", "-C", str(lane2), "config", "remote.origin.promisor",
                "true"], check=True, env=G.env())
subprocess.run(["git", "-C", str(lane2), "config", "extensions.partialclone",
                "origin"], check=True, env=G.env())
subprocess.run(["git", "-C", str(lane2), "config", "remote.origin.url",
                str(remote)], check=True, env=G.env())

before_lane = G.object_inventory(lane2)
before_remote = G.object_inventory(remote)
argv2 = [sys.executable, str(CURRENT), "--lane-repo", str(lane2),
         "--fleet-repo", str(comp_fleet), "--rounds", "1", "--json",
         "--no-errata"]
proc2 = subprocess.run(argv2, capture_output=True, env=G.env(), cwd=str(tmp2),
                       timeout=60)
after_lane = G.object_inventory(lane2)
after_remote = G.object_inventory(remote)
result["stage_b"] = {
    "exit": proc2.returncode,
    "stderr": proc2.stderr.decode(errors="replace").strip(),
    "stdout_empty": not proc2.stdout.strip(),
    "objects_acquired_lane": sorted(after_lane - before_lane),
    "objects_acquired_remote": sorted(after_remote - before_remote),
    "tree_still_missing_in_lane": tree_oid not in after_lane,
    "names_tip_tree": tree_oid in proc2.stderr.decode(errors="replace"),
}

# stage C: the same lane, WITHOUT the isolation flag, must fetch: this
# proves the trap is live and stage B's refusal is caused by the isolation.
probe = subprocess.run(["git", "-C", str(lane2), "cat-file", "-e",
                        f"{tree_oid}^{{object}}"], capture_output=True,
                       env=G.env())
after_control = G.object_inventory(lane2)
result["stage_c_control"] = {
    "git_cat_file_rc": probe.returncode,
    "stderr": probe.stderr.decode(errors="replace").strip(),
    "objects_acquired_lane_without_isolation":
        sorted(after_control - before_lane),
    "trap_is_live": tree_oid in after_control,
}

(OUT / "probe2.json").write_text(json.dumps(result, indent=1, sort_keys=True) + "\n")
print(json.dumps(result, indent=1))
