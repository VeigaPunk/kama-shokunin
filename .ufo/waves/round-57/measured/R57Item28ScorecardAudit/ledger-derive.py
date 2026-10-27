#!/usr/bin/env python3
"""case49-ledger-derive.py -- re-derive the two calibration-row ledger counts.

Reads the lane ledgers at the working tree/HEAD and prints the figures the
SCORECARD calibration row asserts:
  verdict-ledger.tsv        rows, round range, agreement/present, overclaim,
                            underclaim, other, absent  (rounds 10-43)
  claim-outcome-ledger.tsv  rows, claims, round range, agreement/comparable,
                            overclaim, underclaim, other, absent (rounds 10-44)

Classification follows the SCORECARD's stated rules: same verdict/outcome =
agreement; self stronger = overclaim; self weaker = underclaim; `mixed` and any
pair the strength order cannot place = other; either side `absent` = absent.
`present`/`comparable` exclude absent keys; `comparable` also excludes `other`.
"""
from collections import Counter, defaultdict

TREND_ORDER = ["harmed", "unchanged", "unprovable", "unprovable-but-better", "improved"]
OUTCOME_ORDER = ["not-met", "unprovable", "partial", "met"]


def load(path):
    rows = [l.rstrip("\n").split("\t") for l in open(path, encoding="utf-8")][1:]
    return [r for r in rows if len(r) == 9]


def group(rows):
    keys = defaultdict(dict)
    for rnd, item, side, value, *_ in rows:
        keys[(rnd, item)][side] = value
    return keys


def classify(keys, order):
    c = Counter()
    for v in keys.values():
        s, o = v.get("self"), v.get("outside")
        if s is None or o is None or "absent" in (s, o):
            c["absent"] += 1
        elif s not in order or o not in order:
            c["other"] += 1
        elif s == o:
            c["agreement"] += 1
        elif order.index(s) > order.index(o):
            c["overclaim"] += 1
        else:
            c["underclaim"] += 1
    c["other"] = c.get("other", 0)
    return c


def main():
    v = load("registry/verdict-ledger.tsv")
    vk = group(v)
    vc = classify(vk, TREND_ORDER)
    vr = sorted({int(r[0]) for r in v})
    present = sum(v for k, v in vc.items() if k != "absent")
    print(f"verdict-ledger rows={len(v)} keys={len(vk)} rounds={vr[0]}-{vr[-1]} "
          f"agreement={vc['agreement']}/{present} overclaim={vc['overclaim']} "
          f"underclaim={vc['underclaim']} other={vc['other']} absent={vc['absent']}")
    c = load("registry/claim-outcome-ledger.tsv")
    ck = group(c)
    cc = classify(ck, OUTCOME_ORDER)
    cr = sorted({int(r[0]) for r in c})
    comparable = cc["agreement"] + cc["overclaim"] + cc["underclaim"]
    print(f"claim-outcome-ledger rows={len(c)} claims={len(ck)} rounds={cr[0]}-{cr[-1]} "
          f"agreement={cc['agreement']}/{comparable} overclaim={cc['overclaim']} "
          f"underclaim={cc['underclaim']} other={cc['other']} absent={cc['absent']}")


if __name__ == "__main__":
    main()
