#!/usr/bin/env python3
"""K2Design evidence: independent re-derivation of the append-only-audit facts.

Usage: python3 analysis.py <repo> <tip>
Read-only on <repo> (git plumbing only). Prints six sections:
  1 events + the deleted lines the tip no longer holds
  2 blank-line accounting per event ("" element of split("\\n"))
  3 relocation: restored lines that the same commit re-adds
  4 below-threshold deletions (1..19 lines per commit,file) and lines lost at tip
  5 SCORECARD head axis-row in-place replacements
  6 merges in history (first-parent diff has live instances)
"""
import collections
import subprocess
import sys

FILES = ["SCORECARD.md", "LOG.md", "corpus/QUALITY.md", "corpus/README.md", "corpus/SOURCES.md"]
AXIS = ["| **operability**", "| **freshness**", "| depth", "| **depth**", "| coverage",
        "| **coverage**", "| calibration", "| **calibration**", "| adjacency", "| **adjacency**"]


def main():
    repo, tip = sys.argv[1], sys.argv[2]

    def git(*a):
        p = subprocess.run(["git", "-C", repo, *a], capture_output=True, text=True)
        if p.returncode:
            raise SystemExit(p.stderr)
        return p.stdout

    commits = git("rev-list", "--topo-order", "--reverse", tip).split()
    parents = {}
    for line in git("rev-list", "--topo-order", "--reverse", "--parents", tip).split("\n"):
        p = line.split()
        if p:
            parents[p[0]] = p[1] if len(p) > 1 else None
    tip_lines = {}
    for f in FILES:
        spec = f"{tip}:{f}"
        out = subprocess.run(["git", "-C", repo, "cat-file", "--batch-check=%(objectname) %(objecttype)"],
                             input=spec + "\n", capture_output=True, text=True).stdout.split()
        blob = out[0] if len(out) == 2 and out[1] == "blob" else None
        tip_lines[f] = git("cat-file", "blob", blob).split("\n") if blob else [""]

    events = []
    below = collections.Counter()
    below_files = collections.Counter()
    below_commits = 0
    axis_hits = collections.Counter()
    axis_commits = set()
    for c in commits:
        p = parents.get(c)
        if not p:
            continue
        changed = set(git("diff", "--no-renames", "--name-only", p, c, "--", *FILES).split("\n")) - {""}
        for f in FILES:
            if f not in changed:
                continue
            d = git("diff", "--no-renames", "--no-color", "-U0", p, c, "--", f)
            lines = d.split("\n")
            dele = [x[1:] for x in lines if x.startswith("-") and not x.startswith("---")]
            add = set(x[1:] for x in lines if x.startswith("+") and not x.startswith("+++"))
            if f == "SCORECARD.md":
                for l in dele:
                    for a in AXIS:
                        if l.startswith(a):
                            axis_hits[a.strip()] += 1
                            axis_commits.add(c[:8])
            if not dele:
                continue
            tipset = set(tip_lines[f])
            miss = [l for l in dele if l not in tipset]
            if len(dele) >= 20:
                events.append((c, f, dele, miss, add, tipset))
            else:
                below_commits += 1
                below["1-4" if len(dele) < 5 else ("5-9" if len(dele) < 10 else "10-19")] += 1
                if miss:
                    below_files[f] += len(miss)

    print("== 1 events and lines the tip no longer holds")
    for c, f, dele, miss, add, tipset in events:
        print(f"{c[:12]} {f} deleted={len(dele)} restored_at_tip={len(dele)-len(miss)} missing={len(miss)}")
        for l in miss:
            print("   missing:", repr(l[:180]))
    print("\n== 2 blank-line accounting (\"\" from split; each deleted blank is auto-restored)")
    for c, f, dele, miss, add, tipset in events:
        blank = sum(1 for x in dele if x == "")
        print(f"{c[:12]} {f} deleted_blank={blank} empty_element_in_tip={'' in tipset}")
    print("\n== 3 relocation: restored lines the same commit re-adds")
    for c, f, dele, miss, add, tipset in events:
        restored = [x for x in dele if x in tipset]
        same = [x for x in restored if x in add]
        print(f"{c[:12]} {f} restored={len(restored)} re_added_in_same_commit={len(same)}")
    print("\n== 4 below-threshold deletions (1..19 lines, per commit,file)")
    print("commits:", below_commits, "buckets:", dict(below))
    print("lines absent at tip, per file:", dict(below_files), "total:", sum(below_files.values()))
    print("\n== 5 SCORECARD head axis-row in-place replacements")
    print("row deletions:", dict(axis_hits))
    print("commits:", len(axis_commits), sorted(axis_commits))
    print("\n== 6 merges")
    print("merges in history:", len(git("rev-list", "--merges", tip).split()))


if __name__ == "__main__":
    main()
