#!/usr/bin/env python3
"""Independent cross-check for round-55 C2.

Imports the FROZEN counter read-only (no edit) and re-derives, from the counter's own
survey primitives, the four fields the seat must compare: cited / unresolved / disclosed /
dropped. Prints the per-token unresolved set and the ledger rows so a human can confirm
the 14 unresolved citations are exactly the 14 ledger-disclosed rows at the landed tip,
and that the base tip's single drop is the round-52 spot-check citation.

Usage: xcheck_c2.py <counter-path> <lane-clone> <tip> <fleet> <fleet-rev>
"""
import importlib.util
import os
import sys

counter_path, clone, tip, fleet, frev = sys.argv[1:6]

spec = importlib.util.spec_from_file_location("r54c2", counter_path)
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

lane = m.Repo(clone, tip)
fl = m.Repo(fleet, frev)
base = m.Repo(clone, m.BASE)

print("counter file:", counter_path)
print("BASE constant in counter:", m.BASE)
print("tip:", tip, "fleet:", frev)

cited, unres = m.survey(lane, fl)
print("cited:", sum(len(v) for v in cited.values()),
      "unresolved:", sum(len(v) for v in unres.values()))
print("unresolved tokens by surface:")
for s in sorted(unres):
    for t in sorted(unres[s]):
        print("  ", s, t, unres[s][t])

rows = m.read_ledger(lane)
print("ledger rows at tip:", len(rows))
for r in rows:
    print("  row", r["line"], r["surface"], r["token"], r["class"], "|", r["evidence"], "|", r.get("note", ""))

# drop set, derived directly
exempt = {(r["surface"], r["token"]) for r in rows
          if r["class"] in ("fixed", "externalized", "superseded")}
print("exempt (fixed/externalized/superseded):", sorted(exempt))
for surf in m.SURFACES:
    bt = m.show(clone, m.BASE, surf) or ""
    tt = m.show(clone, tip, surf) or ""
    bset = {tok for _n, tok, *_r in m.citations(bt)} - {t for s, t in exempt if s == surf}
    tset = {tok for _n, tok, *_r in m.citations(tt)}
    print(f"  {surf}: base-cited={len(bset)} tip-cited={len(tset)} dropped={sorted(bset - tset)}")
