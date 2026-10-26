#!/usr/bin/env python3
"""Round-44 C2 cross-check (not part of the frozen predicate): compare every
non-absent outside verdict of registry/verdict-ledger.tsv with the `trends`
object of the fleet MANIFEST.json closure entry for kama at that round (last
entry wins). Usage: manifest-crosscheck.py <ledger.tsv> <MANIFEST.json>"""
import json, sys
led = [l.rstrip("\n").split("\t") for l in open(sys.argv[1])][1:]
man = json.load(open(sys.argv[2]))["rounds"]
mt = {}
for i, e in enumerate(man):
    if e.get("lane") == "kama" and isinstance(e.get("trends"), dict):
        mt[str(e.get("lane_round", e.get("round")))] = (i, e["trends"])
agree = diff = absent_with_manifest = 0
for r in led:
    if r[2] != "outside":
        continue
    i, tr = mt.get(r[0], (None, {}))
    mv = tr.get(r[1])
    if r[3] == "absent":
        if mv:
            absent_with_manifest += 1
            print(f"absent-in-ledger round={r[0]} {r[1]} manifest rounds[{i}]={mv}")
        continue
    if mv is None:
        print(f"no-manifest round={r[0]} {r[1]}")
    elif mv.replace(" ", "-") == r[3]:
        agree += 1
    else:
        diff += 1
        print(f"DIFF round={r[0]} {r[1]} ledger={r[3]} manifest rounds[{i}]={mv}")
print(f"outside_rows_compared={agree + diff} agree={agree} diff={diff} absent_with_manifest={absent_with_manifest}")
