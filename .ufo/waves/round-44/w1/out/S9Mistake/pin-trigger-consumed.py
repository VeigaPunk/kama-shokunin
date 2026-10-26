#!/usr/bin/env python3
"""Proposed standing KQ check: a pin-watch `behind` must have a recheck consumer.

Reads a committed pin-watch receipt (lines `engine=<e> pin=<p> newest=<n> ...
status=behind`) and requires, at the lane tip, a ledger file
`registry/release-recheck-<newest>.tsv` for every behind engine.

usage: pin-trigger-consumed.py --repo <lane clone> --tip <commit> --receipt <pin-watch out>
exit 0 every behind has a consumer, 1 at least one does not, 2 unusable input.
"""
import argparse, subprocess, sys

a = argparse.ArgumentParser()
a.add_argument("--repo", required=True)
a.add_argument("--tip", required=True)
a.add_argument("--receipt", required=True)
g = a.parse_args()

behind = []
try:
    for line in open(g.receipt, encoding="utf-8"):
        for part in line.split("|"):
            cells = part.split()
            d = dict(c.split("=", 1) for c in cells if "=" in c)
            if d.get("status") == "behind" and d.get("engine") and d.get("newest"):
                behind.append((d["engine"], d["newest"]))
except OSError as e:
    print(f"could-not-evaluate: {e}", file=sys.stderr)
    sys.exit(2)
if not behind:
    print(f"no behind rows in {g.receipt}")
    print("met=True")
    sys.exit(0)

tree = subprocess.run(["git", "-C", g.repo, "ls-tree", "--name-only", g.tip, "registry/"],
                      capture_output=True, text=True)
if tree.returncode != 0:
    print(f"could-not-evaluate: {tree.stderr.strip()}", file=sys.stderr)
    sys.exit(2)
present = set(tree.stdout.split())
bad = 0
for engine, newest in behind:
    ledger = f"registry/release-recheck-{newest}.tsv"
    if ledger in present:
        print(f"ok {engine} newest={newest} consumer={ledger}")
    else:
        bad += 1
        print(f"missing {engine} newest={newest}: no {ledger} at {g.tip[:12]}")
print("met=" + ("True" if bad == 0 else "False"))
sys.exit(0 if bad == 0 else 1)
