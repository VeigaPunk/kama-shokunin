#!/usr/bin/env python3
"""FinalCase44: document-level twin comparison for the PG44/PG45 pair.

A twin equality claim requires TWO PRESENT verdict documents.  A refusal
has no document, so a pair of refusals is NOT twin equality.  This script
asserts that and compares the two documents field by field.
"""
import json
from pathlib import Path

OUT = Path("/fast/scratch/hyaku/kama-r24/postfix/FinalCase44/out/pair")
cand = json.loads((OUT / "candidate.json").read_text())
rows = {r["case"]: r for r in cand["arms"]["current"]["rows"]}
a = rows["PG44-missing-unused-tree-promisor"]
b = rows["PG45-missing-unused-tree-plain"]

print("PG44: exit", a["exit"], "document_present", a["document"] is not None,
      "twin_equal", a.get("twin_equal"), "twins", a.get("twins"))
print("PG45: exit", b["exit"], "document_present", b["document"] is not None,
      "twin_equal", b.get("twin_equal"), "twins", b.get("twins"))
print("BOTH documents present:",
      a["document"] is not None and b["document"] is not None,
      "-> twin equality is a real comparison, not two missing documents")
print("documents byte-identical:", a["document"] == b["document"])
if a["document"] != b["document"]:
    da, db = a["document"], b["document"]
    for k in sorted(set(da) | set(db)):
        if da.get(k) != db.get(k):
            print("  DIFF", k, "->", da.get(k), "vs", db.get(k))
print("PG44 defects", a["defects"], "raw", a["raw_defects"])
print("PG45 defects", b["defects"], "raw", b["raw_defects"])
print("PG44 objects_acquired", a["objects_acquired"])
print("PG45 objects_acquired", b["objects_acquired"])
print("PG44 stderr_tail", repr(a["stderr_tail"]))
print("PG45 stderr_tail", repr(b["stderr_tail"]))
print("PG44 forbidden 'partial clone (' in stderr:",
      "partial clone (" in a["stderr_tail"],
      "| 'promisor pack':", "promisor pack" in a["stderr_tail"])
print("PG44 problems", a["problems"], "amended", a["amended_problems"],
      "original", a["original_problems"])
print("PG45 problems", b["problems"], "amended", b["amended_problems"],
      "original", b["original_problems"])
print("PG45 expected(amended view):", b["expectation"]["amended"])
print("live expectation equals registered {defects:[],exit:0,kinds:[],reason_class:null}:",
      b["expectation"]["amended"] == {"defects": [], "exit": 0, "kinds": [],
                                      "reason_class": None})
s = cand["arms"]["current"]
for k in ("graded", "violations", "violating_cases", "amended_view_met",
          "amended_view_total", "amended_view_unmet", "original_view_unmet",
          "withdrawn_original_failures", "amendment_changed_cases",
          "twin_pairs_compared", "twin_mismatch", "tracebacks", "timeouts",
          "harness_leaks"):
    print("arm summary", k, "=", s.get(k))
print("auditor_sha256", cand["auditor_sha256"])
print("grid_sha256", cand["grid_sha256"])
print("expectations_sha256", cand["expectations_sha256"])
print("population_sha256", cand["population_sha256"],
      "size", cand["population_size"])
