#!/usr/bin/env python3
"""Proposed KQ check: a census summary sentence must name every class its receipt carries.

usage: census-summary-check.py --receipt <census validate out> --sentence <file with the summary sentence>
exit 0 the sentence names every class with the right count, 1 it does not, 2 unusable input.
"""
import argparse, collections, re, sys

a = argparse.ArgumentParser()
a.add_argument("--receipt", required=True)
a.add_argument("--sentence", required=True)
g = a.parse_args()

hist = collections.Counter()
try:
    for line in open(g.receipt, encoding="utf-8"):
        f = line.rstrip("\n").split("\t")
        if len(f) >= 2 and re.fullmatch(r"(W\d\d|E)", f[1]):
            hist[f[1]] += 1
except OSError as e:
    print(f"could-not-evaluate: {e}", file=sys.stderr)
    sys.exit(2)

sentence = open(g.sentence, encoding="utf-8").read()
named = {c: int(n) for n, c in re.findall(r"(\d+)\s+(W\d\d|E)\b", sentence)}

bad = 0
for cls in sorted(set(hist) | set(named)):
    got, said = hist.get(cls, 0), named.get(cls)
    if said is None:
        bad += 1
        print(f"missing class {cls}: receipt has {got}, sentence does not name it")
    elif said != got:
        bad += 1
        print(f"count mismatch {cls}: receipt {got}, sentence {said}")
print("receipt=" + " ".join(f"{c}={hist[c]}" for c in sorted(hist)))
print("sentence=" + " ".join(f"{c}={named[c]}" for c in sorted(named)))
print("met=" + ("True" if bad == 0 else "False"))
sys.exit(0 if bad == 0 else 1)
