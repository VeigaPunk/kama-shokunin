#!/usr/bin/env python3
"""Probe 4: (a) does `--filter=blob:none` still report a missing TREE (so a
non-blob missing set N is computable)?  (b) does `rev-list --objects
--missing=print` attempt any fetch in a promisor store whose remote is a dead
path (marker-file witness)?  (c) what does `cat-file --batch-all-objects
--batch-check` report for a store with missing objects?

Offline: local synthetic fixtures only; the 'remote' is a nonexistent path.
"""
import json, os, shutil, subprocess, tempfile
from pathlib import Path

BASE = "/fast/scratch/hyaku/kama-r24"

def env(**extra):
    e = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    e.update(GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_NOSYSTEM="1",
             GIT_PROTOCOL_ALLOW="never",
             GIT_AUTHOR_NAME="k", GIT_AUTHOR_EMAIL="k@example.invalid",
             GIT_COMMITTER_NAME="k", GIT_COMMITTER_EMAIL="k@example.invalid",
             GIT_AUTHOR_DATE="@1000 +0000", GIT_COMMITTER_DATE="@1000 +0000", **extra)
    return e

def g(repo, *args, check=True):
    pr = subprocess.run(["git", "-C", str(repo), *args], capture_output=True,
                        env=env(), timeout=60)
    if check and pr.returncode != 0:
        raise RuntimeError(f"{args} rc={pr.returncode} {pr.stderr.decode()[:300]}")
    return pr

def commit(repo, msg, path, body):
    Path(repo, path).write_text(body)
    g(repo, "add", path)
    g(repo, "-c", "commit.gpgsign=false", "commit", "-q", "-m", msg)
    return g(repo, "rev-parse", "HEAD").stdout.decode().strip()

def missing(repo, extra=(), isolation=("--no-lazy-fetch",)):
    pr = subprocess.run(["git", *isolation, "-C", str(repo), "rev-list",
                         "--objects", "--missing=print", "--no-object-names",
                         *extra, "--all"], capture_output=True, env=env(), timeout=60)
    out = pr.stdout.decode()
    return pr.returncode, {l.strip()[1:] for l in out.splitlines() if l.startswith("?")}

def loose(repo, oid):
    return Path(repo, ".git/objects", oid[:2], oid[2:])

res = {}
tmp = Path(tempfile.mkdtemp(prefix="probe4-", dir=BASE))
repo = tmp / "r"; repo.mkdir()
g(repo, "init", "-q", "-b", "master")
c1 = commit(repo, "round-1: a", "a.txt", "alpha\n")
c2 = commit(repo, "round-2: b", "b.txt", "beta\n")
tree2 = g(repo, "rev-parse", "HEAD^{tree}").stdout.decode().strip()

A = tmp / "A"; shutil.copytree(repo, A)
loose(A, tree2).unlink()
rc, Mall = missing(A)
rc2, Nall = missing(A, extra=("--filter=blob:none",))
res["missing_tree"] = {
    "M_all": sorted(Mall),
    "N_filter_blob_none": sorted(Nall),
    "tree_in_M": tree2 in Mall,
    "tree_in_N": tree2 in Nall,
    "M_equals_N": Mall == Nall,
    "rc": rc,
}

# (b) promisor store with dead remote: does rev-list --missing=print fetch?
C = tmp / "C"; shutil.copytree(repo, C)
g(C, "config", "core.repositoryformatversion", "1")
g(C, "config", "extensions.partialclone", "origin")
g(C, "config", "remote.origin.url", str(tmp / "absent.git"))
g(C, "config", "remote.origin.promisor", "true")
g(C, "config", "remote.origin.uploadpack", "touch " + str(tmp / "FETCHED"))
b2 = g(C, "rev-parse", "HEAD:b.txt").stdout.decode().strip()
loose(C, b2).unlink()                     # remove a blob -> store is incomplete
marker = tmp / "FETCHED"
rc, M = missing(C)
res["promisor_no_fetch"] = {
    "M": sorted(M),
    "missing_blob_in_M": b2 in M,
    "fetch_marker_exists": marker.exists(),
    "rc": rc,
}
# same call WITHOUT --no-lazy-fetch (for contrast only; remote path is dead)
rc, M2 = missing(C, isolation=())
res["promisor_without_no_lazy_fetch"] = {
    "M": sorted(M2),
    "fetch_marker_exists": marker.exists(),
    "stderr": g(C, "rev-list", "--objects", "--missing=print", "--all",
                check=False).stderr.decode()[:200],
}

# (c) batch-all-objects on an incomplete store
pr = subprocess.run(["git", "--no-lazy-fetch", "-C", str(C), "cat-file",
                     "--batch-all-objects", "--batch-check=%(objecttype) %(objectname)"],
                    capture_output=True, env=env(), timeout=60)
res["batch_all_objects"] = {
    "stdout": pr.stdout.decode().strip().splitlines(),
    "rc": pr.returncode,
}
Path("probe4-result.json").write_text(json.dumps(res, indent=2))
print(json.dumps(res, indent=2))
print("tmp:", tmp)
