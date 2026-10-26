#!/usr/bin/env python3
"""manifest-crosscheck.py - compare the outside trend verdicts of the lane's
trend-verdict ledger with the fleet MANIFEST.json closure entries (round-44
closure D4: the round-44 probe printed DIFF lines but always exited 0).

For every non-absent `outside` row of the ledger (header `round trend side
verdict ...`), the kama closure entry with `trends` for that lane round (the
last one wins) must give the same verdict.

  manifest-crosscheck.py <ledger.tsv> <MANIFEST.json>
  manifest-crosscheck.py --selftest

Output: one `DIFF ...`, `no-manifest ...` or `absent-in-ledger ...` line per
finding, then `outside_rows_compared=N agree=A diff=D no_manifest=M
absent_with_manifest=K`.
Exit: 0 diff=0 and no_manifest=0; 1 any diff or a non-absent outside row with
no MANIFEST verdict; 2 could not evaluate (unreadable or malformed input).
Read-only; --selftest writes fixtures under TMPDIR and removes them.
"""
from __future__ import annotations

import json
import os
import shutil
import sys
import tempfile


def check(ledger, manifest, out=print):
    try:
        lines = [x.rstrip("\n").split("\t") for x in open(ledger) if x.strip()]
        man = json.load(open(manifest))["rounds"]
    except (OSError, ValueError, KeyError, TypeError) as e:
        out(f"could-not-evaluate: {e}")
        return 2
    if not lines or lines[0][:4] != ["round", "trend", "side", "verdict"]:
        out("could-not-evaluate: ledger header is not `round trend side verdict ...`")
        return 2
    mt = {}
    for i, e in enumerate(man):
        if isinstance(e, dict) and e.get("lane") == "kama" and isinstance(e.get("trends"), dict):
            mt[str(e.get("lane_round", e.get("round")))] = (i, e["trends"])
    agree = diff = nom = absent_m = 0
    for r in lines[1:]:
        if len(r) < 4 or r[2] != "outside":
            continue
        i, tr = mt.get(r[0], (None, {}))
        mv = tr.get(r[1])
        if r[3] == "absent":
            if mv:
                absent_m += 1
                out(f"absent-in-ledger round={r[0]} {r[1]} manifest rounds[{i}]={mv}")
            continue
        if mv is None:
            nom += 1
            out(f"no-manifest round={r[0]} {r[1]}")
        elif str(mv).replace(" ", "-") == r[3]:
            agree += 1
        else:
            diff += 1
            out(f"DIFF round={r[0]} {r[1]} ledger={r[3]} manifest rounds[{i}]={mv}")
    out(f"outside_rows_compared={agree + diff} agree={agree} diff={diff} no_manifest={nom} "
        f"absent_with_manifest={absent_m}")
    return 1 if diff or nom else 0


def selftest():
    root = tempfile.mkdtemp(prefix="manifest-crosscheck-")
    fails = 0
    try:
        man = os.path.join(root, "MANIFEST.json")
        json.dump({"rounds": [{"lane": "kama", "lane_round": 10, "trends": {"quality": "improved"}},
                              {"lane": "kama", "lane_round": 11, "trends": {"quality": "harmed"}}]}, open(man, "w"))
        hdr = "round\ttrend\tside\tverdict\n"
        good = os.path.join(root, "good.tsv")
        open(good, "w").write(hdr + "10\tquality\toutside\timproved\n11\tquality\toutside\tharmed\n"
                              "11\tquality\tself\timproved\n")
        bad = os.path.join(root, "bad.tsv")
        open(bad, "w").write(hdr + "10\tquality\toutside\tunchanged\n")
        nom = os.path.join(root, "nom.tsv")
        open(nom, "w").write(hdr + "12\tquality\toutside\timproved\n")
        junk = os.path.join(root, "junk.tsv")
        open(junk, "w").write("not a ledger\n")
        q = lambda *a: None
        cases = [("agreeing ledger exits 0", check(good, man, q) == 0),
                 ("one-row mutant exits 1", check(bad, man, q) == 1),
                 ("row without MANIFEST verdict exits 1", check(nom, man, q) == 1),
                 ("malformed ledger exits 2", check(junk, man, q) == 2),
                 ("missing MANIFEST exits 2", check(good, os.path.join(root, "none.json"), q) == 2)]
        for name, ok in cases:
            print(f"{'pass' if ok else 'FAIL'} {name}")
            fails += not ok
    finally:
        shutil.rmtree(root, ignore_errors=True)
    print(f"MANIFEST_CROSSCHECK_SELFTEST pass={5 - fails} fail={fails}")
    return 1 if fails else 0


if __name__ == "__main__":
    if sys.argv[1:] == ["--selftest"]:
        sys.exit(selftest())
    if len(sys.argv) != 3:
        print(__doc__)
        sys.exit(2)
    sys.exit(check(sys.argv[1], sys.argv[2]))
