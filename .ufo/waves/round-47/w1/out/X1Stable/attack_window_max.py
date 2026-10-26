#!/usr/bin/env python3
"""X1Stable fixture: mass deletion fully restored, then re-deleted below threshold.

Frozen v2 definition (tools/append-only-audit.py docstring, lines 28-35):
  event (commit,file) when numstat deletions >= 20; restored_max = max over the
  window of held(x); status restored when restored_max == deleted.
Construction: an event of 57 deleted lines is fully restored in one commit, then
the same 57 lines are removed again in three commits of 19 lines each. Every
re-deletion is below the 20-line threshold, so it is not an event; the window
maximum was attained at the restore commit and cannot fall. The audited tip holds
none of the 57 lines.
"""
import json
import os
import subprocess
import sys

FIX = sys.argv[1]
TOOL = sys.argv[2]
CONTRACT = sys.argv[3]
V1 = sys.argv[4]
IDENT = ["-c", "user.name=x1st-aoa", "-c", "user.email=x1st-aoa@invalid", "-c", "commit.gpgsign=false"]


def git(*args, inp=None):
    p = subprocess.run(["git", "-C", FIX, *args], input=inp, capture_output=True)
    if p.returncode != 0:
        raise SystemExit(f"git {' '.join(args)}: {p.stderr.decode()[:300]}")
    return p.stdout.decode()


os.makedirs(FIX, exist_ok=True)
git("init", "-q")
top = git("rev-parse", "--show-toplevel").strip()
assert os.path.realpath(top) == os.path.realpath(FIX), (top, FIX)

A = [f"restored-line-{i:03d}" for i in range(100)]
HEADER = "path\trule\tdeclared_at\tnote"
contract = (HEADER + "\n" + f"LOG.md\tA-corr\tAGENTS.md:1\tfixture log append-only\n")


def commit(files, name):
    for rel, body in files.items():
        path = os.path.join(FIX, rel)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "wb") as fh:
            fh.write(body.encode())
    git("add", "-A")
    git(*IDENT, "commit", "-q", "--allow-empty", "-m", name)
    return git("rev-parse", "HEAD").strip()


def body(lines):
    return "".join(x + "\n" for x in lines)


c1 = commit({"LOG.md": body(A), "AGENTS.md": "LOG.md is append-only (fixture)\n",
             "registry/append-only-contract.tsv": contract}, "c1 seed 100 lines")
# event: delete 57 lines (one commit, >= threshold 20)
c2 = commit({"LOG.md": body(A[57:])}, "c2 delete 57 (event)")
# full restoration
c3 = commit({"LOG.md": body(A)}, "c3 restore all 57")
# three sub-threshold re-deletions of exactly the restored lines
state = list(A)
c4 = c5 = c6 = None
for idx, name in enumerate(("c4 delete 19", "c5 delete 19", "c6 delete 19")):
    # delete 19 of the 57 restored lines (A[0:57]) per commit
    drop = A[19 * idx:19 * idx + 19]
    state = [x for x in state if x not in drop]
    c = commit({"LOG.md": body(state)}, name)
    if idx == 0:
        c4 = c
    elif idx == 1:
        c5 = c
    else:
        c6 = c

tip = c6
print(json.dumps({"c1": c1, "event": c2, "restore": c3, "c4": c4, "c5": c5, "c6": c6, "tip": tip}, indent=1))

# run v2 (frozen tool contract) at every post-restore tip
for label, rev in (("after-restore", c3), ("after-1st-19", c4), ("after-2nd-19", c5), ("after-3rd-19", c6)):
    p = subprocess.run([sys.executable, TOOL, "--repo", FIX, "--to", rev, "--contract", CONTRACT, "--json"],
                       capture_output=True, text=True)
    d = json.loads(p.stdout)
    ev = [e for e in d["events"] if e["file"] == "LOG.md"]
    print(f"v2 {label} {rev[:12]} rc={p.returncode} events={json.dumps(ev)} summary={d['summary']}")

# v1 (round-46 tool) at the same tips, for contrast
for label, rev in (("after-restore", c3), ("after-3rd-19", c6)):
    p = subprocess.run([sys.executable, V1, "--repo", FIX, "--to", rev, "--json"],
                       capture_output=True, text=True)
    d = json.loads(p.stdout)
    ev = [e for e in d["events"] if e["file"] == "LOG.md"]
    print(f"v1 {label} {rev[:12]} rc={p.returncode} events={json.dumps(ev)}")

# independent held(tip) under the frozen definition, own code path
def lines_at(rev):
    raw = subprocess.run(["git", "-C", FIX, "show", f"{rev}:LOG.md"], capture_output=True).stdout
    segs = raw.split(b"\n")
    if segs and segs[-1] == b"":
        segs.pop()
    return segs


def deleted_of(parent, commit, path="LOG.md"):
    raw = subprocess.run(["git", "-C", FIX, "diff", "--no-renames", "-U0", parent, commit, "--", path],
                         capture_output=True).stdout
    out, i, lines = [], 0, raw.split(b"\n")
    import re
    HUNK = re.compile(rb"^@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@")
    while i < len(lines):
        m = HUNK.match(lines[i]); i += 1
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


import collections
D = collections.Counter(deleted_of(c2 + "^", c2))
K = collections.Counter(lines_at(c2 + "^")) - D
M = collections.Counter(lines_at(tip))
held_tip = sum(min(n, max(0, M[l] - K[l])) for l, n in D.items())
print(json.dumps({"deleted": sum(D.values()), "held_at_tip": held_tip,
                  "tip_line_count": sum(M.values()), "restored_lines_present_at_tip":
                  sum(min(D[l], M[l]) for l in D)}))
