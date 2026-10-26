#!/usr/bin/env python3
"""Seat W1F02 measurement, not a frozen counter.

Reproduces, independently of tools/round43-hexrun-audit.py, the population its
docstring fixes (tools/round43-hexrun-audit.py:15-20,46-54):
  documents  blobs at REV whose path ends .md or .tsv, outside .ufo/, except
             registry/hexrun-ledger.tsv and registry/digest-ledger.tsv
  token      maximal [0-9a-f] run 32 <= L <= 127, L != 64, no [0-9A-Za-z] adjacent
  class      lane_oid (L==40, object exists) | md5_blob (L==32, MD5 of a blob)
             | unexplained
and the digest-ledger population (exact 64-hex runs, tools/digest-ledger.py:67).

Usage: hexrun-population.py REPO REV
"""
import collections
import hashlib
import re
import subprocess
import sys

repo, rev = sys.argv[1], sys.argv[2]


def git(*a):
    return subprocess.run(["git", "-C", repo, *a], capture_output=True, text=True).stdout


files = [f for f in git("ls-tree", "-r", "--name-only", rev).split()
         if f.endswith((".md", ".tsv")) and not f.startswith(".ufo/")
         and f not in ("registry/hexrun-ledger.tsv", "registry/digest-ledger.tsv")]
token = re.compile(r"(?<![0-9A-Za-z])[0-9a-f]{32,127}(?![0-9A-Za-z])")
d64 = set()
non64 = set()
by_len = collections.Counter()
for f in files:
    body = git("show", f"{rev}:{f}")
    for m in token.finditer(body):
        s = m.group(0)
        by_len[len(s)] += 1
        if len(s) == 64:
            d64.add(s)
        else:
            non64.add(s)

blobs = [l.split()[2] for l in git("ls-tree", "-r", rev).splitlines() if l]
md5s = set()
for b in blobs:
    raw = subprocess.run(["git", "-C", repo, "cat-file", "blob", b], capture_output=True).stdout
    md5s.add(hashlib.md5(raw).hexdigest())

objects = set(git("cat-file", "--batch-check", "--batch-all-objects").split()[::3])
lane = {t for t in non64 if len(t) == 40 and t in objects}
md5 = {t for t in non64 if len(t) == 32 and t in md5s}
unexplained = non64 - lane - md5
print(f"documents={len(files)}")
print(f"runs_by_length={dict(sorted(by_len.items()))}")
print(f"distinct_64={len(d64)} distinct_non64={len(non64)}")
print(f"lane_oid={len(lane)} md5_blob={len(md5)} unexplained={len(unexplained)}")
print("unexplained_by_length=" + str(dict(sorted(collections.Counter(len(t) for t in unexplained).items()))))
