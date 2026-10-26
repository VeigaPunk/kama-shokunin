#!/usr/bin/env python3
"""X1Stable: how far is restored_max (window maximum) from the audited tip?

The frozen v2 contract (tools/append-only-audit.py docstring lines 28-35) reports
restored_max = max over the window of held(x). This script recomputes held(tip)
with its own diff/line reading and lists the post-restore commits that delete
lines from an event's file, so the gap between "was restored once" and "is held
at the audited tip" is visible per event.
"""
import collections
import json
import re
import subprocess
import sys

REPO, TIP = sys.argv[1], sys.argv[2]
THRESHOLD = 20
FILES = ["SCORECARD.md", "LOG.md", "corpus/QUALITY.md", "corpus/README.md", "corpus/SOURCES.md",
         "corpus/lessons/*.md", "registry/history/DELTA.md"]
HUNK = re.compile(rb"^@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@")


def git(*args):
    p = subprocess.run(["git", "-C", REPO, *args], capture_output=True)
    if p.returncode != 0:
        raise SystemExit(f"git {' '.join(args)}: {p.stderr.decode()[:200]}")
    return p.stdout


def ls(rev):
    return [x for x in git("ls-tree", "-r", "--name-only", rev).decode().split("\n") if x]


def expand(rev):
    import fnmatch
    tree = ls(rev)
    return sorted({t for t in tree if any(fnmatch.fnmatchcase(t, p) for p in FILES)})


def split_lines(data):
    segs = data.split(b"\n")
    if segs and segs[-1] == b"":
        segs.pop()
    return segs


def blob_lines(rev, path):
    p = subprocess.run(["git", "-C", REPO, "show", f"{rev}:{path}"], capture_output=True)
    return collections.Counter(split_lines(p.stdout)) if p.returncode == 0 else collections.Counter()


def diff_deleted(parent, commit, path):
    raw = git("diff", "--no-renames", "-U0", "--text", parent, commit, "--", path)
    out, lines, i = [], raw.split(b"\n"), 0
    while i < len(lines):
        m = HUNK.match(lines[i])
        i += 1
        if not m:
            continue
        nd = int(m.group(2)) if m.group(2) is not None else 1
        na = int(m.group(4)) if m.group(4) is not None else 1
        gd = ga = 0
        while i < len(lines) and (gd < nd or ga < na):
            ln = lines[i]
            if ln.startswith(b"-") and gd < nd:
                out.append(ln[1:]); gd += 1
            elif ln.startswith(b"+") and ga < na:
                ga += 1
            i += 1
    return out


tip = git("rev-parse", "--verify", TIP + "^{commit}").decode().strip()
files = expand(tip)
revs = git("rev-list", "--topo-order", "--reverse", "--parents", tip).decode().split("\n")
commits, parents = [], {}
for line in revs:
    parts = line.split()
    if parts:
        commits.append(parts[0]); parents[parts[0]] = parts[1] if len(parts) > 1 else None
idx = {c: i for i, c in enumerate(commits)}
rows = []
for c in commits:
    p = parents[c]
    if p is None:
        continue
    for f in files:
        dl = diff_deleted(p, c, f)
        if len(dl) < THRESHOLD:
            continue
        D = collections.Counter(dl)
        K = blob_lines(p, f) - D
        window = commits[idx[c]:]
        best = best_c = by = None
        best = 0
        for x in window:
            M = blob_lines(x, f)
            h = sum(min(n, max(0, M[l] - K[l])) for l, n in D.items())
            if h > best:
                best, best_c = h, x
            if h == len(dl):
                by = x
                break
        M_tip = blob_lines(tip, f)
        held_tip = sum(min(n, max(0, M_tip[l] - K[l])) for l, n in D.items())
        # post-restore deletions of the event's file, per commit
        after = []
        for x in commits[idx[c] + 1:]:
            px = parents[x]
            n = len(diff_deleted(px, x, f))
            if n:
                after.append((x, n))
        rows.append({"commit": c, "file": f, "deleted": len(dl), "restored_max": best,
                     "restored_best": best_c, "restored_by": by,
                     "held_at_tip": held_tip, "gap": best - held_tip,
                     "post_restore_commits_touching_file": len(after),
                     "post_restore_max_single_deletion": max([n for _, n in after], default=0),
                     "post_restore_deletions": sum(n for _, n in after),
                     "post_restore_subthreshold_commits": sum(1 for _, n in after if n < THRESHOLD),
                     "held_at_tip_vs_deleted": f"{held_tip}/{len(dl)}"})
print(json.dumps({"tip": tip, "files": len(files), "events": rows}, indent=1))
