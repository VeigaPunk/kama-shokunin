#!/usr/bin/env python3
"""Probe 2: fresh promisor-marked lane per probe, --no-lazy-fetch first."""
import os
import subprocess
from pathlib import Path

ROOT = Path("/fast/scratch/hyaku/kama-r24/CaseMissingAncestor/proto/probe2-run")


def env(**extra):
    e = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    e.update(GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_NOSYSTEM="1",
             GIT_AUTHOR_EMAIL="a@x", GIT_COMMITTER_EMAIL="a@x")
    e.update(extra)
    return e


def g(repo, *args, check=True, **extra):
    p = subprocess.run(["git", "-C", str(repo), *args], capture_output=True,
                       env=env(**extra))
    if check and p.returncode:
        raise SystemExit(f"git {args}: {p.stderr.decode()}")
    return p.stdout.decode(errors="replace").strip()


def commit(repo, author, when, msg, path="f"):
    target = Path(repo, path)
    with open(target, "a") as fh:
        fh.write(msg + "\n")
    g(repo, "add", "--", path)
    stamp = f"@{when} +0000"
    g(repo, "-c", "commit.gpgsign=false", "commit", "-q", "-m", msg,
      GIT_AUTHOR_NAME=author, GIT_COMMITTER_NAME=author,
      GIT_AUTHOR_DATE=stamp, GIT_COMMITTER_DATE=stamp)
    return g(repo, "rev-parse", "HEAD")


def build(name):
    """Fresh lane (promisor-marked, L1 removed) + local origin holding L1."""
    root = ROOT / name
    root.mkdir(parents=True)
    lane = root / "lane"
    g(root, "init", "-q", "-b", "master", str(lane))
    commit(lane, "kama-shokunin", 900, "round-1: base")
    l1 = commit(lane, "kama-shokunin", 1000, "round-1: work")
    commit(lane, "kama-shokunin", 1100, "round-1: measure")
    commit(lane, "kama-shokunin", 2100, "round-1: late")
    origin = root / "origin.git"
    g(root, "clone", "-q", "--bare", "--no-hardlinks", str(lane), str(origin))
    for k, v in (("remote.origin.url", str(origin)),
                 ("remote.origin.promisor", "true"),
                 ("remote.origin.partialclonefilter", "blob:none"),
                 ("extensions.partialClone", "origin"),
                 ("core.repositoryformatversion", "1")):
        g(lane, "config", k, v)
    Path(lane, ".git/objects", l1[:2], l1[2:]).unlink()
    return lane, origin, l1


def probe(label, argv, extra_args=("--no-lazy-fetch",)):
    lane, origin, l1 = build(label.replace(" ", "_"))
    argv = [a.replace("REV", l1) for a in argv]
    p = subprocess.run(["git", "-C", str(lane), *extra_args, *argv],
                       capture_output=True, env=env())
    present = subprocess.run(["git", "-C", str(lane), "cat-file", "-e", l1],
                             capture_output=True,
                             env=env()).returncode == 0
    print(f"--- {label} rc={p.returncode} l1_present_after={present}")
    print("    stdout:", p.stdout.decode(errors='replace').strip()[:500])
    print("    stderr:", p.stderr.decode(errors='replace').strip()[:500])


if ROOT.exists():
    subprocess.run(["rm", "-rf", str(ROOT)])

probe("log (--no-lazy-fetch)", ["log", "--format=%H %s", "master"])
probe("cat-file -e (--no-lazy-fetch)", ["cat-file", "-e", "REV"])
probe("rev-list --missing=print (--no-lazy-fetch)",
      ["rev-list", "--missing=print", "master"])
probe("rev-list --objects --missing=print (--no-lazy-fetch)",
      ["rev-list", "--objects", "--missing=print", "master"])
probe("fsck-connectivity (--no-lazy-fetch)", ["fsck", "--connectivity-only"])
probe("log (lazy fetch allowed)", ["log", "--format=%H %s", "master"],
      extra_args=())
probe("cat-file -e (lazy fetch allowed)", ["cat-file", "-e", "REV"],
      extra_args=())
