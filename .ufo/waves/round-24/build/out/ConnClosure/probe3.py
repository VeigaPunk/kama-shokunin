#!/usr/bin/env python3
"""Probe 3: is the `rev-list --objects --missing=print` missing-set M CLOSED
under a missing commit?  i.e. are objects that live only inside a missing
commit's tree also reported as missing?

If not, then "token not in M" does NOT mean "proven absent": a blob that
exists only under a missing commit is absent locally and also absent from M,
so a per-token rule keyed on M membership would report a *guessed absence*
(exit 1) where the truth is "unknown" (exit 2).

Offline: local synthetic fixtures only.
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

def commit(repo, msg, path, body):
    Path(repo, path).write_text(body)
    g(repo, "add", path)
    g(repo, "-c", "commit.gpgsign=false", "commit", "-q", "-m", msg)
    return g(repo, "rev-parse", "HEAD").stdout.decode().strip()

def missing(repo, extra=()):
    pr = subprocess.run(["git", "--no-lazy-fetch", "-C", str(repo), "rev-list",
                         "--objects", "--missing=print", "--no-object-names",
                         *extra, "--all"], capture_output=True, env=env(), timeout=60)
    out = pr.stdout.decode()
    miss = {l.strip()[1:] for l in out.splitlines() if l.startswith("?")}
    return pr.returncode, miss

def loose(repo, oid):
    return Path(repo, ".git/objects", oid[:2], oid[2:])

res = {}
tmp = Path(tempfile.mkdtemp(prefix="probe3-", dir=BASE))
repo = tmp / "r"; repo.mkdir()
g(repo, "init", "-q", "-b", "master")
c1 = commit(repo, "round-1: only-a", "a.txt", "alpha\n")
b1 = g(repo, "rev-parse", "HEAD:a.txt").stdout.decode().strip()
c2 = commit(repo, "round-2: only-b", "b.txt", "beta\n")
b2 = g(repo, "rev-parse", "HEAD:b.txt").stdout.decode().strip()

# store where the missing commit is an ANCESTOR (reachable from HEAD)
A = tmp / "A"; shutil.copytree(repo, A)
loose(A, c1).unlink()          # delete the ancestor commit c1
rc, M = missing(A)
res["ancestor_missing_commit"] = {
    "c1_in_M": c1 in M,
    "b1_in_M": b1 in M,      # blob reachable ONLY through c1
    "b2_in_M": b2 in M,
    "M": sorted(M),
    "rev_list_rc": rc,
}
# is b1 still in the store?
pr = subprocess.run(["git", "--no-lazy-fetch", "-C", str(A), "cat-file", "-e", b1],
                     capture_output=True, env=env())
res["ancestor_missing_commit"]["b1_locally_present"] = (pr.returncode == 0)

# store where the missing commit is the TIP (unreachable from any other ref)
B = tmp / "B"; shutil.copytree(repo, B)
loose(B, c2).unlink()
rc, M = missing(B)
res["tip_missing_commit"] = {
    "c2_in_M": c2 in M,
    "b2_in_M": b2 in M,
    "M": sorted(M),
    "rev_list_rc": rc,
    "stderr": g(B, "rev-list", "--objects", "--missing=print", "--no-object-names",
                "--all", check=False).stderr.decode()[:200],
}

# promisor-marked variant of A
C = tmp / "C"; shutil.copytree(repo, C)
g(C, "config", "core.repositoryformatversion", "1")
g(C, "config", "extensions.partialclone", "origin")
g(C, "config", "remote.origin.url", str(tmp / "absent.git"))
g(C, "config", "remote.origin.promisor", "true")
loose(C, c1).unlink()
rc, M = missing(C)
res["promisor_ancestor_missing"] = {
    "c1_in_M": c1 in M,
    "b1_in_M": b1 in M,
    "M": sorted(M),
    "rev_list_rc": rc,
}

Path("probe3-result.json").write_text(json.dumps(res, indent=2))
print(json.dumps(res, indent=2))
print("tmp:", tmp)
