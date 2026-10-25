#!/usr/bin/env python3
"""Build a synthetic lane-shaped git fixture: 50 commits x 400 files
(4 .md docs + 396 data blobs each) => 20000 files, 200 .md docs, each .md
carrying 5 full SHA-256 digests of data blobs committed in the same commit.

usage: gen.py <repo-dir> <pad-bytes-per-data-file>
"""
import hashlib
import os
import subprocess
import sys

D, pad = sys.argv[1], int(sys.argv[2])
COMMITS, PER_COMMIT, DOCS_PER_COMMIT = 50, 400, 4


def g(*a):
    subprocess.run(["git", "-C", D, *a], check=True, capture_output=True)


os.makedirs(os.path.join(D, "registry"), exist_ok=True)
os.makedirs(os.path.join(D, "data"), exist_ok=True)
os.makedirs(os.path.join(D, "docs"), exist_ok=True)
with open(os.path.join(D, "registry", "digest-ledger.tsv"), "w") as f:
    f.write("digest\tclass\tsubject\tpath\tcorrect\tverified-at\tnote\n")
g("add", "-A")
g("commit", "-q", "-m", "fixture: ledger")

filler = "x" * pad
for c in range(COMMITS):
    ddir = os.path.join(D, "data", f"c{c:02d}")
    os.makedirs(ddir, exist_ok=True)
    digests = []
    for j in range(PER_COMMIT - DOCS_PER_COMMIT):
        body = f"blob {c} {j}\n{filler}"
        rel = f"data/c{c:02d}/f{j:03d}.txt"
        with open(os.path.join(D, rel), "w") as f:
            f.write(body)
        digests.append((hashlib.sha256(body.encode()).hexdigest(), rel))
    for k in range(DOCS_PER_COMMIT):
        rel = f"docs/d{c:02d}_{k}.md"
        with open(os.path.join(D, rel), "w") as f:
            f.write(f"# doc {c}/{k}\n")
            for h, p in digests[k * 5:(k + 1) * 5]:
                f.write(f"- {h}  {p}\n")
    g("add", "-A")
    g("commit", "-q", "-m", f"fixture: commit {c}")

print("built", D, "commits", COMMITS, "files", COMMITS * PER_COMMIT)
