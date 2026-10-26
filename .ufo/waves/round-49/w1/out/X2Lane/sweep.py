#!/usr/bin/env python3
"""sweep.py - X2Lane (round 49) driver: v3 vs v4 append-only-audit over 8 lane tips.

Read-only on the lane clone. Writes one JSON record per run to runs/<label>.json:
{tool, tip, contract, threshold, exit, stderr, raw, json} so summarize.py can rebuild
matrix.tsv and events.tsv without re-running the tools.

  sweep.py <lane-clone> <v3-tool.py> <v4-tool.py> <out-dir>

Tips: idx = i*(N-1)//7 for i in 0..7 over
  git rev-list --reverse 438127bc01ff3b99f98468549d58046f932490ef~40..74558c71...
so the first and last are the round-44 freeze base and the round-49 build tip.
Contract modes: "tip" = registry/append-only-contract.tsv at that tip (default lookup),
"pinned" = the 5-column contract at the build tip, held constant so pre-contract tips are
still evaluable. Thresholds: 20 (tool default) everywhere; 1,2,5,10 at the build tip.
"""
import json
import os
import subprocess
import sys

BASE = "438127bc01ff3b99f98468549d58046f932490ef"
TIP = "74558c71c38ceaeace15fd4cf8aa9d84977584b1"
CONTRACT = "registry/append-only-contract.tsv"


def git(lane, *a):
    return subprocess.run(["git", "-C", lane, *a], capture_output=True, text=True)


def main():
    lane, v3, v4, out = sys.argv[1:5]
    runs = os.path.join(out, "runs")
    os.makedirs(os.path.join(out, "contracts"), exist_ok=True)
    os.makedirs(runs, exist_ok=True)
    rng = git(lane, "rev-list", "--reverse", f"{BASE}~40..{TIP}").stdout.split()
    tips = [rng[i * (len(rng) - 1) // 7] for i in range(8)]
    for t in tips:
        p = git(lane, "show", f"{t}:{CONTRACT}")
        open(os.path.join(out, "contracts", f"{t}.tsv"), "w").write(p.stdout if p.returncode == 0 else "")
    pinned = os.path.join(out, "contracts", f"{TIP}.tsv")

    def run(tool, tip, contract, thr, label):
        cmd = [sys.executable, tool, "--repo", lane, "--to", tip, "--threshold", str(thr), "--json"]
        if contract:
            cmd += ["--contract", contract]
        p = subprocess.run(cmd, capture_output=True, text=True)
        try:
            j = json.loads(p.stdout)
        except ValueError:
            j = None
        rec = {"tool": os.path.basename(tool), "tip": tip, "contract": contract, "threshold": thr,
               "exit": p.returncode, "stderr": p.stderr[-400:], "raw": p.stdout, "json": j}
        json.dump(rec, open(os.path.join(runs, label + ".json"), "w"), indent=1)

    for i, t in enumerate(tips):
        c = os.path.join(out, "contracts", f"{t}.tsv")
        tipc = c if os.path.getsize(c) else None
        for tool, name in ((v3, "v3.py"), (v4, "v4.py")):
            run(tool, t, tipc, 20, f"{i:02d}_{t[:8]}_{name[:-3]}_tipcontract")
            run(tool, t, pinned, 20, f"{i:02d}_{t[:8]}_{name[:-3]}_pinned")
    for thr in (1, 2, 5, 10):
        for tool, name in ((v3, "v3.py"), (v4, "v4.py")):
            run(tool, TIP, pinned, thr,
                f"{'99' if thr == 1 else '98'}_thr{thr}_{name}" + ("_pinned" if thr == 1 else ""))
    json.dump({"tips": tips}, open(os.path.join(out, "tips.json"), "w"), indent=1)
    print(f"tips {len(tips)} runs {len(os.listdir(runs))}")


if __name__ == "__main__":
    main()
