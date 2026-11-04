#!/usr/bin/env python3
"""Run every C1 attack fixture against the landed round-scope tool (and, for
comparison, the base gate arm command). Captures receipts under $S/receipts/.

Usage: python3 run_attacks.py /path/to/round72-round-scope.py
"""
import json, os, subprocess, sys

S = "/fast/scratch/hyaku/kama-r72/RVW01RoundScopeAttack"
FIX = f"{S}/fixtures"
REC = f"{S}/receipts"
TOOL = sys.argv[1]
WAVE = ".ufo/waves/round-72"

def run_tool(name, args, cwd):
    os.makedirs(REC, exist_ok=True)
    r = subprocess.run(args, cwd=cwd, capture_output=True, text=True)
    out = [f"# cmd: {' '.join(args)}", f"# cwd: {cwd}",
           f"# exit: {r.returncode}", "--- stdout ---", r.stdout.rstrip("\n")]
    if r.stderr:
        out += ["--- stderr ---", r.stderr.rstrip("\n")]
    with open(f"{REC}/{name}.out", "w") as f:
        f.write("\n".join(out) + "\n")
    line = next((ln for ln in r.stdout.splitlines() if "ROUND_SCOPE " in ln), "")
    print(f"{name}: exit={r.returncode} line={line!r}")
    return {"name": name, "exit": r.returncode, "line": line,
            "stdout": r.stdout, "stderr": r.stderr}

results = []

def scope(name, repo, extra=(), rnd="72", lane_args=()):
    args = ["python3", TOOL, "--repo", repo, "--round", rnd, "--tip", "master", *lane_args, *extra]
    results.append(run_tool(name, args, cwd=repo))

def base_arm(name, repo, rnd="72"):
    """The round-71 fifth-arm command (what the base gate graded)."""
    args = ["git", "-C", repo, "status", "--porcelain", "-uall", "--", f".ufo/waves/round-{rnd}"]
    results.append(run_tool(name, args, cwd=repo))

# clean baselines
scope("b0-seed-clean", f"{S}/seed", lane_args=("--lane", "kama"))
base_arm("b0-seed-basearm", f"{S}/seed")
scope("b0-round99-wronglabel", f"{S}/seed", rnd="99", lane_args=("--lane", "kama"))

# A1 staged-only records
scope("a1-staged-new", f"{FIX}/a1", lane_args=("--lane", "kama"))
base_arm("a1-staged-new-basearm", f"{FIX}/a1")
# A2 staged deletion
scope("a2-staged-delete", f"{FIX}/a2", lane_args=("--lane", "kama"))
base_arm("a2-staged-delete-basearm", f"{FIX}/a2")
# A3 space+newline names
scope("a3-space-newline-stray", f"{FIX}/a3", lane_args=("--lane", "kama"))
scope("a3i-space-newline-ignored", f"{FIX}/a3i", lane_args=("--lane", "kama"))
# A4 tracked-but-ignored under wave dir
scope("a4-tracked-ignored", f"{FIX}/a4", lane_args=("--lane", "kama"))
scope("a4b-tracked+untracked-ignored", f"{FIX}/a4b", lane_args=("--lane", "kama"))
base_arm("a4-tracked-ignored-basearm", f"{FIX}/a4")
# A5 second-worktree dirt
scope("a5-worktree-primary", f"{FIX}/a5", lane_args=("--lane", "kama"))
scope("a5-worktree-linked", f"{FIX}/a5-wt", lane_args=("--lane", "kama"))
base_arm("a5-worktree-primary-basearm", f"{FIX}/a5")
# A6 label/prompt/wave-dir mismatches
scope("a6-prompt+plan-clean", f"{FIX}/a6", lane_args=("--lane", "kama"))
scope("a6b-prompt-yes-plan-gone", f"{FIX}/a6b", lane_args=("--lane", "kama"))
scope("a6c-plan-no-prompt", f"{FIX}/a6c", lane_args=("--lane", "kama"))
scope("a6d-plan-mislabelled-heading", f"{FIX}/a6d", lane_args=("--lane", "kama"))
scope("a6e-round71-wronglabel", f"{FIX}/a6e", rnd="71", lane_args=("--lane", "kama"))
# A7 submodule + broad allow-list
scope("a7sub-submodule-default", f"{FIX}/a7sub", lane_args=("--lane", "kama"))
scope("a7sub2-submodule-ignore-all", f"{FIX}/a7sub2", lane_args=("--lane", "kama"))
scope("a7allow-prefix-dir", f"{FIX}/a7allow", extra=("--allow", "corpus/lessons"), lane_args=("--lane", "kama"))
scope("a7allow-prefix-dir-slash", f"{FIX}/a7allow", extra=("--allow", "corpus/lessons/"), lane_args=("--lane", "kama"))
scope("a7allow-glob-star", f"{FIX}/a7allow", extra=("--allow", "corpus/lessons/*"), lane_args=("--lane", "kama"))
scope("a7allow-glob-starstar", f"{FIX}/a7allow", extra=("--allow", "corpus/lessons/**"), lane_args=("--lane", "kama"))
base_arm("a7sub2-submodule-ignore-all-basearm", f"{FIX}/a7sub2")

with open(f"{REC}/summary.json", "w") as f:
    json.dump(results, f, indent=1)
print("RUN_COMPLETE", len(results))
