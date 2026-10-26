#!/usr/bin/env python3
"""M2Ctr golden-pair runner: runs one counter variant against tip and base."""
import os
import subprocess
import sys

TIP = "74558c71c38ceaeace15fd4cf8aa9d84977584b1"
BASE = "438127bc01ff3b99f98468549d58046f932490ef"
S = "/fast/scratch/hyaku/kama-r49/M2Ctr"
LANE = os.path.join(S, "lane")


def run(variant_path, tag, tip):
    outdir = os.path.join(S, "runs")
    os.makedirs(outdir, exist_ok=True)
    stem = os.path.join(outdir, variant_path.replace("/", "_") + "." + tag)
    scratch = os.path.join(S, "scratch", variant_path.replace("/", "_") + "." + tag)
    os.makedirs(scratch, exist_ok=True)
    env = dict(os.environ, TMPDIR=scratch)
    with open(stem + ".out", "wb") as fh:
        p = subprocess.run(["timeout", "900", sys.executable, os.path.join(S, variant_path + ".py"),
                            "--repo", LANE, "--tip", tip, "--scratch", scratch], stdout=fh,
                           stderr=subprocess.STDOUT, env=env)
    with open(stem + ".exit", "w") as fh:
        fh.write(str(p.returncode))


if __name__ == "__main__":
    run(sys.argv[1], sys.argv[2], TIP if sys.argv[2] == "tip" else BASE)
