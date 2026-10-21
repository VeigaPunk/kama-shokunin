#!/usr/bin/env python3
"""Probe 3: real blobless partial clone; pack rebuilt without the required
ancestor L1, so the repo keeps its .promisor pack but L1 is unavailable."""
import os
import subprocess
from pathlib import Path

ROOT = Path("/fast/scratch/hyaku/kama-r24/CaseMissingAncestor/proto/probe3-run")


def env(**extra):
    e = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    e.update(GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_NOSYSTEM="1",
             GIT_AUTHOR_EMAIL="a@x", GIT_COMMITTER_EMAIL="a@x")
    e.update(extra)
    return e


def g(repo, *args, check=True, data=None, **extra):
    p = subprocess.run(["git", "-C", str(repo), *args], input=data,
                       capture_output=True, env=env(**extra))
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


def build():
    root = ROOT
    if root.exists():
        subprocess.run(["rm", "-rf", str(root)])
    root.mkdir(parents=True)
    src = root / "src"
    g(root, "init", "-q", "-b", "master", str(src))
    l0 = commit(src, "kama-shokunin", 900, "round-1: base")
    l1 = commit(src, "kama-shokunin", 1000, "round-1: work")
    l2 = commit(src, "kama-shokunin", 1100, "round-1: measure")
    l3 = commit(src, "kama-shokunin", 2100, "round-1: late")
    origin = root / "origin.git"
    g(root, "clone", "-q", "--bare", "--no-hardlinks", str(src), str(origin))
    clone = root / "lane"
    g(root, "-c", "protocol.file.allow=always", "clone", "-q", "--no-checkout",
      "--filter=blob:none", "--no-local", f"file://{origin}", str(clone))
    return root, clone, origin, (l0, l1, l2, l3)


root, clone, origin, (l0, l1, l2, l3) = build()
print("clone config:", g(clone, "config", "--local", "--list"))
print("packs:", sorted(p.name for p in Path(clone, ".git/objects/pack").iterdir()))
print("L0", l0, "L1", l1, "L2", l2, "L3", l3)
print("blob of L1 present?", g(clone, "cat-file", "-t", g(clone, "rev-parse",
                                                        f"{l0}:f")))
# rebuild the pack without L1 and its ancestors, keeping L0 explicitly
revs = f"{l0}\n{l2}\n{l3}\n^{l1}\n".encode()
pack = subprocess.run(["git", "-C", str(clone), "pack-objects", "--revs",
                       "--stdout"], input=revs, capture_output=True, env=env())
print("pack-objects rc", pack.returncode, pack.stderr.decode()[:200])
packfile = root / "new.pack"
packfile.write_bytes(pack.stdout)
old = sorted(Path(clone, ".git/objects/pack").iterdir())
for p in old:
    p.unlink()
idx = subprocess.run(["git", "-C", str(clone), "index-pack", "--stdin"],
                     input=pack.stdout, capture_output=True, env=env())
print("index-pack rc", idx.returncode, idx.stdout.decode().strip(),
      idx.stderr.decode()[:200])
newpacks = sorted(Path(clone, ".git/objects/pack").iterdir())
print("new packs:", [p.name for p in newpacks])
name = [p.name for p in newpacks if p.name.endswith(".pack")][0][:-5]
Path(clone, ".git/objects/pack", name + ".promisor").write_bytes(b"")
print("packs now:", sorted(p.name for p in Path(clone, ".git/objects/pack").iterdir()))


def run(label, argv):
    p = subprocess.run(["git", "-C", str(clone), *argv], capture_output=True,
                       env=env())
    print(f"--- {label}: rc={p.returncode}")
    print("    stdout:", p.stdout.decode(errors="replace").strip()[:400])
    print("    stderr:", p.stderr.decode(errors="replace").strip()[:400])


run("cat-file -e L1 (--no-lazy-fetch)",
    ["--no-lazy-fetch", "cat-file", "-e", l1])
run("log (--no-lazy-fetch)", ["--no-lazy-fetch", "log", "--format=%H %s",
                               "master"])
run("rev-list --missing=print (--no-lazy-fetch)",
    ["--no-lazy-fetch", "rev-list", "--missing=print", "master"])
run("ls-tree (--no-lazy-fetch)", ["--no-lazy-fetch", "ls-tree", "master"])
run("cat-file -t blob of L0 (--no-lazy-fetch)",
    ["--no-lazy-fetch", "cat-file", "-t",
     g(clone, "rev-parse", f"{l0}:f")])
print("L1 present (no-lazy-fetch):", subprocess.run(
    ["git", "--no-lazy-fetch", "-C", str(clone), "cat-file", "-e", l1],
    capture_output=True, env=env()).returncode == 0)
print("L1 present (lazy allowed):", subprocess.run(
    ["git", "-C", str(clone), "cat-file", "-e", l1],
    capture_output=True, env=env()).returncode == 0)
print("packs after probes:", sorted(p.name for p in Path(clone, ".git/objects/pack").iterdir()))
print("loose objects:", sorted(p.name for p in Path(clone, ".git/objects").iterdir()))
