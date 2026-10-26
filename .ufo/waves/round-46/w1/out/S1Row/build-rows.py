#!/usr/bin/env python3
"""build-rows.py - rebuild the validated scratch copy of corpus/SOURCES.md and run the frozen census.

Read-only on the lane: the copy is written next to this script (SOURCES-validated.md, a symlink
farm of the lane's own directories is created under a temporary directory).
The two row lines come from rows-validated.txt so no long row is retyped here.
"""
import os
import subprocess
import sys
import tempfile

LANE = "/home/vgpnk/Projects/shokunin/kama-shokunin"
HERE = os.path.dirname(os.path.abspath(__file__))
CENSUS = "/home/vgpnk/Projects/shokunin/scripts/sources-census.sh"
rows = open(os.path.join(HERE, "rows-validated.txt")).read().rstrip("\n").split("\n")
assert len(rows) == 2, len(rows)

src = open(os.path.join(LANE, "corpus/SOURCES.md")).read().split("\n")
anchor = [i for i, x in enumerate(src) if x.startswith("| S485 |")]
assert len(anchor) == 1, anchor
at = anchor[0] + 1
out = src[:at] + rows + src[at:]

d = tempfile.mkdtemp(prefix="s1row-")
os.makedirs(os.path.join(d, "corpus"))
for name in sorted(os.listdir(LANE)):
    if name in ("corpus",):
        continue
    os.symlink(os.path.join(LANE, name), os.path.join(d, name))
for name in sorted(os.listdir(os.path.join(LANE, "corpus"))):
    if name == "SOURCES.md":
        continue
    os.symlink(os.path.join(LANE, "corpus", name), os.path.join(d, "corpus", name))
copy = os.path.join(d, "corpus/SOURCES.md")
open(copy, "w").write("\n".join(out))
open(os.path.join(HERE, "SOURCES-validated.md"), "w").write("\n".join(out))
print("scratch", copy)
p = subprocess.run(["bash", CENSUS, "validate", "--file", copy, "--today", "2026-10-26"],
                   capture_output=True, text=True)
sys.stdout.write(p.stdout)
print("validate exit", p.returncode)
q = subprocess.run(["bash", CENSUS, "census", "--file", copy], capture_output=True, text=True)
sys.stdout.write(q.stdout)
print("census exit", q.returncode)
