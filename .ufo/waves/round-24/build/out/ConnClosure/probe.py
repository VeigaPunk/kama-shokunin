#!/usr/bin/env python3
"""Bounded offline probe: per-token absence provability in a promisor-backed store.

No network: every 'remote' URL is a nonexistent local path; protocol.file.allow=never
blocks any transport attempt. Only local synthetic fixtures.
"""
import hashlib, json, os, subprocess, sys, tempfile
from pathlib import Path

def env(**extra):
    e = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    e.update(GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_NOSYSTEM="1",
             GIT_PROTOCOL_ALLOW="never",
             GIT_AUTHOR_NAME="kama-shokunin", GIT_AUTHOR_EMAIL="kama@example.invalid",
             GIT_COMMITTER_NAME="kama-shokunin", GIT_COMMITTER_EMAIL="kama@example.invalid",
             GIT_AUTHOR_DATE="@1000 +0000", GIT_COMMITTER_DATE="@1000 +0000", **extra)
    return e

def g(repo, *args, check=True):
    p = subprocess.run(["git", "-C", str(repo), *args], capture_output=True,
                       env=env(), timeout=60)
    if check and p.returncode != 0:
        raise RuntimeError(f"{args} rc={p.returncode} {p.stderr.decode()[:200]}")
    return p.returncode, p.stdout.decode(), p.stderr.decode()

def commit(repo, msg, path="f"):
    Path(repo, path).write_text(msg + "\n")
    g(repo, "add", path)
    g(repo, "-c", "commit.gpgsign=false", "commit", "-q", "-m", msg)
    return g(repo, "rev-parse", "HEAD")[1].strip()

def blob_id(repo, rev):
    return g(repo, "rev-parse", f"{rev}:f")[1].strip()

def make_origin(tmp):
    origin = Path(tmp, "origin")
    origin.mkdir()
    g(origin, "init", "-q", "-b", "master")
    g(origin, "config", "uploadpack.allowFilter", "true")
    c1 = commit(origin, "round-1: work")
    b1 = blob_id(origin, c1)
    c2 = commit(origin, "round-2: more")
    return origin, c1, b1, c2

def clone_blobless(tmp, origin, name):
    dest = Path(tmp, name)
    pr = subprocess.run(
        ["git", "-c", "protocol.file.allow=always", "-c", "uploadpack.allowFilter=true",
         "clone", "-q", "--no-checkout", "--filter=blob:none", "--no-local",
         f"file://{origin}", str(dest)], capture_output=True, env=env(), timeout=60)
    return dest, pr.returncode, pr.stderr.decode()[:300]

def missing_set(repo, extra=()):
    pr = subprocess.run(
        ["git", "--no-lazy-fetch", "-C", str(repo), "rev-list", "--objects",
         "--missing=print", "--no-object-names", *extra, "--all"],
        capture_output=True, env=env(), timeout=60)
    out = pr.stdout.decode()
    miss = {l.strip() for l in out.splitlines() if l.startswith("?")}
    return pr.returncode, miss, pr.stderr.decode()[:200]

def present_set(repo):
    pr = subprocess.run(
        ["git", "--no-lazy-fetch", "-C", str(repo), "cat-file",
         "--batch-all-objects", "--batch-check=%(objecttype) %(objectname)"],
        capture_output=True, env=env(), timeout=60)
    out = pr.stdout.decode()
    d = {}
    for line in out.splitlines():
        t, n = line.split()
        d[n] = t
    return pr.returncode, d

def main():
    tmp = tempfile.mkdtemp(prefix="connclosure-probe-", dir="/fast/scratch/hyaku/kama-r24")
    origin, c1, b1, c2 = make_origin(tmp)
    # make the promisor-capable remote a dead path: promisor-marked but complete content
    clone, rc, err = clone_blobless(tmp, origin, "blobless")
    print("clone rc", rc, err)
    rc, P = present_set(clone)
    rc2, M, _ = missing_set(clone)
    rc3, N, _ = missing_set(clone, extra=("--filter=blob:none",))
    print("blobless: present", len(P), "M(missing all)", sorted(M)[:5], "N(missing non-blob)", sorted(N)[:5])
    print("  b1 in M?", b1 in M, " b1 present?", b1 in P)
    fake = "a" * 40
    print("  fake in M?", fake in M, " fake in P?", fake in P)
    # also: is the blob really absent locally?
    print("  cat-file -e b1 rc:", subprocess.run(
        ["git", "--no-lazy-fetch", "-C", str(clone), "cat-file", "-e", b1],
        capture_output=True, env=env()).returncode)
    # completeness variant: hydrate the blob by checking out (T01 shape)
    full = Path(tmp, "full")
    subprocess.run(["git", "-c", "protocol.file.allow=always", "clone", "-q",
                    "--no-local", f"file://{origin}", str(full)], capture_output=True,
                   env=env(), timeout=60)
    # now simulate a promisor-marked but content-complete store: add marker + config to full
    g(full, "config", "core.repositoryformatversion", "1")
    g(full, "config", "extensions.partialclone", "origin")
    g(full, "config", "remote.origin.url", str(Path(tmp, "absent.git")))
    g(full, "config", "remote.origin.promisor", "true")
    rc, P2 = present_set(full)
    rc2, M2, _ = missing_set(full)
    rc3, N2, _ = missing_set(full, extra=("--filter=blob:none",))
    print("marked-complete: present", len(P2), "M", sorted(M2), "N", sorted(N2),
          "b1 present?", b1 in P2)
    out = {"tmp": tmp, "blobless": {"M": sorted(M), "N": sorted(N)},
           "marked_complete": {"M": sorted(M2), "N": sorted(N2)},
           "b1": b1, "c1": c1, "fake": fake}
    Path("probe-result.json").write_text(json.dumps(out, indent=2))
    print("tmp", tmp)

main()
