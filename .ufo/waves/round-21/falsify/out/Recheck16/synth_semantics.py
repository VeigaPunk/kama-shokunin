#!/usr/bin/env python3
"""Recheck16: does `cat-file --batch-check` (the tool's lookup) classify tokens differently
from a per-token commit-only resolution? Builds throwaway repos under /tmp scratch only.

Uses 4-hex prefixes (git's minimum) to make collisions cheap to construct; the matching
rule is the same for longer prefixes [INFERENCE: not executed at 7 hex].
Imports the tool's real lookup() from the scratch lane clone (read-only use; no bytecode written).
"""
import hashlib
import importlib.util
import json
import os
import shutil
import subprocess
import sys

sys.dont_write_bytecode = True
TOOL = "/tmp/kama-r21-Recheck16/lane/tools/report-landing-audit.py"
ROOT = "/tmp/kama-r21-Recheck16/synth"
ENV = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
ENV.update(GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_NOSYSTEM="1")
CENV = dict(ENV, GIT_AUTHOR_NAME="a", GIT_AUTHOR_EMAIL="a@x", GIT_COMMITTER_NAME="a",
            GIT_COMMITTER_EMAIL="a@x", GIT_AUTHOR_DATE="@1000 +0000",
            GIT_COMMITTER_DATE="@1000 +0000")

spec = importlib.util.spec_from_file_location("rla", TOOL)
rla = importlib.util.module_from_spec(spec)
spec.loader.exec_module(rla)


def run(repo, *args, inp=None, env=None):
    p = subprocess.run(["git", "-C", repo, *args], input=inp, capture_output=True,
                       env=env or ENV)
    if p.returncode:
        raise SystemExit(f"FATAL git {args} rc={p.returncode} {p.stderr.decode(errors='replace')}")
    return p.stdout.decode().strip()


def obj_sha(kind, content):
    return hashlib.sha1(b"%s %d\0" % (kind.encode(), len(content)) + content).hexdigest()


def pertoken(repos, tok):
    """Independent per-token rule: commit-only candidates per repo; unique in any repo
    -> found; several commits and none unique -> ambiguous; else missing."""
    result = "missing"
    for repo in repos:
        p = subprocess.run(["git", "-C", repo, "rev-parse", f"--disambiguate={tok}"],
                           capture_output=True, env=ENV)
        if p.returncode:
            continue
        cands = [c for c in p.stdout.decode().split() if len(c) == 40]
        commits = [c for c in cands if run(repo, "cat-file", "-t", c) == "commit"]
        if not commits:
            continue
        if len(commits) == 1:
            return "found"
        result = "ambiguous"
    return result


def exists_any(repos, tok):
    return any(subprocess.run(["git", "-C", r, "cat-file", "-e", tok], env=ENV).returncode == 0
               for r in repos)


shutil.rmtree(ROOT, ignore_errors=True)
LANE_S, FLEET_S = f"{ROOT}/lane", f"{ROOT}/fleet"
for r in (LANE_S, FLEET_S):
    os.makedirs(r)
    run(r, "init", "-q", "-b", "master")
EMPTY = run(LANE_S, "hash-object", "-t", "tree", "-w", "--stdin", inp=b"")

# Lane: commits until two share a 4-hex prefix (ambiguous pair P).
seen, lane_commits, pair = {}, [], None
i = 0
while pair is None:
    c = run(LANE_S, "commit-tree", EMPTY, "-m", f"lane {i}", env=CENV)
    lane_commits.append(c)
    p4 = c[:4]
    if p4 in seen and pair is None:
        pair = (seen[p4], c)
    seen.setdefault(p4, c)
    i += 1
P = pair[0][:4]
used = {c[:4] for c in lane_commits}
# X: a unique lane commit prefix that a blob will also match (commit+blob collision).
X_commit = next(c for c in lane_commits if sum(x.startswith(c[:4]) for x in lane_commits) == 1)
X = X_commit[:4]
blob_for_X = None
k = 0
while blob_for_X is None:
    content = f"xblob {k}".encode()
    if obj_sha("blob", content).startswith(X):
        blob_for_X = content
    k += 1
run(LANE_S, "hash-object", "-w", "--stdin", inp=blob_for_X)
# Q: a prefix used by no lane object; two blobs (no commit) will share it.
Q = next(f"{n:04x}" for n in range(0x10000) if f"{n:04x}" not in used and f"{n:04x}" != X)
qblobs, k = [], 0
while len(qblobs) < 2:
    content = f"qblob {k}".encode()
    if obj_sha("blob", content).startswith(Q):
        qblobs.append(content)
    k += 1
for content in qblobs:
    run(LANE_S, "hash-object", "-w", "--stdin", inp=content)
blob_full = obj_sha("blob", qblobs[0])
commit_full = pair[1]

# Fleet: one commit whose sha begins with P, so P is ambiguous in lane but unique in fleet.
k = 0
while True:
    content = (f"tree {EMPTY}\nauthor f <f@x> 1000 +0000\ncommitter f <f@x> 1000 +0000\n\n"
               f"fleet {k}\n").encode()
    if obj_sha("commit", content).startswith(P):
        break
    k += 1
fleet_commit = run(FLEET_S, "hash-object", "-t", "commit", "-w", "--stdin", inp=content)
assert fleet_commit == obj_sha("commit", content), "crafted commit sha mismatch"

cases = [
    ("P ambiguous in lane only", [LANE_S], P, "^{commit}"),
    ("P ambiguous in lane, unique in fleet", [LANE_S, FLEET_S], P, "^{commit}"),
    ("X: commit + blob share prefix", [LANE_S], X, "^{commit}"),
    ("Q: two blobs, no commit", [LANE_S], Q, "^{commit}"),
    ("missing prefix", [LANE_S], "0000" if "0000" not in used else "ffff", "^{commit}"),
    ("full blob sha, commit peel", [LANE_S], blob_full, "^{commit}"),
    ("full commit sha, commit peel", [LANE_S], commit_full, "^{commit}"),
]
rows = []
for name, repos, tok, peel in cases:
    tool = rla.lookup(repos, [tok], peel)[tok]
    mine = pertoken(repos, tok)
    rows.append({"case": name, "token": tok, "repos": [os.path.basename(r) for r in repos],
                 "tool_batch_check": tool, "per_token_commit_only": mine,
                 "equal": tool == mine})
# FULL-hash path in the tool uses peel "" (any object type); compare with existence.
for name, tok in (("full blob sha, FULL path (no peel)", blob_full),
                  ("full commit sha, FULL path (no peel)", commit_full)):
    tool = rla.lookup([LANE_S, FLEET_S], [tok], "")[tok]
    mine = "found" if exists_any([LANE_S, FLEET_S], tok) else "missing"
    rows.append({"case": name, "token": tok, "repos": ["lane", "fleet"],
                 "tool_batch_check": tool, "per_token_commit_only": mine,
                 "equal": tool == mine})
print(json.dumps({"lane_ambiguous_prefix": P, "X_commit_plus_blob_prefix": X,
                  "Q_two_blobs_prefix": Q, "fleet_commit": fleet_commit,
                  "lane_commit_count": len(lane_commits), "rows": rows}, indent=1))
