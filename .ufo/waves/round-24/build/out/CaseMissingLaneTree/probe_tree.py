#!/usr/bin/env python3
"""Premise probe: what does git do when a reachable lane tree is missing?

Offline only. No network, no remote fetch, no program execution.
"""
import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path("/fast/scratch/hyaku/kama-r24/CaseMissingLaneTree/probe/work")


def env(**extra):
    e = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    e.update(GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_NOSYSTEM="1",
             GIT_AUTHOR_EMAIL="a@x", GIT_COMMITTER_EMAIL="a@x",
             GIT_AUTHOR_NAME="kama-shokunin",
             GIT_COMMITTER_NAME="kama-shokunin")
    e.update(extra)
    return e


def g(repo, *args, data=None, check=True, **extra):
    p = subprocess.run(["git", "-C", str(repo), *args], input=data,
                       capture_output=True, env=env(**extra))
    if check and p.returncode:
        raise SystemExit(f"git {args} failed: {p.stderr.decode()}")
    return p.stdout.decode(errors="surrogateescape").strip()


def commit(repo, when, msg, path="f"):
    target = Path(repo, path)
    target.parent.mkdir(parents=True, exist_ok=True)
    with open(target, "ab") as fh:
        fh.write((msg + "\n").encode())
    g(repo, "add", "--", path)
    stamp = f"@{when} +0000"
    g(repo, "-c", "commit.gpgsign=false", "commit", "-q", "-m", msg,
      GIT_AUTHOR_DATE=stamp, GIT_COMMITTER_DATE=stamp)
    return g(repo, "rev-parse", "HEAD")


def build(root):
    lane, fleet = root / "lane", root / "fleet"
    for repo in (lane, fleet):
        repo.mkdir(parents=True)
        g(repo.parent, "init", "-q", "-b", "master", str(repo))
    c1 = commit(lane, 1000, "round-1: work")
    c2 = commit(lane, 1500, "round-1: more")
    body = ("# kama round 1\n\n## Landed changes\n\n- `" + c1 + "` work\n")
    rep = fleet / ".ufo/reports/round-1/kama.md"
    rep.parent.mkdir(parents=True)
    rep.write_text(body, encoding="utf-8")
    g(fleet, "add", "--", ".ufo/reports/round-1/kama.md")
    g(fleet, "-c", "commit.gpgsign=false", "commit", "-q", "-m",
      "round-1: report", GIT_AUTHOR_DATE="@2000 +0000",
      GIT_COMMITTER_DATE="@2000 +0000")
    return lane, fleet, c1, c2


def loose_path(repo, oid):
    return Path(repo, ".git/objects", oid[:2], oid[2:])


def main():
    if ROOT.exists():
        shutil.rmtree(ROOT)
    ROOT.mkdir(parents=True)
    lane, fleet, c1, c2 = build(ROOT)
    tree1 = g(lane, "rev-parse", f"{c1}^{{tree}}")
    tree2 = g(lane, "rev-parse", f"{c2}^{{tree}}")
    print("c1", c1, "tree1", tree1, "loose?", loose_path(lane, tree1).exists())
    print("c2", c2, "tree2", tree2, "loose?", loose_path(lane, tree2).exists())

    # remove the tree of the *older* commit c1 (reachable, ancestor of tip)
    os.unlink(loose_path(lane, tree1))
    print("\n-- after removing c1 tree --")
    print("cat-file -e tree1 rc:",
          subprocess.run(["git", "-C", str(lane), "cat-file", "-e", tree1],
                         capture_output=True, env=env()).returncode)
    print("cat-file -e c1 rc:",
          subprocess.run(["git", "-C", str(lane), "cat-file", "-e", c1],
                         capture_output=True, env=env()).returncode)

    for label, args in [
            ("log --format", ["log", "--format=%H%x00%an%x00%at%x00%s", "master"]),
            ("log -z (tool form)", ["log", "-z", "--format=%H%x00%an%x00%at%x00%s", "master"]),
            ("ls-tree tip SOURCES", ["ls-tree", "master", "--", "corpus/SOURCES.md"]),
            ("rev-list --objects --missing=print",
             ["rev-list", "--objects", "--missing=print", "master"]),
            ("rev-list --objects --missing=allow-any",
             ["rev-list", "--objects", "--missing=allow-any", "master"]),
            ("cat-file --batch-check tree1", ["cat-file", "--batch-check"]),
    ]:
        data = tree1 + "\n" if "batch-check" in label else None
        p = subprocess.run(["git", "-C", str(lane), *args], input=data,
                           capture_output=True, env=env())
        print(f"\n[{label}] rc={p.returncode}")
        print("  out:", p.stdout.decode(errors="replace")[:800].replace("\n", " | "))
        print("  err:", p.stderr.decode(errors="replace")[:400].replace("\n", " | "))

    # with --no-lazy-fetch (as the auditor runs git)
    p = subprocess.run(["git", "--no-lazy-fetch", "--no-replace-objects", "-C",
                        str(lane), "log", "--format=%H", "master"],
                       capture_output=True, env=env())
    print("\n[log with --no-lazy-fetch] rc=", p.returncode,
          "err:", p.stderr.decode(errors="replace")[:300].replace("\n", " | "))

    # promisor metadata on top: does a missing object trigger a fetch?
    for k, v in (("extensions.partialClone", "origin"),
                 ("remote.origin.url", str(ROOT / "absent.git")),
                 ("remote.origin.promisor", "true")):
        g(lane, "config", k, v)
    p = subprocess.run(["git", "-C", str(lane), "cat-file", "-e", tree1],
                       capture_output=True, env=env())
    print("\n[promisor cat-file -e tree1, no --no-lazy-fetch] rc=",
          p.returncode, "err:", p.stderr.decode(errors="replace")[:300].replace("\n", " | "))
    p = subprocess.run(["git", "--no-lazy-fetch", "-C", str(lane), "cat-file",
                        "-e", tree1], capture_output=True, env=env())
    print("[promisor cat-file -e tree1, --no-lazy-fetch] rc=", p.returncode,
          "err:", p.stderr.decode(errors="replace")[:300].replace("\n", " | "))
    p = subprocess.run(["git", "--no-lazy-fetch", "-C", str(lane), "log",
                        "--format=%H", "master"], capture_output=True, env=env())
    print("[promisor log --no-lazy-fetch] rc=", p.returncode,
          "err:", p.stderr.decode(errors="replace")[:300].replace("\n", " | "))
    p = subprocess.run(["git", "--no-lazy-fetch", "-C", str(lane), "rev-list",
                        "--objects", "--missing=print", "master"],
                       capture_output=True, env=env())
    print("[promisor rev-list --missing=print --no-lazy-fetch] rc=",
          p.returncode)
    print(p.stdout.decode(errors="replace")[:600].replace("\n", " | "))
    print("  err:", p.stderr.decode(errors="replace")[:300].replace("\n", " | "))


if __name__ == "__main__":
    sys.exit(main())
