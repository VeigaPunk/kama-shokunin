#!/usr/bin/env python3
"""OracleLocalBlobType measurement 2: is the presence check transport-safe?

Three questions, answered offline (local path origin, GIT_ALLOW_PROTOCOL=file):

 1. A MISSING object in a promisor-marked repo, read with
    `git --no-lazy-fetch cat-file --batch-check`  -> "missing", no fetch.
 2. The same read WITHOUT --no-lazy-fetch         -> git attempts a fetch
    (FETCH_HEAD appears): the flag is load-bearing, GIT_ISOLATION must keep
    it.
 3. A PRESENT blob in a promisor-marked repo      -> "<sha> blob <size>" in
    both cases, no transport: a locally present object is a valid existence
    token regardless of promisor state.
"""
from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path

ROOT = Path("/fast/scratch/hyaku/kama-r24/OracleLocalBlobType")
MISSING = "deadbeefdeadbeefdeadbeefdeadbeefdeadbeef"


def env(**extra):
    e = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    e.update(GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_NOSYSTEM="1",
             GIT_ALLOW_PROTOCOL="file")
    e.update(extra)
    return e


def git(repo, *args, data=None):
    return subprocess.run(["git", "-C", str(repo), *args], input=data,
                          capture_output=True, env=env())


def main():
    work = ROOT / "transport"
    if work.exists():
        subprocess.run(["rm", "-rf", str(work)])
    work.mkdir(parents=True)
    origin = work / "origin.git"
    lane = work / "lane"
    subprocess.run(["git", "init", "-q", "--bare", str(origin)], env=env(),
                   check=True)
    subprocess.run(["git", "init", "-q", "-b", "master", str(lane)], env=env(),
                   check=True)
    blob = b"local blob body\n"
    (lane / "corpus").mkdir()
    (lane / "corpus/blob.txt").write_bytes(blob)
    subprocess.run(["git", "-C", str(lane), "add", "--", "corpus/blob.txt"],
                   env=env(), check=True)
    subprocess.run(["git", "-C", str(lane), "-c", "commit.gpgsign=false",
                    "commit", "-q", "-m", "round-1: work"],
                   env=env(GIT_AUTHOR_NAME="kama-shokunin",
                           GIT_AUTHOR_EMAIL="a@x",
                           GIT_COMMITTER_EMAIL="a@x",
                           GIT_COMMITTER_NAME="kama-shokunin",
                           GIT_AUTHOR_DATE="@1000 +0000",
                           GIT_COMMITTER_DATE="@1000 +0000"), check=True)
    blob_sha = subprocess.run(["git", "-C", str(lane), "rev-parse",
                               "HEAD:corpus/blob.txt"],
                              capture_output=True, env=env(),
                              check=True).stdout.decode().strip()
    for k, v in (("remote.origin.url", str(origin)),
                 ("remote.origin.promisor", "true"),
                 ("remote.origin.partialclonefilter", "blob:none"),
                 ("extensions.partialclone", "origin")):
        subprocess.run(["git", "-C", str(lane), "config", k, v], env=env(),
                       check=True)

    fetch_head = Path(lane, ".git/FETCH_HEAD")
    doc = {"blob": blob_sha, "missing": MISSING}

    def read(args, token):
        fetch_head.unlink(missing_ok=True)
        p = subprocess.run(["git", "-C", str(lane), *args, "cat-file",
                            "--batch-check"], input=(token + "\n").encode(),
                           capture_output=True, env=env())
        return {"out": p.stdout.decode().strip(),
                "err": p.stderr.decode(errors="replace").strip()[:200],
                "fetch_head_written": fetch_head.exists()}

    doc["1_missing_with_no_lazy_fetch"] = read(
        ("--no-lazy-fetch",), MISSING)
    doc["2_missing_without_no_lazy_fetch"] = read((), MISSING)
    doc["3_present_blob_with_no_lazy_fetch"] = read(
        ("--no-lazy-fetch",), blob_sha)
    doc["4_present_blob_without_no_lazy_fetch"] = read((), blob_sha)
    (ROOT / "transport-measurements.json").write_text(
        json.dumps(doc, indent=1, sort_keys=True))
    print(json.dumps(doc, indent=1, sort_keys=True))


if __name__ == "__main__":
    main()
