#!/usr/bin/env python3
"""MT01Mutants landed-tree fixtures: clones of the round-70 landed tip 73597158.

L            clean clone of the landed tip (must be green with the landed tools)
fx2-nbanner  head banner broken                        -> banner=1
fx2-nprovince PROVINCE.md loses one token (re-anchored) -> province=1
fx2-nclosure calibration pointer names round-68          -> closure_ptr=0
fx2-nharness  calibration row gains a git-dependent run fact -> r41=1 under a
              metadata-free export, 0 under a checkout of the tip
"""
import hashlib
import os
import re
import shutil
import subprocess
import sys

S = "/fast/scratch/hyaku/kama-r70/MT01Mutants"
LANE = "/home/vgpnk/Projects/shokunin/kama-shokunin"
TIP = "73597158ec1cd6707a6f3abe0814615b82580d49"
IDENT = ["-c", "user.name=mt01fixture", "-c", "user.email=mt01@fixture.invalid"]

GIT_FACT = ('; run `python3 -c "import subprocess;'
            "print('GIT_FACT_OK' if subprocess.run(['git','rev-parse','HEAD'],"
            'capture_output=True).returncode == 0 else \'NO_GIT\')"` \u2192 `GIT_FACT_OK`')


def sh(*a):
    p = subprocess.run(a, capture_output=True, text=True)
    if p.returncode != 0:
        raise SystemExit(f"FAILED {a}: {p.stderr}")
    return p.stdout


def clone_at(name, tip=TIP):
    fx = os.path.join(S, name)
    if os.path.exists(fx):
        shutil.rmtree(fx)
    sh("git", "clone", "-q", "--shared", LANE, fx)
    if os.path.realpath(sh("git", "-C", fx, "rev-parse", "--show-toplevel").strip()) != os.path.realpath(fx):
        raise SystemExit(f"{fx}: not its own toplevel")
    sh("git", "-C", fx, "checkout", "-q", "-B", "master", tip)
    return fx


def commit(fx, msg):
    sh("git", "-C", fx, "add", "-A")
    sh("git", "-C", fx, *IDENT, "commit", "-q", "-m", msg)
    rev = sh("git", "-C", fx, "rev-parse", "HEAD").strip()
    if sh("git", "-C", fx, "rev-parse", "--abbrev-ref", "HEAD").strip() != "master":
        raise SystemExit(f"{fx}: fixture commit is not on master")
    return rev


def edit1(path, old, new):
    t = open(path).read()
    if t.count(old) != 1:
        raise SystemExit(f"{path}: expected 1 occurrence of {old[:70]!r}, got {t.count(old)}")
    open(path, "w").write(t.replace(old, new))


def reanchor_province(fx):
    pv = open(os.path.join(fx, "PROVINCE.md"), "rb").read()
    scp = os.path.join(fx, "SCORECARD.md")
    t = open(scp).read()
    m = re.search(r"surface list `PROVINCE\.md` sha256 `([0-9a-f]{64})` \((\d+) lines", t)
    if not m:
        raise SystemExit("coverage PROVINCE anchor not found")
    open(scp, "w").write(t.replace(
        f"`{m.group(1)}` ({m.group(2)} lines",
        f"`{hashlib.sha256(pv).hexdigest()}` ({pv.count(bytes([10]))} lines", 1))


def main():
    fx = clone_at("L")
    print(f"L\t{fx}\t{TIP}")
    fx = clone_at("fx2-nbanner")
    scp = os.path.join(fx, "SCORECARD.md")
    sc = open(scp).read()
    head, sep, rest = sc.partition("\n## ")
    if head.count("Latest measured round: 70") < 1:
        raise SystemExit("banner plant: head has no 'Latest measured round: 70'")
    open(scp, "w").write(head.replace("Latest measured round: 70", "Latest measured round: 69", 1) + sep + rest)
    print(f"fx2-nbanner\t{fx}\t{commit(fx, 'fixture: banner violation')}")

    fx = clone_at("fx2-nprovince")
    edit1(os.path.join(fx, "PROVINCE.md"), "`tools/round69-newest-closure-counter.py`", "`tools/round69-newest-closure-counter`")
    reanchor_province(fx)
    print(f"fx2-nprovince\t{fx}\t{commit(fx, 'fixture: province violation')}")

    fx = clone_at("fx2-nclosure")
    scp = os.path.join(fx, "SCORECARD.md")
    lines = open(scp).read().split("\n")
    hits = [i for i, l in enumerate(lines) if l.startswith("| calibration | **7**")]
    if len(hits) != 1:
        raise SystemExit("nclosure: calibration row not unique")
    i = hits[0]
    row = lines[i]
    m = re.search(r"latest outside closure `corpus/lessons/round-(\d+)-verifier-spotcheck\.md`", row)
    inc = re.search(r"including round (\d+)", row)
    if not m or not inc:
        raise SystemExit(f"nclosure: pointer/including not found in row ({bool(m)}, {bool(inc)})")
    n = int(m.group(1))
    row = row.replace(m.group(0), f"latest outside closure `corpus/lessons/round-{n - 1}-verifier-spotcheck.md`")
    row = row.replace(inc.group(0), f"including round {n - 1}")
    lines[i] = row
    open(scp, "w").write("\n".join(lines))
    print(f"fx2-nclosure\t{fx}\t{commit(fx, 'fixture: closure pointer violation')}")

    fx = clone_at("fx2-nharness")
    scp = os.path.join(fx, "SCORECARD.md")
    lines = open(scp).read().split("\n")
    hits = [i for i, l in enumerate(lines) if l.startswith("| calibration | **7**")]
    i = hits[0]
    if "|" in GIT_FACT:
        raise SystemExit("nharness: fact must not contain a pipe")
    anchor = "\u2192 `CAP_SELFTEST pass=2 fail=0`"
    if lines[i].count(anchor) != 1:
        raise SystemExit("nharness: anchor fact not found exactly once")
    lines[i] = lines[i].replace(anchor, anchor + GIT_FACT, 1)
    open(scp, "w").write("\n".join(lines))
    print(f"fx2-nharness\t{fx}\t{commit(fx, 'fixture: git-dependent run fact')}")


if __name__ == "__main__":
    main()
