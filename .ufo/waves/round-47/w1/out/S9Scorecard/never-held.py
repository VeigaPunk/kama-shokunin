#!/usr/bin/env python3
"""never-held.py - name the deleted lines a mass-deletion event never holds again.

Implements the frozen v2 definitions of tools/append-only-audit.py (round-47 C1
counter docstring): lines are split on b"\\n" with a final non-empty segment
counted as a line; deletions are read from the first-parent diff's hunk headers
(not from the diff text, so a deleted line starting with `--` is not filtered);
held(x) = sum over line values l of min(D[l], max(0, M_x[l] - K[l])) with
K = M_parent - D; the window is the event commit through the audited tip.

usage: never-held.py <repo> <commit> <path> <tip>
Prints one line per deleted line value never held again in the window, with the
number of copies lost, and the deleted/held totals.
"""
import collections
import re
import subprocess
import sys

HUNK = re.compile(rb"^@@ -(\d+)(?:,(\d+))? \+\d+(?:,\d+)? @@")


def git(repo, *args):
    p = subprocess.run(["git", "-C", repo, *args], capture_output=True)
    if p.returncode != 0:
        raise SystemExit(f"git {' '.join(args)[:80]}: {p.stderr.decode()[:200]}")
    return p.stdout


def lines(repo, rev, path):
    p = subprocess.run(["git", "-C", repo, "cat-file", "-p", f"{rev}:{path}"],
                       capture_output=True)
    if p.returncode != 0:
        return []
    parts = p.stdout.split(b"\n")
    if parts and parts[-1] == b"":
        parts = parts[:-1]
    return parts


def deleted_indices(repo, commit, path):
    parent = commit + "^1"
    d = git(repo, "diff", "--no-renames", "--no-color", "--no-ext-diff", "-U0",
            parent, commit, "--", path)
    out = []
    for ln in d.split(b"\n"):
        m = HUNK.match(ln)
        if not m:
            continue
        start = int(m.group(1))
        n = int(m.group(2)) if m.group(2) is not None else 1
        out += list(range(start - 1, start - 1 + n))
    return out


def main():
    repo, commit, path, tip = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]
    parent = git(repo, "rev-parse", "--verify", f"{commit}^1").decode().strip()
    parent_lines = lines(repo, parent, path)
    idx = deleted_indices(repo, commit, path)
    D = collections.Counter(parent_lines[i] for i in idx)
    K = collections.Counter(parent_lines)
    for byte, n in D.items():
        K[byte] -= n
        if K[byte] == 0:
            del K[byte]
    window = git(repo, "rev-list", "--topo-order", "--reverse", f"{commit}..{tip}").decode().split()
    window = [commit] + [c for c in window if c]
    best = collections.Counter()
    for x in window:
        M = collections.Counter(lines(repo, x, path))
        for byte, n in D.items():
            hold = min(n, max(0, M[byte] - K[byte]))
            if hold > best[byte]:
                best[byte] = hold
    never = [(n - best[b], b) for b, n in D.items() if n > best[b]]
    never.sort(key=lambda t: (-t[0], t[1]))
    print(f"path={path} commit={commit[:12]} deleted={sum(D.values())} "
          f"held_max={sum(min(n, best[b]) for b, n in D.items())} "
          f"never_held={sum(n for n, _ in never)}")
    for n, b in never:
        print(f"never x{n}: {b.decode('utf-8', 'replace')!r}")


if __name__ == "__main__":
    main()
