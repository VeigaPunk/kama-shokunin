#!/usr/bin/env python3
"""For each SHA-256 argument, find the git blob(s) whose content hashes to it
across all history of REPO, plus the path(s) rev-list --objects reports, and
whether that blob is the current HEAD version at that path.
usage: whois.py <repo> <sha256>..."""
import hashlib
import subprocess
import sys

repo, targets = sys.argv[1], set(sys.argv[2:])


def git(*a, **kw):
    return subprocess.run(["git", "-C", repo, *a], capture_output=True, **kw).stdout


names = {}
lines = [l for l in git("rev-list", "--objects", "--all").decode().split("\n") if l]
for l in lines:
    oid, _, name = l.partition(" ")
    names.setdefault(oid, name)
ids = list(names)
p = subprocess.run(["git", "-C", repo, "cat-file", "--batch"],
                   input="".join(i + "\n" for i in ids).encode(), capture_output=True)
buf, i, hits = p.stdout, 0, {}
while i < len(buf):
    j = buf.index(b"\n", i)
    oid, typ, size = buf[i:j].decode().split()
    size = int(size)
    if typ == "blob":
        h = hashlib.sha256(buf[j + 1:j + 1 + size]).hexdigest()
        if h in targets:
            hits.setdefault(h, []).append((oid, names.get(oid, "?")))
    i = j + 1 + size + 1

for t in sorted(targets):
    got = hits.get(t)
    if not got:
        print(f"{t} NO-BLOB (content is not in any reachable blob)")
        continue
    for oid, path in got[:4]:
        head = git("rev-parse", "--verify", "-q", f"HEAD:{path}").decode().strip()
        print(f"{t} blob={oid} path={path} at_HEAD={'same' if head == oid else 'HISTORICAL (HEAD ' + head[:12] + ')'}")
