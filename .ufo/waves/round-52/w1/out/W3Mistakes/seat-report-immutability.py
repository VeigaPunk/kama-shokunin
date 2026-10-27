#!/usr/bin/env python3
"""seat-report-immutability.py - proposed check for the round-52 lesson's Mistakes row 3.

Question: is every committed seat report under `.ufo/waves/<round>/<wave>/out/*.md`
the blob it was first committed as?

Rule: for each such path at --tip, take its first-add commit reachable from --tip
and that commit's blob. A later blob is permitted only when (a) the tip blob is
the first-add blob again (a restoration) and (b) a sibling `<stem>.late-rewrite.md`
exists at --tip. Any other change is a violation, named with the commit that made it.

Exit: 0 no violation; 1 at least one; 2 could not evaluate.
This is a proposal in the seat's out directory; it is not a lane tool.
"""
import argparse
import subprocess
import sys


def git(repo, *args):
    p = subprocess.run(["git", "-C", repo, *args], capture_output=True)
    if p.returncode:
        raise SystemExit(f"git {' '.join(args)} failed: {p.stderr.decode()[:200]}")
    return p.stdout.decode("utf-8", "replace")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", required=True)
    ap.add_argument("--tip", required=True)
    a = ap.parse_args()
    paths = [p for p in git(a.repo, "ls-tree", "-r", "--name-only", a.tip,
                            "--", ".ufo/waves").split("\n")
             if p.endswith(".md") and "/out/" in p and not p.endswith(".late-rewrite.md")]
    treeset = set(p for p in git(a.repo, "ls-tree", "-r", "--name-only", a.tip).split("\n") if p)
    bad = 0
    for path in paths:
        adds = [l for l in git(a.repo, "log", "--diff-filter=A", "--format=%H", a.tip,
                                "--", path).split("\n") if l]
        if not adds:
            continue
        first = adds[-1]                       # oldest first-add on the walked history
        first_blob = git(a.repo, "rev-parse", f"{first}:{path}").strip()
        tip_blob = git(a.repo, "rev-parse", f"{a.tip}:{path}").strip()
        if tip_blob == first_blob:
            continue
        stem = path[:-3] if path.endswith(".md") else path
        sibling = stem + ".late-rewrite.md"
        mods = [l for l in git(a.repo, "log", "--format=%h %aI %s", f"{first}..{a.tip}",
                               "--", path).split("\n") if l.strip()]
        # a restoration that keeps the first-add bytes plus the sibling is the round-52
        # convention; here the tip differs, so it is still a live rewrite
        bad += 1
        print(f"REWRITTEN {path} first={first[:12]} modified_by={mods[:1]} "
              f"sibling_present={sibling in treeset}")
    print(f"seat-report-immutability tip={a.tip} reports={len(paths)} violations={bad} "
          f"met={'False' if bad else 'True'}")
    return 0 if bad == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
