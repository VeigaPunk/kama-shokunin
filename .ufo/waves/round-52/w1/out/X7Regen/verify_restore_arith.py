#!/usr/bin/env python3
"""X7Regen supporting arithmetic: tie the build's restored blocks to the lines
this seat's engine finds unheld at the base, and check the tip ledger's ten rows
against the base ledger's A/A-row rows.

All numbers are recomputed here from the clone at --tip and the base engine JSON
produced by recompute_c2.py at --base.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("rc2", os.path.join(HERE, "recompute_c2.py"))
rc2 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(rc2)

HEADINGS = (b"## Restored lines (round 52)", b"### Restored lines (round 52)")


def restored_counts(lines):
    idx = [i for i, l in enumerate(lines) if l.rstrip(b"\r") in HEADINGS]
    if not idx:
        return None
    seg = lines[idx[0]:]
    inside = False
    cnt = 0
    for l in seg:
        s = l.decode("utf-8", "surrogateescape").rstrip("\r")
        m = re.match(r"^ {0,3}(`{3,}|~{3,})(.*)$", s)
        if not inside:
            if m and not (m.group(1)[0] == "`" and "`" in m.group(2)):
                inside = True
            continue
        if m and m.group(1)[0] == "`" and len(m.group(1)) >= 5 and m.group(2).strip() == "":
            inside = False
            continue
        cnt += 1
    return cnt


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", required=True)
    ap.add_argument("--tip", required=True)
    ap.add_argument("--base", default="9ff76b1f763512be2f554cbbfd0b2213b63b0847")
    ap.add_argument("--base-engine-json", required=True)
    a = ap.parse_args()
    repo, tip, base = a.repo, a.tip, a.base
    eng = json.load(open(a.base_engine_json))

    names = rc2.git(repo, "ls-tree", "-r", "--name-only", tip).decode().splitlines()
    restored = {}
    for n in names:
        c = restored_counts(rc2.split_lines(rc2.blob(repo, tip, n)))
        if c:
            restored[n] = c
    base_unheld = {p: d["unheld"] for p, d in eng["per_file"].items() if d["unheld"]}
    print(f"files with a restored block: {len(restored)}; fenced content lines: {sum(restored.values())}")
    print(f"base engine unheld total: {sum(base_unheld.values())} "
          f"in {len(base_unheld)} files")
    print("per-file restored vs base unheld:")
    for p in sorted(set(restored) | set(base_unheld)):
        r, u = restored.get(p, 0), base_unheld.get(p, 0)
        mark = "" if r == u else f"   <-- difference {r - u:+d}"
        print(f"  {p}\trestored={r}\tbase_unheld={u}{mark}")

    base_led = rc2.blob(repo, base, rc2.LEDGER).decode().splitlines()
    tip_led = rc2.blob(repo, tip, rc2.LEDGER).decode().splitlines()
    def rows(ls):
        return [l.split("\t") for l in ls if l.strip() and not l.startswith("commit\t")]
    br, tr = rows(base_led), rows(tip_led)
    noncorr = [r for r in br if r[1] in ("corpus/SOURCES.md",
                                        "registry/report-landing-errata.tsv")]
    print(f"base ledger rows={len(br)} (A-corr={len(br) - len(noncorr)}, A/A-row={len(noncorr)})")
    print(f"tip ledger rows={len(tr)}")
    print(f"every tip row is a base row: "
          f"{all(any(tuple(x) == tuple(y) for y in br) for x in tr)}")
    print(f"tip rows == base A/A-row rows: "
          f"{sorted(map(tuple, tr)) == sorted(map(tuple, noncorr))}")
    contract = rc2.read_contract(repo, tip)
    corr_only = {r["path"] for r in contract if r["rule"] == "A-corr"}
    bad = [r for r in tr if r[1] in corr_only]
    print(f"tip ledger rows naming an A-corr file: {len(bad)}")
    extra = {p: restored.get(p, 0) - base_unheld.get(p, 0)
             for p in restored if restored.get(p, 0) != base_unheld.get(p, 0)}
    print(f"restored-minus-base-unheld per file: {extra} (sum "
          f"{sum(restored.values()) - sum(base_unheld.values()):+d})")


if __name__ == "__main__":
    main()
