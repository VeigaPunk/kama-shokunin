#!/usr/bin/env python3
"""X7Regen cross-check: recompute the same C2 quantities with a second,
independent deletion detector (difflib.SequenceMatcher opcodes) instead of the
git-diff hunk positions used by recompute_c2.py.

It reuses this seat's own rule helpers from recompute_c2.py (fence/section,
region, cell/row, holding) but derives the deleted parent lines itself, so the
result does not depend on git's diff algorithm.
"""
from __future__ import annotations

import argparse
import collections
import difflib
import importlib.util
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("rc2", os.path.join(HERE, "recompute_c2.py"))
rc2 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(rc2)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", required=True)
    ap.add_argument("--tip", required=True)
    ap.add_argument("--json", default=None)
    a = ap.parse_args()
    repo, tip = a.repo, a.tip

    rows = rc2.read_contract(repo, tip)
    files = {}
    for r in rows:
        for path in rc2.expand(repo, tip, r["path"]):
            files[path] = (r["rule"], r["region"])
    tip_keys = {p: collections.Counter(rc2.key(l) for l in rc2.split_lines(rc2.blob(repo, tip, p)))
                for p in files}

    commits = rc2.git(repo, "rev-list", "--topo-order", "--parents", tip).decode().splitlines()
    commits.reverse()
    stats = {p: collections.Counter() for p in files}
    unheld_by_file = collections.Counter()
    unheld_rows = []
    events = 0
    diff_events = 0
    for cline in commits:
        parts = cline.split()
        c, parents = parts[0], parts[1:]
        if not parents:
            continue
        p = parents[0]
        changed = rc2.git(repo, "diff", "--name-only", "--no-renames", p, c).decode().splitlines()
        for path in changed:
            if path not in files:
                continue
            rule, region = files[path]
            plines = rc2.split_lines(rc2.blob(repo, p, path))
            new_lines = rc2.split_lines(rc2.blob(repo, c, path))
            if plines == new_lines:
                continue
            delpos = []
            sm = difflib.SequenceMatcher(None, plines, new_lines, autojunk=False)
            for tag, i1, i2, _j1, _j2 in sm.get_opcodes():
                if tag in ("delete", "replace"):
                    delpos.extend(range(i1, i2))
            if not delpos:
                continue
            diff_events += 1
            events += 1
            psecs = rc2.sections(plines)[0]
            new_rows_by_id = {}
            if rule == "A-row":
                for nl in new_lines:
                    rid = rc2.row_id(nl)
                    if rid:
                        cs = rc2.split_cells(nl)
                        if cs:
                            new_rows_by_id.setdefault("S" + rid, []).append(cs)
            G = collections.Counter()
            D = collections.Counter()
            for i in delpos:
                line = plines[i]
                k = rc2.key(line)
                D[k] += 1
                stats[path]["deleted"] += 1
                sec = psecs[i]
                mode, arg = region
                if mode == "all":
                    grade = True
                elif mode == "exempt":
                    grade = sec not in arg
                else:
                    grade = sec is not None and sec.startswith(arg)
                if grade and rule == "A-row" and rc2.row_id(line) is not None:
                    ok, _ = rc2.permitted_row_survivor(line, new_rows_by_id)
                    if ok:
                        grade = False
                        stats[path]["permitted_rows"] += 1
                if grade:
                    G[k] += 1
                    stats[path]["graded"] += 1
            pkeys = collections.Counter(rc2.key(l) for l in plines)
            for k, g in G.items():
                kept = max(0, pkeys.get(k, 0) - D[k])
                M = tip_keys[path].get(k, 0)
                restored = max(0, M - kept)
                held = min(g, restored)
                stats[path]["held_by_tip"] += held
                if g - held > 0:
                    unheld_by_file[path] += g - held
                    unheld_rows.append({"commit": c, "file": path, "line_sha256": k,
                                        "count": g - held})

    led_raw = rc2.blob(repo, tip, rc2.LEDGER)
    ledger = []
    for ln in led_raw.decode().splitlines():
        if not ln.strip() or ln.startswith("commit\t"):
            continue
        commit, f, sha, count, klass, note = ln.split("\t")
        ledger.append((commit, f, sha, int(count)))
    led_keys = collections.Counter(ledger)
    my_keys = collections.Counter((r["commit"], r["file"], r["line_sha256"], r["count"])
                                  for r in unheld_rows)
    a_corr = [p for p, (r, _) in files.items() if r == "A-corr"]
    corr_lost = sum(unheld_by_file[p] for p in a_corr)
    row_lost = sum(unheld_by_file[p] for p in files if files[p][0] in ("A", "A-row"))
    out = {
        "files": len(files), "commits": len(commits), "events": events,
        "deletion_events_gitplusdifflib": diff_events,
        "corr_lost": corr_lost, "row_lost": row_lost,
        "ledger_rows": len(ledger), "ledger_matched": len(led_keys & my_keys),
        "ledger_missing": [list(x) for x in (led_keys - my_keys).elements()],
        "my_extra": [list(x) for x in (my_keys - led_keys).elements()],
        "per_file": {p: dict(stats[p], unheld=unheld_by_file[p])
                     for p in files if stats[p]["deleted"]},
    }
    print(json.dumps(out, indent=1, sort_keys=True))
    if a.json:
        with open(a.json, "w") as fh:
            json.dump(out, fh, indent=1, sort_keys=True)


if __name__ == "__main__":
    main()
