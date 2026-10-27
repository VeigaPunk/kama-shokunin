#!/usr/bin/env python3
"""sweep-build-tip.py - did any round-50 receipt cite a tip that did not exist yet?

Round-50 lesson, Mistakes row 3 guard.  A receipt that names `tip=<sha>` can only
have been produced after that commit object existed.  If the receipt's first
committed state C does not descend from the cited tip T, the receipt text names a
commit it could not have seen at C - either it was run on an uncommitted tree and
the hash filled in later, or it was edited after the fact.

Read-only on the lane.  Exit 0 = no lane tip predates its receipt's commit,
1 = at least one does, 2 = usage/IO.
"""
from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys

TIP_RES = (re.compile(r"\btip=([0-9a-f]{40})\b"), re.compile(r"--tip[ =]([0-9a-f]{40})\b"))


def git(repo, *args):
    return subprocess.run(["git", "-C", repo, *args], capture_output=True, text=True)


def has_commit(repo, rev):
    return git(repo, "rev-parse", "--verify", "--quiet", rev + "^{commit}").returncode == 0


def is_ancestor(repo, a, b):
    return git(repo, "merge-base", "--is-ancestor", a, b).returncode == 0


def commit_time(repo, rev):
    return git(repo, "show", "-s", "--format=%cI", rev).stdout.strip()


def files(repo, wave):
    root = os.path.join(repo, wave)
    out = []
    for dirpath, dirs, names in os.walk(root):
        # a seat's scratch copy of the whole tree lives under w1/out/<seat>/homescratch/;
        # its historical receipts are not round-50 receipts
        dirs[:] = [d for d in dirs if d not in ("homescratch", "tree", ".git")]
        for n in sorted(names):
            p = os.path.join(dirpath, n)
            rel = os.path.relpath(p, repo)
            if not (rel.endswith(".out") or rel.endswith(".txt") or rel.endswith(".json")):
                continue
            if os.path.basename(rel) in ("spec.json", "dispatch.json", "preregistration.json",
                                         "swarm-registry.json"):
                continue
            out.append(rel)
    return out


def classify(repo, rel, add_commit, tip):
    if not has_commit(repo, tip):
        return "fixture/unknown tip (not a lane commit)", None
    if add_commit is None:
        if is_ancestor(repo, tip, "HEAD"):
            return "ok (uncommitted receipt, tip is a lane ancestor of HEAD)", None
        return "PREDATES (uncommitted receipt, tip not an ancestor of HEAD)", "PREDATES"
    if is_ancestor(repo, tip, add_commit):
        return "ok (receipt commit descends from the tip)", None
    return ("PREDATES (receipt committed at %s %s, before tip %s %s)"
            % (add_commit[:8], commit_time(repo, add_commit), tip[:8], commit_time(repo, tip)),
            "PREDATES")


def selftest(repo, build):
    """The check must fail on a receipt committed before the tip it cites."""
    base = git(repo, "rev-parse", "--verify", "26ecba64ad6fb571d09074b07202d1618a46ecd1^{commit}").stdout.strip()
    status, verdict = classify(repo, "(planted)", base, build)
    print("selftest: planted receipt committed at base %s citing build %s -> %s"
          % (base[:8], build[:8], status))
    if verdict != "PREDATES":
        print("selftest FAIL: the check did not flag a receipt older than its tip")
        return 1
    status2, verdict2 = classify(repo, "(control)", git(repo, "rev-parse", "HEAD").stdout.strip(), build)
    print("selftest: control receipt committed at HEAD citing build %s -> %s" % (build[:8], status2))
    if verdict2 is not None:
        print("selftest FAIL: the control was flagged")
        return 1
    print("selftest PASS")
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--repo", required=True, help="lane clone (read-only), full clone (commits present)")
    ap.add_argument("--wave", default=".ufo/waves/round-50")
    ap.add_argument("--build", default="97c864bead3ee4a2f629574e77263d33834ec98a")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args(argv)
    if a.selftest:
        return selftest(a.repo, a.build)
    if git(a.repo, "rev-parse", "--show-toplevel").returncode != 0:
        print("not a git repo:", a.repo)
        return 2
    bad = 0
    rows = 0
    for rel in files(a.repo, a.wave):
        try:
            text = open(os.path.join(a.repo, rel), encoding="utf-8", errors="replace").read()
        except OSError as exc:
            print("unreadable:", rel, exc)
            continue
        tips = sorted({m.group(1) for r in TIP_RES for m in r.finditer(text)})
        if not tips:
            continue
        add = git(a.repo, "log", "--diff-filter=A", "--format=%H", "--", rel).stdout.split()
        add_commit = add[-1] if add else None
        for tip in tips:
            status, verdict = classify(a.repo, rel, add_commit, tip)
            rows += 1
            print("%-70s tip=%s  %s" % (rel, tip[:12], status))
            if verdict:
                bad += 1
    print("rows=%d predates=%d" % (rows, bad))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
