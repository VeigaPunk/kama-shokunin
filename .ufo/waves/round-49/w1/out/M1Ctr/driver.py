#!/usr/bin/env python3
"""Run C1 counter invocations; one job per argv line: <counter> <tag> <repo> <tip>.
Outputs: $S/results/<tag>.stdout / .stderr / .exit (exit code of the counter).
Timeouts: 900s per run. The counter's own scratch is $S (cleaned by the counter).
"""
import os
import subprocess
import sys

S = "/fast/scratch/hyaku/kama-r49/M1Ctr"
RES = os.path.join(S, "results")
os.makedirs(RES, exist_ok=True)
env = dict(os.environ)
env["TMPDIR"] = S

jobs = [line.split() for line in sys.stdin.read().splitlines() if line.strip()]
jobs = [(c, t, r, tip) for c, t, r, tip in jobs]
for counter, tag, repo, tip in jobs:
    out = os.path.join(RES, tag + ".stdout")
    err = os.path.join(RES, tag + ".stderr")
    ex = os.path.join(RES, tag + ".exit")
    with open(out, "wb") as fo, open(err, "wb") as fe:
        try:
            p = subprocess.run([sys.executable, counter, "--repo", repo, "--tip", tip,
                                "--scratch", S, "--out", os.path.join(RES, tag + ".txt")],
                               env=env, stdout=fo, stderr=fe, timeout=900)
            code = p.returncode
        except subprocess.TimeoutExpired:
            code = -999
    with open(ex, "w") as fh:
        fh.write(str(code) + "\n")
    print(tag, "exit=", code, flush=True)
