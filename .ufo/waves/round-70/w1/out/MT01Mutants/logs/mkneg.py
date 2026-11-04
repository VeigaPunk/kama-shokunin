#!/usr/bin/env python3
"""MT01Mutants negative fixtures: each is fixture-gl plus ONE planted violation.

fx-nbanner    head banner says 'Latest measured round: 69'      -> banner=1
fx-nprovince  PROVINCE.md loses one indicted token (re-anchored) -> province=1
fx-nclosure   calibration row pointer names round-68             -> closure_ptr=0
fx-nharness   calibration row gains a git-dependent run fact     -> r41=1 under a
              metadata-free export, 0 under a checkout of the tip
"""
import hashlib
import os
import re
import shutil
import subprocess

S = "/fast/scratch/hyaku/kama-r70/MT01Mutants"
SRC = os.path.join(S, "fixture-gl")
BASE = subprocess.run(["git", "-C", SRC, "rev-parse", "HEAD"], capture_output=True,
                      text=True, check=True).stdout.strip()
IDENT = ["-c", "user.name=mt01fixture", "-c", "user.email=mt01@fixture.invalid"]

GIT_FACT = ('; run `python3 -c "import subprocess;'
            "print('GIT_FACT_OK' if subprocess.run(['git','rev-parse','HEAD'],"
            'capture_output=True).returncode == 0 else \'NO_GIT\')"` \u2192 `GIT_FACT_OK`')


def sh(*a):
    p = subprocess.run(a, capture_output=True, text=True)
    if p.returncode != 0:
        raise SystemExit(f"FAILED {a}: {p.stderr}")
    return p.stdout


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
    new = t.replace(f"`{m.group(1)}` ({m.group(2)} lines",
                    f"`{hashlib.sha256(pv).hexdigest()}` ({pv.count(chr(10).encode())} lines", 1)
    open(scp, "w").write(new)


def build(name, fn):
    fx = os.path.join(S, name)
    if os.path.exists(fx):
        shutil.rmtree(fx)
    sh("git", "clone", "-q", "--shared", SRC, fx)
    top = sh("git", "-C", fx, "rev-parse", "--show-toplevel").strip()
    if os.path.realpath(top) != os.path.realpath(fx):
        raise SystemExit(f"{fx}: toplevel {top}")
    sh("git", "-C", fx, "checkout", "-q", "master")
    fn(fx)
    sh("git", "-C", fx, "add", "-A")
    sh("git", "-C", fx, *IDENT, "commit", "-q", "-m", f"fixture: {name}")
    # the clone checked out master, so the fixture commit advanced master itself;
    # a nested clone therefore has a local master (gate-registry-check lane-tip arm)
    rev = sh("git", "-C", fx, "rev-parse", "HEAD").strip()
    if sh("git", "-C", fx, "rev-parse", "--abbrev-ref", "HEAD").strip() != "master":
        raise SystemExit(f"{fx}: fixture commit is not on master")
    print(f"{name}\t{fx}\t{rev}")
    return fx, rev


def nbanner(fx):
    scp = os.path.join(fx, "SCORECARD.md")
    sc = open(scp).read()
    head, sep, rest = sc.partition("\n## ")
    if head.count("Latest measured round: 70") != 1:
        raise SystemExit("banner plant: head does not carry one 'Latest measured round: 70'")
    open(scp, "w").write(head.replace("Latest measured round: 70", "Latest measured round: 69")
                         + sep + rest)


def nprovince(fx):
    pvp = os.path.join(fx, "PROVINCE.md")
    edit1(pvp, "`tools/round69-newest-closure-counter.py`.", ".")
    reanchor_province(fx)


def nclosure(fx):
    scp = os.path.join(fx, "SCORECARD.md")
    t = open(scp).read()
    lines = t.split("\n")
    hits = [i for i, l in enumerate(lines)
            if l.startswith("| calibration | **7**")]
    if len(hits) != 1:
        raise SystemExit("nclosure: calibration row not unique")
    i = hits[0]
    row = lines[i]
    old_ptr = ("latest outside closure `corpus/lessons/round-69-verifier-spotcheck.md`")
    if row.count(old_ptr) != 1 or row.count("including round 69") != 1:
        raise SystemExit("nclosure: row does not carry the round-69 pointer/including pair")
    row = row.replace(old_ptr, "latest outside closure `corpus/lessons/round-68-verifier-spotcheck.md`")
    row = row.replace("including round 69", "including round 68")
    lines[i] = row
    open(scp, "w").write("\n".join(lines))


def nharness(fx):
    scp = os.path.join(fx, "SCORECARD.md")
    t = open(scp).read()
    lines = t.split("\n")
    hits = [i for i, l in enumerate(lines) if l.startswith("| calibration | **7**")]
    if len(hits) != 1:
        raise SystemExit("nharness: calibration row not unique")
    i = hits[0]
    if "|" in GIT_FACT:
        raise SystemExit("nharness: fact must not contain a pipe")
    # insert INSIDE the evidence cell (cell 2), not after the row's trailing pipe:
    # a token appended past the last pipe becomes a 5th cell and is never evaluated.
    anchor = "\u2192 `CAP_SELFTEST pass=2 fail=0`"
    if lines[i].count(anchor) != 1:
        raise SystemExit("nharness: anchor fact not found exactly once")
    lines[i] = lines[i].replace(anchor, anchor + GIT_FACT, 1)
    open(scp, "w").write("\n".join(lines))


if __name__ == "__main__":
    print(f"fixture-gl\t{SRC}\t{BASE}")
    build("fx-nbanner", nbanner)
    build("fx-nprovince", nprovince)
    build("fx-nclosure", nclosure)
    build("fx-nharness", nharness)
