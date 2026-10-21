#!/usr/bin/env python3
"""Read-only check (kama round-21 scout, SrcJjRebaseTimestamps).

Does the C1 report-cutoff pre/post split, which tools/report-landing-audit.py
computes on committer epoch (%ct, audit lines 86, 98, 121-122 at a29bb84), differ
from the same split on author epoch (%at)? Also counts lane commits whose
committer epoch differs from author epoch. NOT an official audit run: the L1
owns official measurements.

Usage: python3 cutoff_check.py [LANE_REPO] [FLEET_REPO] [REV]
Only git read commands are issued (log, show); no repository is modified.
"""
import re
import subprocess
import sys

LANE = sys.argv[1] if len(sys.argv) > 1 else "/home/vgpnk/Projects/shokunin/kama-shokunin"
FLEET = sys.argv[2] if len(sys.argv) > 2 else "/home/vgpnk/Projects/shokunin"
REV = sys.argv[3] if len(sys.argv) > 3 else "a29bb84"


def git(repo, *args):
    result = subprocess.run(["git", "-C", repo, *args], capture_output=True, text=True)
    if result.returncode != 0:
        raise SystemExit(f"git {' '.join(args)} failed: {result.stderr.strip()}")
    return result.stdout


rows = [
    line.split("\t", 4)
    for line in git(LANE, "log", "--format=%H%x09%an%x09%at%x09%ct%x09%s", REV).splitlines()
    if line
]
kama = [r for r in rows if r[1] == "kama-shokunin"]
print(f"lane={LANE} rev={REV} commits={len(rows)} kama_commits={len(kama)}")
print(f"kama commits with committer epoch != author epoch: "
      f"{sum(1 for r in kama if r[3] != r[2])} of {len(kama)}")

landed = re.compile(r"^## Landed changes[^\n]*\n(.*?)(?=^## |\Z)", re.S | re.M)
flips = []
checked = 0
for rnd in range(10, 21):
    rel = f".ufo/reports/round-{rnd}/kama.md"
    adds = git(FLEET, "log", "--diff-filter=A", "--format=%ct", "--", rel).split()
    if not adds:
        print(f"round {rnd}: no fleet commit adds {rel}")
        continue
    cutoff = int(adds[-1])
    match = landed.search(git(FLEET, "show", f"HEAD:{rel}"))
    section = match.group(1) if match else ""
    pat = re.compile(rf"^(?:round-{rnd}:|checkpoint\(r{rnd}\))")
    for sha, an, at, ct, subj in rows:
        if an != "kama-shokunin" or not pat.match(subj):
            continue
        checked += 1
        pre_ct = int(ct) <= cutoff
        pre_at = int(at) <= cutoff
        if pre_ct != pre_at:
            flips.append((rnd, sha[:9], pre_ct, pre_at, int(ct) - int(at), sha[:7] in section, subj[:48]))

print(f"round-10..20 round/checkpoint commits checked: {checked}")
print(f"pre/post flips committer-epoch vs author-epoch: {len(flips)}")
for f in flips:
    print(f"  r{f[0]} {f[1]} ct_pre={f[2]} at_pre={f[3]} ct-at={f[4]}s cited={f[5]} | {f[6]}")
hidden = sum(1 for f in flips if (not f[2]) and f[3] and not f[5])
print(f"flips hiding an uncited commit under %ct: {hidden}")
