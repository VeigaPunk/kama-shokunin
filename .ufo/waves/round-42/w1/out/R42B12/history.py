#!/usr/bin/env python3
"""Seat R42B12: of the .ufo/ unexplained tokens, how many hash a blob that exists
anywhere in the repo's refs (stale-but-real) versus nowhere at all."""
import hashlib
import json
import re
import subprocess
import sys

TOKEN = re.compile(r"(?<![0-9a-f])[0-9a-f]{64}(?![0-9a-f])")
LEDGER = "registry/digest-ledger.tsv"
REPO, REV = sys.argv[1], sys.argv[2]


def git(*a):
    p = subprocess.run(["git", "-C", REPO, *a], capture_output=True)
    if p.returncode:
        raise SystemExit(p.stderr.decode())
    return p.stdout


def blob_sha_set(args):
    ids = [l.split(" ", 1)[0] for l in git(*args).decode().split("\n") if l]
    p = subprocess.run(["git", "-C", REPO, "cat-file", "--batch"],
                       input="".join(i + "\n" for i in ids).encode(), capture_output=True)
    out, buf, i = set(), p.stdout, 0
    while i < len(buf):
        j = buf.index(b"\n", i)
        _, typ, size = buf[i:j].decode().split()
        size = int(size)
        if typ == "blob":
            out.add(hashlib.sha256(buf[j + 1:j + 1 + size]).hexdigest())
        i = j + 1 + size + 1
    return out


rev = git("rev-parse", "--verify", REV + "^{commit}").decode().strip()
at_rev = blob_sha_set(["rev-list", "--objects", rev])
all_refs = blob_sha_set(["rev-list", "--objects", "--all"])
paths = [x for x in git("ls-tree", "-r", "--name-only", "-z", rev).decode().split("\0") if x]
led = {}
if LEDGER in paths:
    txt = git("cat-file", "-p", f"{rev}:{LEDGER}").decode(errors="replace")
    for n, line in enumerate(txt.split("\n")):
        if not line or (n == 0 and line.startswith("digest\t")):
            continue
        c = line.split("\t") + [""] * 7
        led[c[0]] = c[1]

occ = {}
for path in paths:
    if not (path.startswith(".ufo/") and path.endswith((".md", ".tsv"))):
        continue
    text = git("cat-file", "-p", f"{rev}:{path}").decode(errors="replace")
    for lineno, line in enumerate(text.split("\n"), 1):
        for m in TOKEN.finditer(line):
            occ.setdefault(m.group(0), []).append((path, lineno))

pref = {b[:8] for b in at_rev}
unexp = {t: o for t, o in occ.items() if t not in at_rev and t not in led}
hist = {t: o for t, o in unexp.items() if t in all_refs}
nowhere = {t: o for t, o in unexp.items() if t not in all_refs}
zero = [t for t in unexp if t == "0" * 64]
print(json.dumps(dict(
    rev=rev, blobs_at_rev=len(at_rev), blobs_all_refs=len(all_refs),
    ufo_tokens=len(occ), ufo_unexplained=len(unexp),
    stale_real=len(hist), stale_real_occurrences=sum(len(o) for o in hist.values()),
    nowhere=len(nowhere), nowhere_occurrences=sum(len(o) for o in nowhere.values()),
    all_zero=zero,
    wrong_unflagged_total=sum(1 for t in unexp if t[:8] in pref),
    wrong_unflagged_stale_real=[t for t in unexp if t[:8] in pref and t in all_refs],
    top_stale=[dict(token=t, occurrences=len(o), first=f"{o[0][0]}:{o[0][1]}")
               for t, o in sorted(hist.items(), key=lambda kv: -len(kv[1]))[:10]],
    top_nowhere=[dict(token=t, occurrences=len(o), first=f"{o[0][0]}:{o[0][1]}")
                 for t, o in sorted(nowhere.items(), key=lambda kv: -len(kv[1]))[:10]],
    pop24_in_history="612b0a74f3eebaa9074bdde8ecd8f194f55ebaf9a35ab2b975fddbff8dd2ed88" in all_refs,
), indent=1))
