#!/usr/bin/env python3
"""Probe 2: does `rev-list --objects --missing=print --all` surface MISSING COMMITS
and MISSING TREES, or only missing blobs?  Offline, local synthetic fixtures only.

If a missing commit is not surfaced, then "token not in M" cannot mean
"proved absent" -- the absence would be a guess, and a cited-but-missing
commit would be misclassified as exit 1 instead of exit 2.
"""
import json, os, shutil, subprocess, tempfile
from pathlib import Path

BASE = "/fast/scratch/hyaku/kama-r24"

def env(**extra):
    e = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    e.update(GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_NOSYSTEM="1",
             GIT_PROTOCOL_ALLOW="never",
             GIT_AUTHOR_NAME="kama-shokunin", GIT_AUTHOR_EMAIL="k@example.invalid",
             GIT_COMMITTER_NAME="kama-shokunin", GIT_COMMITTER_EMAIL="k@example.invalid",
             GIT_AUTHOR_DATE="@1000 +0000", GIT_COMMITTER_DATE="@1000 +0000", **extra)
    return e

def g(repo, *args, check=True):
    pr = subprocess.run(["git", "-C", str(repo), *args], capture_output=True,
                        env=env(), timeout=60)
    if check and pr.returncode != 0:
        raise RuntimeError(f"{args} rc={pr.returncode} {pr.stderr.decode()[:300]}")
    return pr

def commit(repo, msg, path="f"):
    Path(repo, path).write_text(msg + "\n")
    g(repo, "add", path)
    g(repo, "-c", "commit.gpgsign=false", "commit", "-q", "-m", msg)
    return g(repo, "rev-parse", "HEAD").stdout.decode().strip()

def objects(repo):
    """all objects present in the store, as (type, name)"""
    pr = subprocess.run(["git", "--no-lazy-fetch", "-C", str(repo), "cat-file",
                         "--batch-all-objects", "--batch-check=%(objecttype) %(objectname)"],
                        capture_output=True, env=env(), timeout=60)
    d = {}
    for line in pr.stdout.decode().splitlines():
        t, n = line.split()
        d[n] = t
    return d

def missing(repo, extra=()):
    pr = subprocess.run(["git", "--no-lazy-fetch", "-C", str(repo), "rev-list",
                         "--objects", "--missing=print", "--no-object-names",
                         *extra, "--all"], capture_output=True, env=env(), timeout=60)
    out = pr.stdout.decode()
    miss = {l.strip()[1:] for l in out.splitlines() if l.startswith("?")}
    return pr.returncode, miss, pr.stderr.decode()[:300], out

def loose_path(repo, oid):
    return Path(repo, ".git/objects", oid[:2], oid[2:])

results = {}

tmp = Path(tempfile.mkdtemp(prefix="probe2-", dir=BASE))
repo = tmp / "r"; repo.mkdir()
g(repo, "init", "-q", "-b", "master")
c1 = commit(repo, "round-1: one")
c2 = commit(repo, "round-2: two")
c3 = commit(repo, "round-3: three")
head = g(repo, "rev-parse", "HEAD").stdout.decode().strip()
results["head"] = head

# --- case A: delete a loose COMMIT object (c1, an ancestor) ---
shutil.copytree(repo, tmp / "A")
A = tmp / "A"
target = loose_path(A, c1)
had_loose = target.exists()
if had_loose:
    target.unlink()
rc, M, err, _ = missing(A)
present = objects(A)
results["A_missing_commit"] = {
    "commit_was_loose": had_loose,
    "c1_present_after": c1 in present,
    "rev_list_rc": rc,
    "M_contains_c1": c1 in M,
    "M_size": len(M),
    "stderr": err.strip()[:200],
}

# --- case B: delete a loose TREE object of the tip commit ---
shutil.copytree(repo, tmp / "B")
B = tmp / "B"
tree = g(B, "rev-parse", "HEAD^{tree}").stdout.decode().strip()
tpath = loose_path(B, tree)
had_tree = tpath.exists()
if had_tree:
    tpath.unlink()
rc, M, err, _ = missing(B)
present = objects(B)
results["B_missing_tree"] = {
    "tree_was_loose": had_tree,
    "tree_present_after": tree in present,
    "rev_list_rc": rc,
    "M_contains_tree": tree in M,
    "M_size": len(M),
    "stderr": err.strip()[:200],
}

# --- case C: what does a *cited* missing commit look like to git? ---
pr = subprocess.run(["git", "--no-lazy-fetch", "-C", str(B), "cat-file",
                      "--batch-check"], input=(c1 + "\n").encode(),
                     capture_output=True, env=env(), timeout=60)
results["C_batch_check_missing_commit"] = {
    "stdout": pr.stdout.decode().strip(),
    "stderr": pr.stderr.decode().strip()[:200],
    "rc": pr.returncode,
}
# and a bare-vs-peel lookup on a present blob
blob = g(repo, "rev-parse", "HEAD:f").stdout.decode().strip()
pr = subprocess.run(["git", "--no-lazy-fetch", "-C", str(B), "cat-file",
                      "--batch-check"], input=(f"{blob}\n{blob}^{{commit}}\n").encode(),
                     capture_output=True, env=env(), timeout=60)
results["C_bare_vs_peel_blob"] = {
    "stdout": pr.stdout.decode().strip(),
    "stderr": pr.stderr.decode().strip()[:300],
}

# --- case D: does rev-list --missing=print report missing commits when the
#     store is promisor-marked (i.e. is the "?" line emitted for commits)? ---
D = tmp / "D"; shutil.copytree(repo, D)
g(D, "config", "core.repositoryformatversion", "1")
g(D, "config", "extensions.partialclone", "origin")
g(D, "config", "remote.origin.url", str(tmp / "absent.git"))
g(D, "config", "remote.origin.promisor", "true")
loose_path(D, c1).unlink()
rc, M, err, _ = missing(D)
results["D_promisor_missing_commit"] = {
    "rev_list_rc": rc,
    "M_contains_c1": c1 in M,
    "M_size": len(M),
    "stderr": err.strip()[:200],
}

Path("probe2-result.json").write_text(json.dumps(results, indent=2))
print(json.dumps(results, indent=2))
print("tmp:", tmp)
