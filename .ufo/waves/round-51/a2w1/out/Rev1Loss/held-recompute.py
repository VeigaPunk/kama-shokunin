#!/usr/bin/env python3
"""Reproduce the v6 held() measure for the LOG.md deletion at ed135b3c.

Definition implemented (tools/append-only-audit.py v6 docstring, v2 'held'):
  D    deleted multiset of the first-parent -U0 diff (byte-exact, header lines dropped)
  K    the parent's lines the diff kept (parent multiset minus D)
  M    the file's lines at the audited tip
  held = sum over l of min(D[l], max(0, M[l] - K[l]))
  lost = |D| - held   (graded lines not held; each must be disclosed or the event is bad)
Line keys follow v5 key(l): the line bytes with one trailing CR removed.

Usage: python3 held-recompute.py <repo> <commit> <file> <tip>
Exit 0 always; prints the per-line table and the totals.
"""
import collections
import hashlib
import subprocess
import sys


def git(repo, *args):
    return subprocess.run(["git", "-C", repo] + list(args),
                          capture_output=True, check=True).stdout


def lines(repo, rev, path):
    seg = git(repo, "show", f"{rev}:{path}").split(b"\n")
    return seg[:-1] if seg and seg[-1] == b"" else seg


def main():
    repo, commit, path, tip = sys.argv[1:5]
    parent = lines(repo, f"{commit}^", path)
    head = lines(repo, tip, path)
    out = git(repo, "show", "-U0", "--format=", commit, "--", path)
    D = collections.Counter()
    for raw in out.split(b"\n"):
        if raw.startswith(b"-") and not raw.startswith(b"---"):
            D[raw[1:]] += 1
    K = collections.Counter(parent)
    for line, count in D.items():
        K[line] -= count
    print("lineno\tsha256\theld\tcount\ttip\tK\ttext")
    total_held = 0
    for i, (line, count) in enumerate(D.items(), 1):
        held = min(count, max(0, head.count(line) - K[line]))
        total_held += held
        key = line[:-1] if line.endswith(b"\r") else line
        print(f"{i}\t{hashlib.sha256(key).hexdigest()}\t{held}\t{count}\t"
              f"{head.count(line)}\t{K[line]}\t{line.decode()}")
    print(f"\ndeleted={sum(D.values())} held={total_held} lost={sum(D.values()) - total_held}")


if __name__ == "__main__":
    main()
