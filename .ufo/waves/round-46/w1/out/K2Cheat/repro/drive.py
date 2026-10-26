#!/usr/bin/env python3
"""Build the C2 cheat candidates in a fixture clone of the lane and score them with
the frozen counter.  Fixture clone lives in K2Cheat scratch; nothing is written to
the lane."""
import json
import os
import shutil
import subprocess
import sys

S = "/fast/scratch/hyaku/kama-r46/K2Cheat"
O = "/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-46/w1/out/K2Cheat"
LANE = "/home/vgpnk/Projects/shokunin/kama-shokunin"
C2 = os.path.join(LANE, "tools/round46-append-audit-check.py")
BASE = "4a2a4d55d09dfacf83dc62d1b3fddae5f6d2a050"
REL_TABLE = "\n| append-only-audit | control | tools/append-only-audit.py | 46 |\n"
ID = ["-c", "user.name=r46-cheat", "-c", "user.email=r46-cheat@invalid", "-c", "commit.gpgsign=false"]
D = os.path.join(S, "fxclone")


def g(*a, check=True):
    p = subprocess.run(["git", "-C", D, *a], capture_output=True, text=True)
    if check and p.returncode != 0:
        raise SystemExit(f"git {' '.join(a)}: {p.stderr}")
    return p


def setup():
    shutil.rmtree(D, ignore_errors=True)
    subprocess.run(["git", "clone", "-q", "--shared", "--no-checkout", LANE, D], check=True)
    top = os.path.realpath(g("rev-parse", "--show-toplevel").stdout.strip())
    assert top == os.path.realpath(D), top


def commit_candidate(name, tool_src):
    g("checkout", "-q", "--detach", BASE)
    dst = os.path.join(D, "tools/append-only-audit.py")
    shutil.copyfile(tool_src, dst)
    with open(os.path.join(D, "SCORECARD.md"), "a") as fh:
        fh.write(REL_TABLE)
    g("add", "-A")
    g(*ID, "commit", "-q", "-m", f"round-46 c2 cheat {name}")
    return g("rev-parse", "HEAD").stdout.strip()


def run(name, sha):
    scratch = os.path.join(S, "c2s-" + name)
    shutil.rmtree(scratch, ignore_errors=True)
    os.makedirs(scratch, exist_ok=True)
    out = os.path.join(O, "receipts", f"{name}.c2.out")
    p = subprocess.run([sys.executable, C2, "--repo", D, "--tip", sha, "--scratch", scratch, "--out", out],
                       capture_output=True, text=True)
    with open(os.path.join(O, "receipts", f"{name}.c2.stderr"), "w") as fh:
        fh.write(p.stderr)
    print(f"== {name} sha={sha[:12]} exit={p.returncode}")
    print(p.stdout.strip())
    shutil.rmtree(scratch, ignore_errors=True)
    return p.returncode


def main():
    os.makedirs(os.path.join(O, "receipts"), exist_ok=True)
    setup()
    sys.path.insert(0, os.path.dirname(C2))
    cands = [(n, os.path.join(O, "tools", n + ".py")) for n in
             ("t1-repo-import", "t2-fixedpath-import", "t3-fixture-shape", "t4-selftest-only")]
    # baseline: the genuine tool shipped at 4a2a4d55 plus the missing SCORECARD row
    real = os.path.join(S, "real-tool.py")
    with open(real, "wb") as fh:
        fh.write(subprocess.run(["git", "-C", LANE, "show", f"{BASE}:tools/append-only-audit.py"],
                                capture_output=True).stdout)
    cands.append(("baseline-real-plus-table", real))
    results = {}
    for name, src in cands:
        sha = commit_candidate(name, src)
        results[name] = run(name, sha)
    with open(os.path.join(O, "receipts", "drivers.json"), "w") as fh:
        json.dump({"base": BASE, "results": results}, fh, indent=1)
    print("DRIVER DONE", results)


if __name__ == "__main__":
    main()
