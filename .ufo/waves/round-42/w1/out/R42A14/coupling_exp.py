#!/usr/bin/env python3
"""R42A14 extension: (A) reproduce the committed sep-c1-only receipt at its own tip,
(B) hunk-level C1-only world: sep-c1-only file set with the round-42 canonical
capability block (C2's SCORECARD text) removed."""
import os, shutil, subprocess, sys, tempfile

LANE = "/fast/scratch/kama-r42/seats/R42A14/clone"
BASE = "0b606b03bf0b2a87b791aa537f6c72c941624cf0"
SEAT = "/fast/scratch/kama-r42/seats/R42A14"
OUT = os.path.join(SEAT, "exp")
os.makedirs(OUT, exist_ok=True)
C1 = os.path.join(LANE, "tools/round42-selfdesc-reconcile.py")
C2_FILES = ["tools/digest-ledger.py", "registry/digest-ledger.tsv"]
C3_FILES = ["corpus/knowledge/context-capacity-engine-sides.md", "corpus/lessons/round-42.md"]
C3_DIRS = [".ufo/waves/round-42/c3", ".ufo/waves/round-42/assimilation"]
ID = ["-c", "user.name=r42a14-fixture", "-c", "user.email=r42a14@fixture.invalid"]


def g(d, *a):
    return subprocess.run(["git", "-C", d, *a], check=True, capture_output=True, text=True).stdout


def show(rev, p):
    return subprocess.run(["git", "-C", LANE, "cat-file", "-p", f"{rev}:{p}"],
                          capture_output=True, text=True).stdout


def sandbox(rev):
    d = tempfile.mkdtemp(prefix="r42a14-exp-", dir=SEAT)
    subprocess.run(["git", "clone", "-q", "--no-local", LANE, d], check=True)
    assert os.path.realpath(g(d, "rev-parse", "--show-toplevel").strip()) == os.path.realpath(d), d
    g(d, "checkout", "-q", "--detach", rev)
    for p in C2_FILES + C3_FILES:
        fp = os.path.join(d, p)
        if os.path.exists(fp):
            os.remove(fp)
    for p in C3_DIRS:
        fp = os.path.join(d, p)
        if os.path.isdir(fp):
            shutil.rmtree(fp)
    for p in ("corpus/SOURCES.md", "corpus/README.md"):
        open(os.path.join(d, p), "w").write(show(BASE, p))
    return d


def commit(d, msg):
    g(d, "add", "-A")
    subprocess.run(["git", "-C", d, *ID, "commit", "-q", "--allow-empty", "-m", msg], check=True)
    return g(d, "rev-parse", "HEAD").strip()


def score(name, d, rev):
    out = os.path.join(OUT, f"{name}.c1.out")
    p = subprocess.run([sys.executable, C1, "--repo", d, "--tip", rev, "--out", out],
                       capture_output=True, text=True, cwd=LANE)
    with open(out, "a") as f:
        f.write(f"exit={p.returncode}\n")
    print(f"== {name} tip={rev} exit={p.returncode}")
    print(open(out).read())
    return p.returncode


# A: the tip the committed sep-c1-only receipt was generated from (pre-decouple)
d = sandbox("2793eb5")
score("A-predeecouple-2793eb5", d, commit(d, "sep: C1 files only @2793eb5"))
print("sandboxA", d)

# B: claim tip, sep-c1-only file set, C2's round-42 canonical block deleted
d = sandbox("3d9bd8d72366e281fab291874524130428ee423d")
sc = os.path.join(d, "SCORECARD.md")
lines = open(sc).read().split("\n")
start = lines.index("**Capabilities — canonical list as of round 42**")
end = start + 1
while end < len(lines) and not lines[end].startswith("### Planned (round 43)"):
    end += 1
del lines[start:end]
open(sc, "w").write("\n".join(lines))
score("B-tip-no-c2canon", d, commit(d, "sep: C1 files only @tip, no round-42 canonical block"))
print("sandboxB", d)
