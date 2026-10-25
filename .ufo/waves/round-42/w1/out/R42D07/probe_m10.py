#!/usr/bin/env python3
"""R42D07: build P-M10 (sep-c2-only with the first external row's path
redirected to a prefix-collision file) and run pristine + M10 there."""
import subprocess, sys

SEAT = "/fast/scratch/kama-r42/seats/R42D07"
D = f"{SEAT}/fixtures/replay"
BIN = "/fast/scratch/kama-r42/seats/R42D07/probe-m10.bin"
ROW = "753bfa7327a75b477d4d14cde71e0e46a40acc3a1408c5504530b78c33a6e226\texternal"
OLDPATH = "/home/vgpnk/.local/opt/llama-b11755-bin-ubuntu-x64.tar.gz"

def g(*a):
    return subprocess.run(["git", "-C", D, *a], check=True, capture_output=True, text=True).stdout

subprocess.run(["git", "-C", D, "checkout", "-q", "--detach", sys.argv[1]], check=True)
led = open(f"{D}/registry/digest-ledger.tsv").read()
assert led.count(OLDPATH) == 1, "external row path anchor"
open(f"{D}/registry/digest-ledger.tsv", "w").write(led.replace(OLDPATH, BIN))
g("add", "-A")
subprocess.run(["git", "-C", D, "-c", "user.name=r42-control",
                "-c", "user.email=r42-control@fixture.invalid",
                "commit", "-q", "--allow-empty", "-m",
                "probe: sep-c2-only with a prefix-collision external artifact"], check=True)
sha = g("rev-parse", "HEAD").strip()
print(f"P-M10={sha}")
with open(f"{SEAT}/probes.rev", "a") as f:
    f.write(f"P-M10={sha}\n")
import os
env = dict(os.environ, TMPDIR=f"{SEAT}/tmp")
for tag, exe in (("pristine", f"{SEAT}/clone/tools/round42-digest-audit.py"),
                 ("M10", f"{SEAT}/mut/M10.py")):
    out = f"{SEAT}/out/{tag}.P-M10.c2.out"
    p = subprocess.run([sys.executable, exe, "--repo", D, "--tip", sha, "--seed", "42",
                        "--out", out], capture_output=True, text=True, env=env, cwd=SEAT)
    with open(out, "a") as f:
        f.write(f"exit={p.returncode}\n")
        if p.stderr.strip():
            f.write(p.stderr.strip() + "\n")
    print(f"{tag}: exit={p.returncode}")
    print("".join(open(out).readlines()[:4]))
