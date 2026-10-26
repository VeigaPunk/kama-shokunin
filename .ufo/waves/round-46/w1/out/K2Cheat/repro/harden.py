#!/usr/bin/env python3
"""Score every candidate with the proposed hardened counter."""
import json
import os
import re
import shutil
import subprocess
import sys

S = "/fast/scratch/hyaku/kama-r46/K2Cheat"
O = "/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-46/w1/out/K2Cheat"
H = os.path.join(O, "proposed/round46-append-audit-check.py")
D = os.path.join(S, "fxclone")
names = ["t1-repo-import", "t2-fixedpath-import", "t3-fixture-shape", "t4-selftest-only",
         "t5-fixedpath-real-tool", "baseline-real-plus-table"]
res = {}
for name in names:
    txt = open(os.path.join(O, "receipts", name + ".c2.out")).read()
    sha = re.search(r"^tip=(\S+)$", txt, re.M).group(1)
    for run in range(3 if name.startswith("baseline") else 1):
        scratch = os.path.join(S, f"hard-{name}-{run}")
        shutil.rmtree(scratch, ignore_errors=True)
        os.makedirs(scratch, exist_ok=True)
        out = os.path.join(O, "receipts", f"hardened.{name}{'' if run == 0 else f'.r{run}'}.out")
        p = subprocess.run([sys.executable, H, "--repo", D, "--tip", sha, "--scratch", scratch, "--out", out],
                           capture_output=True, text=True)
        print(f"== hardened {name} run={run} sha={sha[:12]} exit={p.returncode}")
        print(p.stdout.strip())
        if p.stderr.strip():
            print("stderr:", p.stderr.strip()[:400])
        res[f"{name}#{run}"] = p.returncode
        shutil.rmtree(scratch, ignore_errors=True)
print("HARDENED", json.dumps(res))
