#!/usr/bin/env python3
"""ConnClosure probes 5-7: closure of the missing-object set M.

Probe 5: does `--missing=print` separate a missing commit from a missing blob?
Probe 6: is M closed when a commit AND its blob are deleted?  (first attempt:
         the blob was still reachable from HEAD's tree, so the test was
         invalid -- superseded by probe 7.)
Probe 7: the corrected closure test.  The blob is created by commit c1 and
         removed by c2, so it is reachable ONLY through c1.  Delete c1 and the
         blob.  Is the blob in M?

Result (git 2.56.0, local synthetic fixtures only, no network):
  M is NOT transitively closed.  The missing commit c1 appears in M
  (`?c1`), but the blob that exists only under it does NOT.  A rule of the
  form "token not in M => proved absent" therefore guesses absence where the
  truth is unknown.  The landed candidate avoids this by refusing whenever a
  missing tree or commit exists at all (the "opaque hole"), independently of
  token membership.

Offline: every "remote" is a nonexistent local path; GIT_PROTOCOL_ALLOW=never.
"""
import json
import os
import shutil
import subprocess
import tempfile
from pathlib import Path

BASE = "/fast/scratch/hyaku/kama-r24"


def env(**extra):
    d = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    d.update(GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_NOSYSTEM="1",
             GIT_PROTOCOL_ALLOW="never",
             GIT_AUTHOR_NAME="k", GIT_AUTHOR_EMAIL="k@x.invalid",
             GIT_COMMITTER_NAME="k", GIT_COMMITTER_EMAIL="k@x.invalid",
             GIT_AUTHOR_DATE="@1000 +0000", GIT_COMMITTER_DATE="@1000 +0000",
             **extra)
    return d


def g(repo, *args, check=True):
    p = subprocess.run(["git", "-C", str(repo), *args], capture_output=True,
                       env=env(), timeout=60)
    if check and p.returncode != 0:
        raise RuntimeError(f"{args} rc={p.returncode} {p.stderr.decode()[:300]}")
    return p


def commit(repo, msg, path, body):
    Path(repo, path).write_text(body)
    g(repo, "add", path)
    g(repo, "-c", "commit.gpgsign=false", "commit", "-q", "-m", msg)
    return g(repo, "rev-parse", "HEAD").stdout.decode().strip()


def loose(repo, oid):
    return Path(repo, ".git/objects", oid[:2], oid[2:])


def missing(repo, extra=()):
    p = subprocess.run(["git", "--no-lazy-fetch", "-C", str(repo), "rev-list",
                        "--objects", "--missing=print", "--no-object-names",
                        *extra, "--all"], capture_output=True, env=env(),
                       timeout=60)
    out = p.stdout.decode()
    return {l.strip()[1:] for l in out.splitlines() if l.startswith("?")}


def main():
    res = {}
    tmp = Path(tempfile.mkdtemp(prefix="cc-probe5-", dir=BASE))
    repo = tmp / "r"
    repo.mkdir()
    g(repo, "init", "-q", "-b", "master")
    c1 = commit(repo, "round-1: only-a", "a.txt", "alpha\n")
    b1 = g(repo, "rev-parse", "HEAD:a.txt").stdout.decode().strip()
    c2 = commit(repo, "round-2: only-b", "b.txt", "beta\n")
    b2 = g(repo, "rev-parse", "HEAD:b.txt").stdout.decode().strip()

    A = tmp / "A"
    shutil.copytree(repo, A)
    loose(A, c1).unlink()
    res["probe5_missing_commit"] = {"M": sorted(missing(A)),
                                    "N_filter_blob_none": sorted(
                                        missing(A, ("--filter=blob:none",)))}

    B = tmp / "B"
    shutil.copytree(repo, B)
    loose(B, b2).unlink()
    res["probe5_missing_blob_only"] = {"M": sorted(missing(B)),
                                       "N_filter_blob_none": sorted(
                                           missing(B, ("--filter=blob:none",)))}

    # probe 7: the corrected closure test
    D = tmp / "D"
    D.mkdir()
    g(D, "init", "-q", "-b", "master")
    d1 = commit(D, "round-1: unique", "unique.txt", "unique-payload\n")
    ub = g(D, "rev-parse", "HEAD:unique.txt").stdout.decode().strip()
    g(D, "rm", "-q", "unique.txt")
    g(D, "-c", "commit.gpgsign=false", "commit", "-q", "-m", "round-1: drop unique")
    pr = subprocess.run(["git", "--no-lazy-fetch", "-C", str(D), "rev-list",
                         "--objects", "--all"], capture_output=True, env=env(),
                        timeout=60)
    reachable = ub in pr.stdout.decode()
    loose(D, d1).unlink()
    loose(D, ub).unlink()
    M = missing(D)
    res["probe7_closure"] = {
        "blob_reachable_before_deletion": reachable,
        "blob_present_locally_after_deletion": loose(D, ub).exists(),
        "blob_in_M": ub in M,
        "missing_commit_in_M": d1 in M,
        "M": sorted(M),
        "M_is_closed": bool(M) and ub in M,
    }
    out = Path(__file__).resolve().parent / "probe5_6_7_closure-result.json"
    out.write_text(json.dumps(res, indent=2))
    print(json.dumps(res, indent=2))


if __name__ == "__main__":
    main()
