#!/usr/bin/env python3
# Case-33 independent oracle: re-derives semantic facts from each SCORECARD commit WITHOUT
# importing or reading tools/round42-selfdesc-reconcile.py. Reports the flags each commit raises
# beyond the pinned base (differential), to compare with the tool's met= verdict.
import os
import re
import subprocess
import sys

CL = os.environ["CL"]
SUMMARY = sys.argv[1]
BASE_SHA = sys.argv[2]


def git(*a):
    return subprocess.run(["git", "-C", CL, *a], capture_output=True, encoding="utf-8").stdout


def exists(sha, path):
    return subprocess.run(["git", "-C", CL, "cat-file", "-e", f"{sha}:{path}"],
                          capture_output=True).returncode == 0


def scan(sha):
    text = git("show", f"{sha}:SCORECARD.md")
    lines = text.split("\n")
    in_fence = False
    outside, fenced_heads = [], 0
    for i, l in enumerate(lines):
        if l.strip().startswith("```"):
            in_fence = not in_fence
            outside.append((i, "FENCE", l))
            continue
        if in_fence:
            if l.startswith("## "):
                fenced_heads += 1
            outside.append((i, "FENCED", l))
        else:
            outside.append((i, "TEXT", l))
    text_lines = [(i, l) for i, k, l in outside if k == "TEXT"]
    flags = set()

    # O1 maxN: highest round heading, space optional (outside fences); banner must match it
    heads = [(i, int(m.group(1))) for i, l in text_lines for m in [re.match(r"^## Round ?(\d+)", l)] if m]
    maxn = max(n for _, n in heads)
    banner = re.search(r"Latest measured round: (\d+)", "\n".join(lines[:8]))
    if not banner or int(banner.group(1)) != maxn:
        flags.add("O1-banner-vs-maxN")

    # O2 canonical table: highest 'canonical list as of round N' header in ANY punctuation form
    hdr = [(i, int(m.group(1))) for i, l in text_lines for m in [re.search(r"canonical list as of round\s+(\d+)", l, re.I)] if m]
    cn_i, cn = max(hdr, key=lambda t: t[1])
    rows = []
    for l in lines[cn_i + 1:]:
        if l.startswith("|"):
            rows.append([c.strip() for c in l.strip().strip("|").split("|")])
        elif rows:
            break
    names = {r[0].strip("` *") for r in rows[2:]}
    mir_i = next(i for i, l in text_lines if l.strip() == "## Capabilities")
    mrows = []
    for l in lines[mir_i + 1:]:
        if l.startswith("## "):
            break
        if l.startswith("|"):
            mrows.append([c.strip() for c in l.strip().strip("|").split("|")])
    mnames = {r[0].strip("` *") for r in mrows[2:]}
    if names != mnames:
        flags.add(f"O2-canon-r{cn}-vs-mirror")

    # O3 live plan: '### Planned (round maxN+1)' must sit inside the '## Round maxN' section
    ph = f"### Planned (round {maxn + 1})"
    cur_sec, plan_sec = None, []
    for i, l in text_lines:
        if l.startswith("## "):
            cur_sec = l
        if l.strip() == ph:
            plan_sec.append(cur_sec)
    if not any(s and re.match(rf"^## Round {maxn}\b", s) for s in plan_sec):
        flags.add("O3-live-plan-not-in-round-section")

    # O4 exactly one '## Retired' heading; capability count token exact
    ret = [i for i, l in text_lines if l.strip() == "## Retired"]
    if len(ret) != 1:
        flags.add(f"O4-retired-headings={len(ret)}")
    rstart = ret[0] if ret else None
    if rstart is not None:
        body = []
        for l in lines[rstart + 1:]:
            if l.startswith("## "):
                break
            body.append(l)
        toks = re.findall(r"\b(\d+) capabilities\b", "\n".join(body))
        if toks and any(int(t) != len(names) for t in toks):
            flags.add("O4-retired-capability-token")

    # O5 fence-aware headings: '## ' lines inside fenced blocks shadow section scoping
    if fenced_heads:
        flags.add(f"O5-fenced-heading-lines={fenced_heads}")

    # O6 every backticked .ufo/ path cited anywhere in SCORECARD exists at the commit
    for tok in sorted(set(re.findall(r"`(\.ufo/[^`\s<>*$]+)`", text))):
        if not exists(sha, tok):
            flags.add(f"O6-missing:{tok}")
    return flags, maxn, cn, len(names)


base_flags, bmax, bcn, bnames = scan(BASE_SHA)
print(f"base {BASE_SHA[:8]}: maxN={bmax} canon=r{bcn} rows={bnames} flags={len(base_flags)}")
rows = [l.rstrip("\n").split("\t") for l in open(SUMMARY, encoding="utf-8")][1:]
print("label\ttool_met\ttool_mismatches\toracle_new_flags")
for label, sha, rc, summary, *_ in rows:
    if sha.startswith("b89bdab2") or sha.startswith("7c873d7b"):
        continue
    try:
        flags, mx, cn, nm = scan(sha)
    except StopIteration:
        print(f"{label}\t{summary.split('met=')[-1]}\t-\toracle-could-not-parse")
        continue
    new = sorted(flags - base_flags)
    met = summary.split("met=")[-1] if "met=" in summary else "?"
    mism = summary.split("mismatches=")[-1].split()[0] if "mismatches=" in summary else "?"
    print(f"{label}\tmet={met}\tmismatches={mism}\t{';'.join(new) or 'none'}")
