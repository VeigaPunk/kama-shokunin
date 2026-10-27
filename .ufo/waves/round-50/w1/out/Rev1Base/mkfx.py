#!/usr/bin/env python3
"""Build a fixture repo whose single commit is a lane tree with one file replaced.

usage: mkfx.py <lane-clone> <src-commit> <fixture-dir> <target-rel-path> <replacement-file>

No working tree is materialised (the lane tree at these revisions holds a deeply nested
round-36 scratch path that a recursive copy cannot reproduce): the fixture repo borrows
the clone's objects through .git/objects/info/alternates, read-tree's the source tree,
replaces one blob with update-index, and commits the result with a throwaway identity
passed per command. Asserts the fixture's toplevel is the fixture dir before the commit.
"""
import os
import subprocess
import sys

lane, src, fx, target, repl = sys.argv[1:6]
IDENT = ["-c", "user.name=r50-rev1base-fixture", "-c", "user.email=r50-rev1base-fixture@invalid",
         "-c", "commit.gpgsign=false"]


def git(*args, inp=None):
    p = subprocess.run(["git", "-C", fx, *args], input=inp, capture_output=True, text=True)
    if p.returncode != 0:
        raise SystemExit(f"git {' '.join(args)}: {p.stderr.strip()[:300]}")
    return p.stdout.strip()


os.makedirs(fx, exist_ok=True)
subprocess.run(["git", "-C", fx, "init", "-q"], check=True)
alt = os.path.join(fx, ".git", "objects", "info")
os.makedirs(alt, exist_ok=True)
with open(os.path.join(alt, "alternates"), "w") as fh:
    fh.write(os.path.realpath(os.path.join(lane, ".git", "objects")) + "\n")
top = git("rev-parse", "--show-toplevel")
if os.path.realpath(top) != os.path.realpath(fx):
    raise SystemExit(f"fixture toplevel {top} is not {fx}")
tree = git("rev-parse", src + "^{tree}")
git("read-tree", tree)
blob = git("hash-object", "-w", repl)
git("update-index", "--add", "--cacheinfo", f"100755,{blob},{target}")
newtree = git("write-tree")
c = git(*IDENT, "commit-tree", newtree, "-m", "fixture: one lane file replaced")
git("update-ref", "HEAD", c)
print(c)
