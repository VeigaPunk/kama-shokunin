#!/usr/bin/env python3
"""report-wave-order.py - proposed check for the round-52 lesson's Mistakes row 1.

Question: was a round's fleet report filed before the wave it reports on had
landed all of its seat output?

Rule: the fleet report `.ufo/reports/round-N/kama.md` (first-add commit, author
time) must not be earlier than either (a) the latest lane commit whose author time
is on the history that ADDS a seat report `.ufo/waves/round-N/<wave>/out/*.md`
(a restore or a fix commit that only modifies one is not a late seat),
or (b) the first-add of that wave's `<wave>-results.json`. Author time is used
because a salvage/rebase may rewrite committer time (the round-51 salvage does not;
both are reported). Violations name the later commit.

Exit: 0 ordered; 1 report precedes seat output or the results record; 2 could not
evaluate (report absent). This is a proposal in the seat's out directory.
"""
import argparse
import subprocess
import sys

FLEET = "/home/vgpnk/Projects/shokunin"


def git(repo, *args):
    p = subprocess.run(["git", "-C", repo, *args], capture_output=True)
    if p.returncode:
        raise SystemExit(f"git -C {repo} {' '.join(args)} failed: {p.stderr.decode()[:200]}")
    return p.stdout.decode("utf-8", "replace")


def latest(repo, rev, *patterns, adds_only=False):
    """(author_epoch, commit, subject) of the last commit on rev's history touching pattern."""
    extra = ["--diff-filter=A"] if adds_only else []
    out = git(repo, "log", *extra, "--format=%at%x09%H%x09%s", rev, "--", *patterns).split("\n")
    rows = [l.split("\t", 2) for l in out if l.strip()]
    if not rows:
        return None
    rows.sort(key=lambda r: int(r[0]))
    t, c, s = rows[-1]
    return int(t), c, s


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lane", required=True)
    ap.add_argument("--fleet", default=FLEET)
    ap.add_argument("--round", type=int, required=True)
    a = ap.parse_args()
    report = f".ufo/reports/round-{a.round}/kama.md"
    adds = [l for l in git(a.fleet, "log", "--diff-filter=A", "--format=%at%x09%H%x09%s",
                           "--", report).split("\n") if l.strip()]
    if not adds:
        print(f"report-wave-order round={a.round} report=absent")
        return 2
    rt, rc, rs = adds[-1].split("\t", 2)
    rt = int(rt)
    seat = latest(a.lane, "HEAD", f":(glob).ufo/waves/round-{a.round}/*/out/*.md",
                  ":(exclude,glob).ufo/waves/round-*/**/*.late-rewrite.md", adds_only=True)
    results = latest(a.lane, "HEAD", f":(glob).ufo/waves/round-{a.round}/*/*-results.json")
    bad = 0
    print(f"report {a.round}: {rc[:12]} author={rt} {rs[:70]}")
    for name, item in (("seat-output", seat), ("results-record", results)):
        if item is None:
            print(f"{name}: none in lane history")
            continue
        t, c, s = item
        verdict = "BEFORE" if rt < t else "after"
        if rt < t:
            bad += 1
        print(f"{name}: {c[:12]} author={t} {s[:70]} -> report {verdict} by {abs(t - rt)}s")
    print(f"report-wave-order round={a.round} violations={bad} met={'False' if bad else 'True'}")
    return 0 if bad == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
