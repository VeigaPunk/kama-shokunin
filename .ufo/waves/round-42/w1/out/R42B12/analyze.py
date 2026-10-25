#!/usr/bin/env python3
"""Seat R42B12 analysis pass: overlap between the two populations, per-round
distribution of the .ufo/ tokens, and the full wrong_unflagged list."""
import hashlib
import json
import re
import subprocess
import sys
from collections import Counter

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
led = {}
if LEDGER in paths:
    txt = git("cat-file", "-p", f"{rev}:{LEDGER}").decode(errors="replace")
    for n, line in enumerate(txt.split("\n")):
        if not line or (n == 0 and line.startswith("digest\t")):
            continue
        c = line.split("\t") + [""] * 7
        led[c[0]] = dict(cls=c[1], path=c[3], correct=c[4], note=c[6])

occ_ufo, occ_in = {}, {}
for path in paths:
    is_ufo = path.startswith(".ufo/") and path.endswith((".md", ".tsv"))
    is_in = not path.startswith(".ufo/") and path != LEDGER and path.endswith((".md", ".tsv"))
    if not (is_ufo or is_in):
        continue
    text = git("cat-file", "-p", f"{rev}:{path}").decode(errors="replace")
    tgt = occ_ufo if is_ufo else occ_in
    for lineno, line in enumerate(text.split("\n"), 1):
        for m in TOKEN.finditer(line):
            tgt.setdefault(m.group(0), []).append((path, lineno))

toks_ufo, toks_in = set(occ_ufo), set(occ_in)
unexp = sorted(t for t in toks_ufo if t not in blobs and t not in led)
wu = [t for t in unexp if t[:8] in pref]
unk = [t for t in unexp if t[:8] not in pref]


def cls(t):
    if t in blobs:
        return "blob"
    if t in led:
        return "ledger:" + led[t]["cls"]
    return "wrong_unflagged" if t[:8] in pref else "unknown"


rounds = Counter()
for t in toks_ufo:
    rs = sorted({o[0].split("/")[2] for o in occ_ufo[t] if o[0].startswith(".ufo/waves/")})
    rounds[",".join(rs) if rs else "(non-wave)"] += 1

out = dict(
    rev=rev, blobs=len(blobs),
    ufo_tokens=len(toks_ufo), in_tokens=len(toks_in),
    overlap=len(toks_ufo & toks_in),
    union=len(toks_ufo | toks_in),
    ufo_blob=sum(1 for t in toks_ufo if t in blobs),
    ufo_ledger=sum(1 for t in toks_ufo if t not in blobs and t in led),
    ufo_unexplained=len(unexp), ufo_wrong_unflagged=len(wu), ufo_unknown=len(unk),
    union_unexplained=len([t for t in (toks_ufo | toks_in) if t not in blobs and t not in led]),
    union_blob=sum(1 for t in (toks_ufo | toks_in) if t in blobs),
    ledger_classes=Counter(cls(t) for t in toks_ufo if t not in blobs and t in led),
    ufo_occurrences=sum(len(v) for v in occ_ufo.values()),
    in_occurrences=sum(len(v) for v in occ_in.values()),
    ufo_occurrences_unexplained=sum(len(occ_ufo[t]) for t in unexp),
    rounds_by_token=rounds.most_common(),
    wrong_unflagged=[dict(token=t, occurrences=len(occ_ufo[t]),
                          first=f"{occ_ufo[t][0][0]}:{occ_ufo[t][0][1]}",
                          lines=[f"{a}:{b}" for a, b in occ_ufo[t]][:6]) for t in wu],
    unknown_top=[dict(token=t, occurrences=len(occ_ufo[t]),
                      files=len({a for a, _ in occ_ufo[t]}),
                      first=f"{occ_ufo[t][0][0]}:{occ_ufo[t][0][1]}") for t in
                 sorted(unk, key=lambda t: -len(occ_ufo[t]))[:10]],
)
print(json.dumps(out, indent=1, default=list))
