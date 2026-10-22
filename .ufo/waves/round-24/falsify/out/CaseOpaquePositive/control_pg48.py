#!/usr/bin/env python3
"""PG48 controls: (1) git-command trace via a logging PATH shim,
(2) negative control: same fixture + one unresolved fabricated token in the
fleet report -> the auditor must refuse with a content-derived reason
naming the missing tree, proving PG48's exit 0 is not "the auditor ignores
holes".  Offline, benign, local fixtures only.
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
AUDIT = REPO / "tools/report-landing-audit.py"
ROOT = Path("/fast/scratch/hyaku/kama-r24/falsify/CaseOpaquePositive/ctrl-root")
SHIM = ROOT / "shim"

spec = importlib.util.spec_from_file_location("pggrid", GRID)
g = importlib.util.module_from_spec(spec)
spec.loader.exec_module(g)


def make_shim():
    SHIM.mkdir(parents=True, exist_ok=True)
    log = SHIM / "git-calls.log"
    real = shutil.which("git")
    sh = SHIM / "git"
    sh.write_text(
        "#!/bin/sh\n"
        f'printf "%s\\n" "$*" >> {log}\n'
        f'exec {real} "$@"\n')
    sh.chmod(0o755)
    return log


def run(lane, fleet, tmp, use_shim=False, trace_log=None):
    env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    env.update(GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_NOSYSTEM="1",
               GIT_AUTHOR_NAME="fixture", GIT_COMMITTER_NAME="fixture",
               GIT_AUTHOR_EMAIL="a@x", GIT_COMMITTER_EMAIL="a@x")
    if use_shim:
        env["PATH"] = str(SHIM) + ":" + env.get("PATH", "")
    argv = [sys.executable, str(AUDIT), "--lane-repo", str(lane),
            "--fleet-repo", str(fleet), "--rounds", "1", "--json",
            "--no-errata"]
    p = subprocess.run(argv, capture_output=True, env=env, cwd=str(tmp),
                       timeout=60)
    return p.returncode, p.stdout.decode(errors="replace"), \
        p.stderr.decode(errors="replace")


def inventory(repo):
    out = subprocess.run(["git", "--no-lazy-fetch", "-C", str(repo),
                          "cat-file", "--batch-all-objects",
                          "--batch-check=%(objectname)"], capture_output=True)
    return set(out.stdout.decode().split())


shutil.rmtree(ROOT, ignore_errors=True)
ROOT.mkdir(parents=True)
log = make_shim()

# ---------- control 1: trace of the graded PG48 fixture
tmp1 = ROOT / "t1"
tmp1.mkdir()
b1 = g.BUILDERS["c_opaque_unused_tree_clean"](ROOT, tmp1)
before = {"lane": inventory(b1["lane"]), "fleet": inventory(b1["fleet"])}
code1, out1, err1 = run(b1["lane"], b1["fleet"], tmp1, use_shim=True)
after = {"lane": inventory(b1["lane"]), "fleet": inventory(b1["fleet"])}
calls = log.read_text(errors="replace").split("\n") if log.exists() else []
missing_oid = b1["shas"]["missing_subtree"]

# ---------- control 2: negative control on the SAME fixture shape
tmp2 = ROOT / "t2"
tmp2.mkdir()
b2 = g.build(ROOT, tmp2, lane_mark="config", opaque_tree=True,
             fake_notes=True, drop=("opaque_tree",))
before2 = {"lane": inventory(b2["lane"]), "fleet": inventory(b2["fleet"])}
code2, out2, err2 = run(b2["lane"], b2["fleet"], tmp2)
after2 = {"lane": inventory(b2["lane"]), "fleet": inventory(b2["fleet"])}

print(json.dumps({
    "trace_fixture": {
        "exit": code1,
        "stdout_is_json": out1.strip().startswith("{"),
        "stderr": err1.strip()[:300],
        "missing_tree_oid": missing_oid,
        "git_calls": [c for c in calls if c],
        "calls_naming_missing_oid": [c for c in calls if missing_oid in c],
        "calls_with_transport": [c for c in calls
                                 if "fetch" in c or "pull" in c
                                 or "clone" in c or "remote" in c],
        "lane_objects_acquired": sorted(after["lane"] - before["lane"]),
        "fleet_objects_acquired": sorted(after["fleet"] - before["fleet"]),
    },
    "negative_control": {
        "exit": code2,
        "stderr": err2.strip()[:600],
        "stdout_is_json": out2.strip().startswith("{"),
        "stdout": out2.strip()[:200],
        "missing_tree_oid": b2["shas"]["missing_subtree"],
        "fake_token": b2["shas"]["fake"],
        "reason_names_missing_tree": b2["shas"]["missing_subtree"] in err2,
        "reason_names_fake_token": b2["shas"]["fake"] in err2,
        "reason_is_metadata_refusal": ("partial clone (" in err2
                                       or "promisor pack" in err2),
        "lane_objects_acquired": sorted(after2["lane"] - before2["lane"]),
        "fleet_objects_acquired": sorted(after2["fleet"] - before2["fleet"]),
    },
}, indent=1))
