#!/usr/bin/env python3
"""FinalCase15: attribute the `remote.origin.partialclonefilter` config write.

Three fixtures are built with the pinned grid's own builder:
  A: pristine, only audited (pinned auditor, --no-lazy-fetch via the auditor)
  B: pristine, only `git status` (my own diagnostic, no --no-lazy-fetch)
  C: pristine, the restore control (tip tree object written back) -> verdict
Every fixture keeps the promisor config; the config text is compared before
and after each action.
"""
import hashlib
import importlib.util
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

CLONE = Path(sys.argv[1]).resolve()
OUT = Path(sys.argv[2]).resolve()
WORK = Path(sys.argv[3]).resolve()
GRID = CLONE / "tests/report-audit/promisor-grid.py"
AUDIT = CLONE / "tools/report-landing-audit.py"

spec = importlib.util.spec_from_file_location("pg", GRID)
pg = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pg)

WORK.mkdir(parents=True, exist_ok=True)
OUT.mkdir(parents=True, exist_ok=True)
report = {"auditor_sha256": hashlib.sha256(AUDIT.read_bytes()).hexdigest(),
          "grid_sha256": hashlib.sha256(GRID.read_bytes()).hexdigest(),
          "builder": "c_missing_lane_tree_promisor"}


def build(name):
    root = WORK / name
    root.mkdir(parents=True, exist_ok=True)
    tmp = root / "case"
    tmp.mkdir(parents=True, exist_ok=True)
    built = pg.BUILDERS["c_missing_lane_tree_promisor"](root, tmp)
    return root, tmp, built


def cfg(repo):
    return (repo / ".git" / "config").read_text(encoding="utf-8")


def inventory(repo):
    p = subprocess.run(["git", "--no-lazy-fetch", "--no-replace-objects",
                        "-C", str(repo), "cat-file", "--batch-all-objects",
                        "--batch-check=%(objectname)"],
                       capture_output=True, env=pg.env())
    return sorted(set(p.stdout.decode().split()))


def env():
    return pg.env()


def run_auditor(built, tmp):
    lane, fleet = built["lane"], built["fleet"]
    argv = [sys.executable, str(AUDIT), "--lane-repo", str(lane),
            "--fleet-repo", str(fleet), "--rounds", "1", "--json",
            "--no-errata"]
    p = subprocess.run(argv, capture_output=True, env=env(), cwd=str(tmp))
    return {"argv": argv, "exit": p.returncode,
            "stdout": p.stdout.decode(errors="replace"),
            "stderr": p.stderr.decode(errors="replace")}


def diff_cfg(before, after):
    b = set(before.splitlines())
    a = set(after.splitlines())
    return {"added": sorted(a - b), "removed": sorted(b - a)}


# ---- A: audited only ---------------------------------------------------
rootA, tmpA, builtA = build("A")
before = cfg(builtA["lane"])
inv_before = inventory(builtA["lane"])
runA = run_auditor(builtA, tmpA)
after = cfg(builtA["lane"])
report["A_audited_only"] = {
    "config_diff": diff_cfg(before, after),
    "config_after": after,
    "exit": runA["exit"],
    "stdout_bytes": len(runA["stdout"]),
    "stderr": runA["stderr"],
    "objects_acquired": sorted(set(inventory(builtA["lane"])) - set(inv_before)),
}

# ---- B: git status only (my own diagnostic) ----------------------------
rootB, tmpB, builtB = build("B")
before = cfg(builtB["lane"])
p = subprocess.run(["git", "-C", str(builtB["lane"]), "status", "--porcelain"],
                   capture_output=True, env=env())
after = cfg(builtB["lane"])
report["B_git_status_only"] = {
    "config_diff": diff_cfg(before, after),
    "git_status_exit": p.returncode,
    "git_status_stderr": p.stderr.decode(errors="replace"),
    "objects_acquired": sorted(set(inventory(builtB["lane"]))
                               - set(inventory(builtB["lane"]))),
}

# ---- C: restore control: put the tip tree back, keep promisor config ---
rootC, tmpC, builtC = build("C")
lane = builtC["lane"]
tip = builtC["shas"]["tip_tree"]
work = subprocess.run(["git", "-C", str(lane), "ls-files", "-s"],
                      capture_output=True, env=env()).stdout.decode()
subprocess.run(["git", "-C", str(lane), "add", "-A"], capture_output=True,
               env=env())
tree = subprocess.run(["git", "-C", str(lane), "write-tree"],
                      capture_output=True, env=env()).stdout.decode().strip()
restored = tree == tip
runC = run_auditor(builtC, tmpC)
report["C_restore_control"] = {
    "expected_tip_tree": tip,
    "written_tree": tree,
    "tree_restored_exactly": restored,
    "exit": runC["exit"],
    "stdout_bytes": len(runC["stdout"]),
    "stdout": runC["stdout"],
    "stderr": runC["stderr"],
    "config_has_partialclonefilter_before": "partialclonefilter"
                                            in cfg(lane),
}
(OUT / "attribution.json").write_text(json.dumps(report, indent=1) + "\n",
                                       encoding="utf-8")
print(json.dumps(report, indent=1)[:6000])
