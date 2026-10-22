#!/usr/bin/env python3
"""Two bounded checks for the PG48 report.

1. Lazy-fetch hazard applicability.  A sibling lane found that in a
   file:// blobless clone a probe WITHOUT --no-lazy-fetch can materialise
   a missing blob and turn a correct exit 2 into a false exit 0.  PG48's
   lane is config-marked (remote.origin.url = a path that does not
   exist), not a blobless clone.  Check whether the same hazard can
   exist here: probe the missing subtree with and without isolation and
   observe whether the hole survives.
2. The inherited Git floor (git >= 2.45 for --no-lazy-fetch).
"""
import importlib.util
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

REPO = Path("/fast/scratch/hyaku/kama-r24/falsify/CaseOpaquePositive/repo")
GRID = REPO / "tests/report-audit/promisor-grid.py"
ROOT = Path("/fast/scratch/hyaku/kama-r24/falsify/CaseOpaquePositive/haz-root")

spec = importlib.util.spec_from_file_location("pggrid", GRID)
g = importlib.util.module_from_spec(spec)
spec.loader.exec_module(g)

shutil.rmtree(ROOT, ignore_errors=True)
ROOT.mkdir(parents=True)
tmp = ROOT / "A"
tmp.mkdir()
built = g.BUILDERS["c_opaque_unused_tree_clean"](ROOT, tmp)
lane, shas = built["lane"], built["shas"]
missing = shas["missing_subtree"]

remote = subprocess.run(["git", "-C", str(lane), "config",
                          "--get", "remote.origin.url"], capture_output=True,
                         text=True).stdout.strip()


def present(repo, sha, isolated):
    cmd = ["git"]
    if isolated:
        cmd += ["--no-lazy-fetch", "--no-replace-objects"]
    cmd += ["-C", str(repo), "cat-file", "-e", sha + "^{object}"]
    p = subprocess.run(cmd, capture_output=True)
    return p.returncode == 0


before = present(lane, missing, False)
# a stray, UNISOLATED probe (the hazard shape)
p = subprocess.run(["git", "-C", str(lane), "cat-file", "-e",
                    missing + "^{object}"], capture_output=True)
unisolated_rc = p.returncode
unisolated_err = p.stderr.decode(errors="replace").strip()[:200]
after_unisolated = present(lane, missing, True)
after_isolated = present(lane, missing, True)

gv = subprocess.run(["git", "--version"], capture_output=True,
                    text=True).stdout.strip()
floor = subprocess.run(["git", "-C", str(lane), "--no-lazy-fetch",
                        "rev-parse", "HEAD"], capture_output=True,
                       text=True)
floor_ok = floor.returncode == 0

print(json.dumps({
    "remote_origin_url": remote,
    "remote_origin_url_exists": Path(remote).exists(),
    "missing_subtree": missing,
    "present_before_unisolated_probe": before,
    "unisolated_probe_rc": unisolated_rc,
    "unisolated_probe_stderr": unisolated_err,
    "present_after_unisolated_probe": after_unisolated,
    "present_after_isolated_probe": after_isolated,
    "hole_survives_unisolated_probe": not after_unisolated,
    "git_version": gv,
    "no_lazy_fetch_supported": floor_ok,
    "git_floor_2_45_satisfied": int(gv.split()[2].split(".")[0]) > 2
    or (int(gv.split()[2].split(".")[0]) == 2
        and int(gv.split()[2].split(".")[1]) >= 45),
}, indent=1))
