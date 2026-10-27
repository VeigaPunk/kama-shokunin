#!/usr/bin/env python3
"""head-hash-check.py - re-derive the HASH facts of the SCORECARD.md head `## Axes`
table at a lane revision (corpus/QUALITY.md KQ49, HASH half only).

Question: does every `` `PATH` md5|sha256 `HEX` `` fact in the head axes table match the
blob PATH at --tip?

This is the HASH half of tools/round41-scorecard-reconcile.py, whose other facts (RUN
lines, LINES counts, paths, scores) execute lane commands and are not evaluated here. It
exists because round 53 changed SKILL.md in place (C2) - a file the head depth row
hashes - and the build's SCORECARD diff adds no head line.

Usage: python3 head-hash-check.py --repo <git dir> --tip <full commit>
Output (one line, exit 0 met / 1 not met / 2 unreadable):
  axes=6 hash_facts=7 hash_bad=0 met=True
and one `detail:` line per bad fact with the expected and observed digest.
"""
import argparse
import hashlib
import re
import subprocess
import sys

FACT = re.compile(r"`([^`]+)`\s+(md5|sha256)\s+`([0-9a-f]+)`")


def git(repo, *args):
    p = subprocess.run(["git", "-C", repo, *args], capture_output=True)
    if p.returncode:
        raise SystemExit(f"could not-eval: git {' '.join(args)}: {p.stderr.decode()[:160]}")
    return p.stdout


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", required=True)
    ap.add_argument("--tip", required=True)
    a = ap.parse_args(argv)
    try:
        text = git(a.repo, "show", f"{a.tip}:SCORECARD.md").decode("utf-8", "replace")
    except SystemExit as exc:
        print(exc)
        return 2
    lines = text.split("\n")
    try:
        start = lines.index("## Axes")
    except ValueError:
        print("could not-eval: no `## Axes` heading")
        return 2
    rows, in_table = [], False
    for ln in lines[start + 1:]:
        if ln.startswith("|"):
            rows.append(ln)
            in_table = True
        elif in_table:
            break
    data = [r for r in rows if not re.match(r"^\|[\s\-|]+\|$", r)]
    axes = 0
    facts = bad = 0
    details = []
    for r in data:
        cs = [c.strip() for c in r.strip().strip("|").split("|")]
        if not cs or cs[0].lower().startswith("axis"):
            continue
        axes += 1
        if len(cs) < 3:
            continue
        for path, algo, want in FACT.findall(cs[2]):
            facts += 1
            try:
                blob = git(a.repo, "show", f"{a.tip}:{path}")
            except SystemExit:
                bad += 1
                details.append(f"detail: {cs[0]}: {path} absent at --tip")
                continue
            got = hashlib.new(algo, blob).hexdigest()
            if got != want:
                bad += 1
                details.append(f"detail: {cs[0]}: {path} {algo} want {want[:12]} got {got[:12]}")
    print(f"axes={axes} hash_facts={facts} hash_bad={bad} met={bad == 0}")
    for d in details:
        print(d)
    return 0 if bad == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
