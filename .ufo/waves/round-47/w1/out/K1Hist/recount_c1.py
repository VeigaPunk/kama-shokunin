#!/usr/bin/env python3
# K1Hist independent recount of C1 (append-only audit v2) — built from the frozen
# counter's published definitions, without reading the tool's or counter's code.
import collections, fnmatch, json, subprocess, sys

REPO = sys.argv[1]
TIP = sys.argv[2]
CONTRACT = sys.argv[3]
THRESHOLD = 20
EMPTY_TREE = "4b825dc642cb6eb9a060e54bf8d69288fbee4904"

def git(*args):
    p = subprocess.run(["git", "-C", REPO, *args], capture_output=True)
    if p.returncode != 0:
        raise SystemExit("git %r failed: %s" % (args, p.stderr.decode("utf-8", "replace")))
    return p.stdout

def lines_of(data):
    segs = data.split(b"\n")
    if segs and segs[-1] == b"":
        segs.pop()
    return segs

# ---- commits (topo order, oldest first) and first parents ----
raw = git("rev-list", "--parents", "--topo-order", "--reverse", TIP).decode().splitlines()
commits = []
parents = {}
for line in raw:
    parts = line.split()
    commits.append(parts[0])
    parents[parts[0]] = parts[1] if len(parts) > 1 else None

# ---- contract at tip ----
ctext = git("cat-file", "blob", TIP + ":" + CONTRACT).decode("utf-8", "replace")
lines = ctext.split("\n")
assert lines[0].rstrip("\r") == "path\trule\tdeclared_at\tnote", "bad header: %r" % lines[0]
patterns = []
for n, line in enumerate(lines[1:], 2):
    if not line.strip():
        continue
    cells = line.split("\t")
    assert len(cells) == 4, "contract line %d has %d cells" % (n, len(cells))
    patterns.append(cells[0].strip())

tip_files = [f for f in git("ls-tree", "-r", "--name-only", TIP).decode().split("\n") if f]
contracted = sorted({f for f in tip_files for pat in patterns if fnmatch.fnmatchcase(f, pat)})

# ---- per-commit numstat deletions for contracted files ----
def numstat_deletions(c):
    base = parents[c] or EMPTY_TREE
    out = git("diff", "--numstat", "--no-renames", base, c, "--", *contracted).decode()
    dels = {}
    for line in out.splitlines():
        parts = line.split("\t")
        if len(parts) != 3:
            continue
        a, d, path = parts
        if a != "-" and d != "-":
            dels[path] = int(d)
        else:
            dels[path] = None
    return dels

def deleted_multiset(c, path):
    base = parents[c] or EMPTY_TREE
    out = git("diff", "--unified=0", "--no-color", "--no-ext-diff",
              "--no-renames", base, c, "--", path)
    D = collections.Counter()
    inhunk = False
    for b in out.split(b"\n"):
        if b.startswith(b"@@"):
            inhunk = True
            continue
        if inhunk and b.startswith(b"-"):
            D[b[1:]] += 1
    return D

events = []
for c in commits:
    dels = numstat_deletions(c)
    for path in contracted:
        d = dels.get(path)
        if d is None or d < THRESHOLD:
            continue
        D = deleted_multiset(c, path)
        if sum(D.values()) != d:
            raise SystemExit("hunk-vs-numstat mismatch %s %s %d vs %d" % (c, path, sum(D.values()), d))
        events.append({"commit": c, "file": path, "deleted": d, "D": D})

# ---- window restoration ----
cat = subprocess.Popen(["git", "-C", REPO, "cat-file", "--batch"],
                       stdin=subprocess.PIPE, stdout=subprocess.PIPE)

def blob_at(c, path):
    cat.stdin.write((c + ":" + path + "\n").encode())
    cat.stdin.flush()
    head = cat.stdout.readline()
    if head.endswith(b" missing\n"):
        return None
    size = int(head.split()[-1])
    data = cat.stdout.read(size)
    cat.stdout.read(1)
    return data

index = {c: i for i, c in enumerate(commits)}
results = []
for ev in events:
    c, path, deleted, D = ev["commit"], ev["file"], ev["deleted"], ev["D"]
    parent = parents[c]
    Mp = collections.Counter(lines_of(blob_at(parent, path))) if parent else collections.Counter()
    K = collections.Counter()
    for v, cnt in Mp.items():
        K[v] = max(0, cnt - D.get(v, 0))
    best = 0
    best_commit = None
    restored_by = None
    for j in range(index[c], len(commits)):
        w = commits[j]
        data = blob_at(w, path)
        Mx = collections.Counter(lines_of(data)) if data is not None else collections.Counter()
        held = sum(min(dv, max(0, Mx[v] - K[v])) for v, dv in D.items())
        if held > best:
            best, best_commit = held, w
        if restored_by is None and held == deleted:
            restored_by = w
    if best == 0:
        best_commit = None
    status = "restored" if best == deleted else ("unrestored" if best == 0 else "partial")
    results.append({"commit": c, "file": path, "deleted": deleted,
                    "restored_max": best, "restored_best": best_commit,
                    "restored_by": restored_by, "status": status})

out = {"schema": "append-only-audit/v2", "to": TIP, "threshold": THRESHOLD,
       "files": contracted, "commits": len(commits),
       "events": [{k: v for k, v in r.items() if k != "D"} for r in results]}
json.dump(out, sys.stdout, indent=1)
print()
