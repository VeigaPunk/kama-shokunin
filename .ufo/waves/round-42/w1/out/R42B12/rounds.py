#!/usr/bin/env python3
"""Seat R42B12: per-round distribution of .ufo/ tokens and docs with unexplained."""
import hashlib
import json
import re
import subprocess
import sys
from collections import Counter, defaultdict

TOKEN = re.compile(r"(?<![0-9a-f])[0-9a-f]{64}(?![0-9a-f])")
LEDGER = "registry/digest-ledger.tsv"
REPO, REV = sys.argv[1], sys.argv[2]


def git(*a):
    p = subprocess.run(["git", "-C", REPO, *a], capture_output=True)
    if p.returncode:
        raise SystemExit(p.stderr.decode())
    return p.stdout


rev = git("rev-parse", "--verify", REV + "^{commit}").decode().strip()
ids = [l.split(" ", 1)[0] for l in git("rev-list", "--objects", rev).decode().split("\n") if l]
p = subprocess.run(["git", "-C", REPO, "cat-file", "--batch"],
                   input="".join(i + "\n" for i in ids).encode(), capture_output=True)
blobs, buf, i = set(), p.stdout, 0
while i < len(buf):
    j = buf.index(b"\n", i)
    _, typ, size = buf[i:j].decode().split()
    size = int(size)
    if typ == "blob":
        blobs.add(hashlib.sha256(buf[j + 1:j + 1 + size]).hexdigest())
    i = j + 1 + size + 1
pref = {b[:8] for b in blobs}
paths = [x for x in git("ls-tree", "-r", "--name-only", "-z", rev).decode().split("\0") if x]
led = set()
if LEDGER in paths:
    for n, line in enumerate(git("cat-file", "-p", f"{rev}:{LEDGER}").decode(errors="replace").split("\n")):
        if line and not (n == 0 and line.startswith("digest\t")):
            led.add(line.split("\t")[0])

tok_round, docs_with_unexp, docs_with_tok = Counter(), set(), set()
for path in paths:
    if not (path.startswith(".ufo/") and path.endswith((".md", ".tsv"))):
        continue
    text = git("cat-file", "-p", f"{rev}:{path}").decode(errors="replace")
    toks = set()
    for line in text.split("\n"):
        toks |= set(TOKEN.findall(line))
    if not toks:
        continue
    docs_with_tok.add(path)
    rnd = path.split("/")[2] if path.startswith(".ufo/waves/") else "(non-wave)"
    for t in toks:
        tok_round[rnd] += 1
        if t not in blobs and t not in led:
            docs_with_unexp.add(path)
print(json.dumps(dict(
    docs_with_tokens=len(docs_with_tok),
    docs_with_unexplained=len(docs_with_unexp),
    tokens_by_round=sorted(tok_round.items(), key=lambda kv: -kv[1]),
), indent=1))
