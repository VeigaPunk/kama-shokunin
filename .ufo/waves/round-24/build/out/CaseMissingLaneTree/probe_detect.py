#!/usr/bin/env python3
"""Detection primitives for an unavailable reachable tree (offline).

Which read-only git invocations report the missing tree of the case
fixture, and do any of them attempt a fetch? All calls carry
--no-lazy-fetch and --no-replace-objects, exactly as the auditor runs git.
"""
import os
import subprocess
import sys
from pathlib import Path

CASE = Path("/fast/scratch/hyaku/kama-r24/CaseMissingLaneTree/measure/"
            "case-promisor-missing-tree/lane")
GIT = ["git", "--no-lazy-fetch", "--no-replace-objects", "-C", str(CASE)]


def env():
    e = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    e.update(GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_NOSYSTEM="1")
    return e


def run(*args, data=None):
    p = subprocess.run([*GIT, *args], input=data, capture_output=True,
                       env=env())
    return p.returncode, p.stdout.decode(errors="replace"), \
        p.stderr.decode(errors="replace")


def main():
    rc, out, err = run("rev-parse", "HEAD^{tree}")
    print("tip tree rev-parse:", rc, out.strip(), "|", err.strip())
    tree = out.strip()
    rc, out, err = run("cat-file", "--batch-check", data=(tree + "\n").encode())
    print("cat-file --batch-check tree:", rc, out.strip(), "|", err.strip())
    rc, out, err = run("rev-list", "--objects", "--missing=print", "master")
    print("rev-list --objects --missing=print:", rc)
    for line in out.splitlines():
        if line.startswith("?") or line.strip() == tree:
            print("   ", line)
    print("   stderr:", err.strip())
    rc, out, err = run("fsck", "--connectivity-only", "--no-dangling")
    print("fsck --connectivity-only:", rc)
    for line in out.splitlines() + err.splitlines():
        if "missing" in line or "dangling" in line:
            print("   ", line)
    rc, out, err = run("cat-file", "--batch-all-objects", "--batch-check")
    print("cat-file --batch-all-objects --batch-check rc:", rc,
          "objects:", len(out.splitlines()))
    rc, out, err = run("log", "--format=%H", "master")
    print("git log master rc:", rc, "commits:", len(out.split()))
    # nothing may have been fetched
    loose = sorted(p.name for p in (CASE / ".git/objects").iterdir()
                   if p.is_dir() and len(p.name) == 2)
    packs = sorted(p.name for p in (CASE / ".git/objects/pack").glob("*"))
    print("loose object dirs:", len(loose), "packs:", packs)
    return 0


if __name__ == "__main__":
    sys.exit(main())
