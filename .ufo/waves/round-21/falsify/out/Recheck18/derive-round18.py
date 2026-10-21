#!/usr/bin/env python3
"""Independent derivation for kama round N (no import of the audit tool).
Usage: derive-round18.py LANE_REPO FLEET_REPO N
Classifies lane commits (author kama-shokunin; subject round-N: or checkpoint(rN))
against the fleet first-add commit of .ufo/reports/round-N/kama.md, once with
author time (%at) and once with committer time (%ct)."""
import os, re, subprocess, sys
lane, fleet, rnd = sys.argv[1], sys.argv[2], int(sys.argv[3])
ENV = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
ENV.update(GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_NOSYSTEM="1")
def git(repo, *args):
    p = subprocess.run(["git", "-C", repo, *args], capture_output=True, text=True, env=ENV)
    if p.returncode:
        raise SystemExit(f"git {' '.join(args)} rc={p.returncode}: {p.stderr.strip()}")
    return p.stdout
SEP, END = "\x1f", "\x1e"
recs = []
for rec in git(lane, "log", "master", f"--format=%H{SEP}%an{SEP}%at{SEP}%ct{SEP}%s{END}").split(END):
    rec = rec.lstrip("\n")
    if not rec:
        continue
    sha, an, at, ct, subj = rec.split(SEP, 4)
    recs.append({"sha": sha, "an": an, "at": int(at), "ct": int(ct), "subj": subj})
rel = f".ufo/reports/round-{rnd}/kama.md"
first = git(fleet, "log", "--diff-filter=A", "--format=%H %at %ct", "--", rel).strip().splitlines()[-1].split()
fsha, fat, fct = first[0], int(first[1]), int(first[2])
text = git(fleet, "show", f"{fsha}:{rel}")
m = re.search(r"^## Landed changes[^\n]*\n(.*?)(?=^## |\Z)", text, re.S | re.M)
if m is None:
    raise SystemExit("no Landed section")
landed = re.findall(r"(?<![0-9A-Za-z])[0-9a-f]{7,40}(?![0-9A-Za-z])", m.group(1))
pat = re.compile(rf"^(round-{rnd}:|checkpoint\(r{rnd}\))")
cands = [r for r in recs if r["an"] == "kama-shokunin" and pat.match(r["subj"])]
print(f"fleet first-add {fsha[:9]} at={fat} ct={fct}")
print(f"landed tokens: {landed}")
for key, cut in (("at", fat), ("ct", fct)):
    pre = [r for r in cands if r[key] <= cut]
    omitted = [r["sha"] for r in pre if not any(r["sha"].startswith(t) for t in landed)]
    print(f"[{key}-time] candidates={len(cands)} pre={len(pre)} post={len(cands) - len(pre)} omitted={omitted}")
for r in cands:
    print(f"  {r['sha'][:9]} at={r['at']} ct={r['ct']} d={r['ct'] - r['at']} {r['subj'][:72]}")
