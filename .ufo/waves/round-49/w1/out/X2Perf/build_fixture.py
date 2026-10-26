#!/usr/bin/env python3
"""Build a synthetic append-only-audit fixture: N commits, each rewriting an exempt
`## Axes` head of H lines (fresh text per commit) plus a small dated `## Round 1` tail.

Identity is fixture-local (`aoa-x2perf`), commits are made with plumbing so the
worktree is written once. Usage: build_fixture.py <dir> <commits> <head_lines> <tail_lines>
"""
import os
import subprocess
import sys

IDENT = ["-c", "user.name=aoa-x2perf", "-c", "user.email=aoa-x2perf@invalid",
         "-c", "commit.gpgsign=false"]

NOTES = ["# n", "score.md is append-only; the ## Axes head is re-derived in place", "x"]
CONTRACT = ("path\trule\tdeclared_at\tregion\tnote\n"
            "score.md\tA-corr\tNOTES.md:2\texempt=## Axes@NOTES.md:2\tfixture\n")


def git(d, *args, inp=None):
    p = subprocess.run(["git", "-C", d, *IDENT, *args], input=inp, capture_output=True)
    if p.returncode != 0:
        raise SystemExit(f"git {' '.join(args)}: {p.stderr.decode()[:400]}")
    return p.stdout


def head_lines(commit, n):
    return [f"## Axes" if False else f"h{c:04d} c{commit:05d} blk" for c in range(n)]


def body(i, head_n, tail_n):
    out = ["# score", "## Axes"]
    out += [f"h{c:04d} c{i:05d} blk" for c in range(head_n)]
    out += ["## Round 1"]
    out += [f"d{c:04d} c{i:05d} row" for c in range(tail_n)]
    return out


def main():
    d, commits, head_n, tail_n = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4])
    stride = int(sys.argv[5]) if len(sys.argv) > 5 else 1
    os.makedirs(d, exist_ok=True)
    subprocess.run(["git", "-C", d, "init", "-q"], check=True)
    top = git(d, "rev-parse", "--show-toplevel").decode().strip()
    if os.path.realpath(top) != os.path.realpath(d):
        raise SystemExit(f"refusing: toplevel {top} != {d}")
    os.makedirs(os.path.join(d, "registry"), exist_ok=True)
    open(os.path.join(d, "NOTES.md"), "w").write("\n".join(NOTES) + "\n")
    open(os.path.join(d, "registry", "append-only-contract.tsv"), "w").write(CONTRACT)
    git(d, "add", "-A")
    git(d, "commit", "-q", "-m", "c0")
    prev = git(d, "rev-parse", "HEAD").decode().strip()
    idx = os.path.join(d, ".git", "index-x2perf")
    env = dict(os.environ, GIT_INDEX_FILE=idx)
    subprocess.run(["git", "-C", d, "read-tree", prev], env=env, check=True)
    tree_prev = git(d, "rev-parse", "HEAD^{tree}").decode().strip()
    for i in range(1, commits):
        if stride > 1 and i % stride:
            prev = subprocess.run(["git", "-C", d, *IDENT, "commit-tree", tree_prev, "-p", prev,
                                   "-m", f"noop {i}"], capture_output=True,
                                  check=True).stdout.decode().strip()
            continue
        data = ("\n".join(body(i, head_n, tail_n)) + "\n").encode()
        blob = subprocess.run(["git", "-C", d, "hash-object", "-w", "--stdin"], input=data,
                              capture_output=True, check=True).stdout.decode().strip()
        subprocess.run(["git", "-C", d, "update-index", "--add", "--cacheinfo",
                        f"100644,{blob},score.md"], env=env, check=True)
        tree = subprocess.run(["git", "-C", d, "write-tree"], env=env,
                              capture_output=True, check=True).stdout.decode().strip()
        tree_prev = tree
        prev = subprocess.run(["git", "-C", d, *IDENT, "commit-tree", tree, "-p", prev,
                               "-m", f"rewrite {i}"], capture_output=True,
                              check=True).stdout.decode().strip()
    git(d, "update-ref", "refs/heads/master", prev)
    git(d, "symbolic-ref", "HEAD", "refs/heads/master")
    git(d, "reset", "-q", "--hard", prev)
    os.unlink(idx) if os.path.exists(idx) else None
    print(f"{d} commits={int(git(d, 'rev-list', '--count', 'HEAD'))} "
          f"score.md_lines={int(git(d, 'show', 'HEAD:score.md').decode().count(chr(10)))} "
          f"tip={prev}")


if __name__ == "__main__":
    main()
