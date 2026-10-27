#!/usr/bin/env python3
"""Collect results.jsonl into a verdict table + classification.
Classification: KILLED (tip verdict flips met True->False or no-verdict crash),
SURVIVED (tip met=True), INCONCLUSIVE (baseline/tip infrastructure failure)."""
import json, os, re, sys

S = "/fast/scratch/hyaku/kama-r50/M1Ctr"
recs = {}
for ln in open(f"{S}/results.jsonl"):
    r = json.loads(ln)
    if r["label"] not in recs:          # keep first (reruns appended; dedupe later if needed)
        recs[r["label"]] = r
# allow reruns to override: re-read keeping LAST occurrence
recs = {}
for ln in open(f"{S}/results.jsonl"):
    r = json.loads(ln)
    recs[r["label"]] = r

ids = sorted({k.rsplit("-", 1)[0] for k in recs})
print(f"{'mutant':<16} {'tip verdict':<52} {'base verdict':<52} {'dur(t/b)':<14} class")
for i in ids:
    t, b = recs.get(f"{i}-tip"), recs.get(f"{i}-base")
    tv = t["verdict"] if t else "MISSING"
    bv = b["verdict"] if b else "MISSING"
    tv = tv or f"NO-VERDICT rc={t['rc']} {t['status']}"
    bv = bv or f"NO-VERDICT rc={b['rc']} {b['status']}"
    dur = f"{t['dur_s'] if t else '?'}s/{b['dur_s'] if b else '?'}s"
    if i == "pristine":
        cls = "BASELINE"
    elif "met=True" in tv:
        cls = "SURVIVED"
    elif "met=False" in tv or "NO-VERDICT" in tv:
        cls = "KILLED"
    else:
        cls = "?"
    print(f"{i:<16} {tv:<52} {bv:<52} {dur:<14} {cls}")
