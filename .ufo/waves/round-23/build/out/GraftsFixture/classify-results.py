#!/usr/bin/env python3
# classify-results.py RESULTS.tsv -- classify every fault x family cell of a graft-shallow-fixture
# matrix against the no-fault truth (fault=none, neutral=none) of the same family.
#   OK            same exit code and same defect set as truth
#   FALSE-CLEAN   truth failed (1), observed clean (0)
#   FALSE-FAIL    truth clean (0), observed failed (1)
#   UNDER-REPORT  both failed, observed defect set is a strict subset of truth's (verdict right, list short)
#   OVER-REPORT   both failed, observed defect set is a strict superset of truth's
#   WRONG-DEFECTS both failed, defect sets incomparable (e.g. unresolved instead of omitted)
#   REFUSED       exit 2 (could-not-evaluate)
import csv
import sys

rows = list(csv.DictReader(open(sys.argv[1]), delimiter="\t"))
truth = {r["family"]: r for r in rows if r["fault"] == "none" and r["neutral"] == "none"}


def defects(r):
    return set() if r["defects"] in ("-", "") else set(r["defects"].split(" "))


def classify(r):
    t = truth[r["family"]]
    if r["rc"] == "2":
        return "REFUSED"
    if r["status"] == "BUILD-FAIL":
        return "BUILD-FAIL"
    if r["rc"] == "0" and t["rc"] == "0":
        return "OK"
    if r["rc"] == "1" and t["rc"] == "1":
        o, tt = defects(r), defects(t)
        if o == tt:
            return "OK"
        if o < tt:
            return "UNDER-REPORT"
        if o > tt:
            return "OVER-REPORT"
        return "WRONG-DEFECTS"
    if r["rc"] == "0" and t["rc"] == "1":
        return "FALSE-CLEAN"
    if r["rc"] == "1" and t["rc"] == "0":
        return "FALSE-FAIL"
    return "OTHER"


modes = ["none", "nro", "nro-env", "nograft", "noshallow", "nro+nograft+noshallow"]
faults = []
for r in rows:
    if r["fault"] not in faults:
        faults.append(r["fault"])
cells = [r for r in rows if r["fault"] != "none"]

print("controls (fault=none) per neutralizer:",
      {m: sorted({classify(r) for r in rows if r["fault"] == "none" and r["neutral"] == m}) for m in modes})
print()
print("counts over the 40 fault x family cells, per neutralizer:")
for m in modes:
    counts = {}
    for r in cells:
        if r["neutral"] == m:
            k = classify(r)
            counts[k] = counts.get(k, 0) + 1
    print(f"  {m:24s} {dict(sorted(counts.items()))}")
print()
print("frozen auditor (neutral=none), fault x family:")
print(f"  {'fault':30s}" + "".join(f"{f:>16s}" for f in "ABCD"))
for f in faults[1:]:
    line = f"  {f:30s}"
    for fam in "ABCD":
        r = next(x for x in cells if x["fault"] == f and x["family"] == fam and x["neutral"] == "none")
        line += f"{classify(r):>16s}"
    print(line)
print()
print("cells not OK under nro+nograft+noshallow:")
for r in cells:
    if r["neutral"] == "nro+nograft+noshallow" and classify(r) != "OK":
        print(f"  {r['fault']} {r['family']} {classify(r)} {r['defects'][:90]}")
