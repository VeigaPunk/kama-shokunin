#!/usr/bin/env python3
"""report-filed-once.py - does a round report exist once, filed after the final lane tip?

Question (round-48 outside closure R2: the round-48 report was filed with placeholders
before its cited tip existed and rewritten in place 58 s later): at a fleet report path,
is there exactly one commit that ADDS the report, no later commit that modifies it, and is
the add no earlier than the final lane commit the report cites?

Read-only: every git call is `git -C <repo> log/show/rev-parse`. Nothing is written.

Usage:
  report-filed-once.py --fleet-repo /home/vgpnk/Projects/shokunin \
      --report .ufo/reports/round-48/kama.md \
      --lane-repo /home/vgpnk/Projects/shokunin/kama-shokunin \
      --tip 4d8334af1c45bce74fa6a3904a7f6aa3a1ec630e
  report-filed-once.py ... --json

Legs:
  add       exactly one commit with `--diff-filter=A` touches the report path
  rewrite   no other commit (non-merge) touches it; a correction is an appended row in
            registry/report-landing-errata.tsv naming the superseded text, not an in-place
            rewrite of the filed report
  after_tip the add commit's author time is not earlier than the tip's author time
            (author time, as tools/report-landing-audit.py does, because rebases rewrite
            committer time)

Output: `report=<rel> adds=1 rewrites=0 tip_gap_s=<n> met=True`
Exit: 0 met, 1 not met, 2 could-not-evaluate (missing report / unusable git).
"""
import argparse
import json
import subprocess
import sys


def git(repo, *args):
    p = subprocess.run(["git", "-C", repo] + list(args), capture_output=True, text=True)
    if p.returncode != 0:
        raise RuntimeError("git " + " ".join(args) + ": " + (p.stderr.strip() or "rc=%d" % p.returncode))
    return p.stdout


def history(repo, rel, added_only=False):
    args = ["log", "--no-merges", "--format=%H\t%at"]
    if added_only:
        args.append("--diff-filter=A")
    args += ["--", rel]
    rows = []
    for line in git(repo, *args).splitlines():
        if not line.strip():
            continue
        sha, at = line.split("\t")
        rows.append((sha, int(at)))
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--fleet-repo", required=True)
    ap.add_argument("--report", required=True)
    ap.add_argument("--lane-repo", default=None)
    ap.add_argument("--tip", default=None)
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()

    res = {"report": a.report, "adds": 0, "rewrites": 0, "add": None, "add_at": None,
           "tip": a.tip, "tip_at": None, "tip_gap_s": None, "met": False, "error": None}
    try:
        adds = history(a.fleet_repo, a.report, added_only=True)
        touching = history(a.fleet_repo, a.report)
        if not adding_exists(a.fleet_repo, a.report):
            res["error"] = "report path is not a regular file at HEAD"
            emit(res, a.json)
            return 2
        res["adds"] = len(adds)
        if adds:
            res["add"] = adds[0][0]
            res["add_at"] = adds[0][1]
        res["rewrites"] = len([r for r in touching if r[0] not in {x[0] for x in adds}])
        if a.tip:
            if not a.lane_repo:
                raise RuntimeError("--tip needs --lane-repo")
            sha = git(a.lane_repo, "rev-parse", "--verify", a.tip + "^{commit}").strip()
            res["tip"] = sha
            res["tip_at"] = int(git(a.lane_repo, "show", "-s", "--format=%at", sha).strip())
            if res["add_at"] is not None:
                res["tip_gap_s"] = res["add_at"] - res["tip_at"]
        res["met"] = (res["adds"] == 1 and res["rewrites"] == 0
                      and (res["tip_gap_s"] is None or res["tip_gap_s"] >= 0))
    except (RuntimeError, ValueError) as exc:
        res["error"] = str(exc)
        emit(res, a.json)
        return 2
    emit(res, a.json)
    return 0 if res["met"] else 1


def adding_exists(repo, rel):
    try:
        git(repo, "cat-file", "-e", "HEAD:" + rel)
        return True
    except RuntimeError:
        return False


def emit(res, as_json):
    if as_json:
        print(json.dumps(res, indent=1, sort_keys=True))
        return
    print("report=%s adds=%d rewrites=%d add=%s add_at=%s tip=%s tip_at=%s tip_gap_s=%s met=%s"
          % (res["report"], res["adds"], res["rewrites"], res["add"], res["add_at"],
             res["tip"], res["tip_at"], res["tip_gap_s"], res["met"]))
    if res["error"]:
        print("error: " + res["error"])


if __name__ == "__main__":
    sys.exit(main())
