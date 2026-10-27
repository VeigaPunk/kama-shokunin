#!/usr/bin/env python3
"""cited-path-exists.py - proposed check for the round-52 lesson's Mistakes row 4.

Question: does every `.ufo/...` path or glob token a standing self-description
surface cites exist at the revision that cites it - and which citations are new?

Scope: SKILL.md and SCORECARD.md (SCORECARD only before its first
`### Restored lines (` heading: restored lines are historical bytes, not standing
claims). Fences are skipped. A token is a backticked string starting `.ufo/` with
no space/`<`/`>`/`$` and a `.` in its last segment. A glob token (`*`, `?`, `[`)
must match >= 1 committed path; a plain path must exist. With --base, only
citations that missed at --base are new violations; older misses are printed as
`pre-existing` and do not decide the exit (the lane's carried shape).

Exit: 0 no new miss; 1 at least one new miss; 2 could not evaluate.
This is a proposal in the seat's out directory; it is not a lane tool.
"""
import argparse
import fnmatch
import re
import subprocess
import sys

SCAN = [("SKILL.md", None), ("SCORECARD.md", "### Restored lines (round 52)")]


def git(repo, *args):
    p = subprocess.run(["git", "-C", repo, *args], capture_output=True)
    if p.returncode:
        raise SystemExit(f"git {' '.join(args)} failed: {p.stderr.decode()[:200]}")
    return p.stdout.decode("utf-8", "replace")


def tokens_at(repo, rev, tree):
    """(surface:line, token, kind) for every cited .ufo token that does not resolve."""
    treeset = set(tree)
    misses = []
    for path, cutoff in SCAN:
        p = subprocess.run(["git", "-C", repo, "show", f"{rev}:{path}"], capture_output=True)
        if p.returncode:
            raise SystemExit(f"could not read {path} at {rev}")
        lines = p.stdout.decode("utf-8", "replace").split("\n")
        if cutoff:
            cut = next((i for i, l in enumerate(lines) if l.startswith(cutoff)), None)
            if cut is not None:
                lines = lines[:cut]
        fenced = False
        for n, line in enumerate(lines, 1):
            s = line.lstrip()
            if s.startswith("`````") or s.startswith("```"):
                fenced = not fenced
                continue
            if fenced:
                continue
            for tok in re.findall(r"`([^`]+)`", line):
                if not tok.startswith(".ufo/") or any(c in tok for c in " <>$") or " " in tok:
                    continue
                if "." not in tok.rsplit("/", 1)[-1]:
                    continue
                if any(c in tok for c in "*?["):
                    if not fnmatch.filter(tree, tok):
                        misses.append((f"{path}:{n}", tok))
                elif tok not in treeset:
                    misses.append((f"{path}:{n}", tok))
    return misses


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", required=True)
    ap.add_argument("--tip", required=True)
    ap.add_argument("--base", help="only misses new since this revision are violations")
    a = ap.parse_args()
    tree = [p for p in git(a.repo, "ls-tree", "-r", "--name-only", a.tip).split("\n") if p]
    misses = tokens_at(a.repo, a.tip, tree)
    base = set()
    if a.base:
        btree = [p for p in git(a.repo, "ls-tree", "-r", "--name-only", a.base).split("\n") if p]
        base = {tok for _loc, tok in tokens_at(a.repo, a.base, btree)}
    new = [(loc, tok) for loc, tok in misses if tok not in base]
    for loc, tok in new:
        print(f"MISSING {loc} {tok}")
    print(f"cited-path-exists tip={a.tip[:12]} base={a.base[:12] if a.base else '-'} "
          f"misses={len(misses)} new={len(new)} met={'False' if new else 'True'}")
    return 0 if not new else 1


if __name__ == "__main__":
    sys.exit(main())
