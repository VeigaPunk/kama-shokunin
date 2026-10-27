#!/usr/bin/env python3
"""X7Regen supporting probe: region coverage, fence sensitivity, A-row permitted
detail, and duplicate risk of the disclosed lines. Uses this seat's own engine
helpers (recompute_c2.py); it does not touch the frozen counter or tool.

Reads the unheld set from recompute_c2.py's JSON (--engine-json) so the loss set
is the engine's, not a second derivation.
"""
from __future__ import annotations

import argparse
import collections
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
    ap.add_argument("--engine-json", required=True)
    a = ap.parse_args()
    repo, tip = a.repo, a.tip
    eng = json.load(open(a.engine_json))

    rows = rc2.read_contract(repo, tip)
    files = {}
    for r in rows:
        for path in rc2.expand(repo, tip, r["path"]):
            files[path] = (r["rule"], r["region"])

    commits = rc2.git(repo, "rev-list", "--topo-order", "--parents", tip).decode().splitlines()
    commits.reverse()
    sec_counts = collections.Counter()        # (file, section, graded) -> n
    fenced_deleted = collections.Counter()    # file -> deleted lines inside a fence
    grade_flips = []                          # fence-aware vs fence-blind
    arow_reasons = collections.Counter()      # reason -> n
    arow_not_permitted = []                   # (commit, id, reason, changed cells)
    for cline in commits:
        parts = cline.split()
        c, parents = parts[0], parts[1:]
        if not parents:
            continue
        p = parents[0]
        patch = rc2.git(repo, "diff", "--no-color", "--no-ext-diff", "--no-renames",
                        "-U0", p, c)
        for old_path, new_path, delnos, binary in rc2.sections_of_patch(patch):
            path = new_path if new_path in files else (old_path if old_path in files else None)
            if path is None or binary or not delnos:
                continue
            rule, region = files[path]
            plines = rc2.split_lines(rc2.blob(repo, p, path))
            new_lines = rc2.split_lines(rc2.blob(repo, c, path))
            secs, fl = rc2.sections(plines)
            # fence-blind sections: recompute with the module switch on
            old_flag = rc2.FENCE_BLIND
            rc2.FENCE_BLIND = True
            blind, _ = rc2.sections(plines)
            rc2.FENCE_BLIND = old_flag
            new_rows_by_id = {}
            if rule == "A-row":
                for nl in new_lines:
                    rid = rc2.row_id(nl)
                    if rid:
                        cs = rc2.split_cells(nl)
                        if cs:
                            new_rows_by_id.setdefault("S" + rid, []).append(cs)
            for n in delnos:
                line = plines[n - 1]
                sec = secs[n - 1]
                bsec = blind[n - 1]
                mode, arg = region
                def grade_of(s):
                    if mode == "all":
                        return True
                    if mode == "exempt":
                        return s not in arg
                    return s is not None and s.startswith(arg)
                g = grade_of(sec)
                gb = grade_of(bsec)
                if sec != bsec:
                    grade_flips.append((c, path, n, sec, bsec, g, gb))
                if fl[n - 1]:
                    fenced_deleted[path] += 1
                sec_counts[(path, sec, g)] += 1
                if rule == "A-row" and rc2.row_id(line) is not None:
                    ok, why = rc2.permitted_row_survivor(line, new_rows_by_id)
                    arow_reasons[why] += 1
                    if not ok:
                        cells = rc2.split_cells(line)
                        rid = rc2.row_id(line)
                        surv = new_rows_by_id.get("S" + rid, [])
                        changed = []
                        if surv and cells:
                            for nc in surv:
                                if len(nc) != len(cells):
                                    changed.append("<cell-count>")
                                    continue
                                for k in range(len(cells)):
                                    if nc[k] != cells[k]:
                                        changed.append(k)
                        arow_not_permitted.append((c, "S" + rid, why, sorted(set(changed))))

    def section_grades(path):
        d = collections.defaultdict(lambda: [0, 0])
        for (f, sec, g), n in sec_counts.items():
            if f == path:
                d[sec][0 if g else 1] += n
        return d

    out = []
    out.append("== REGION GRADE TABLE (per file and section heading in the PARENT blob)")
    for path in sorted(files):
        rule, region = files[path]
        if rule == "A-row":
            continue
        d = section_grades(path)
        if not d:
            continue
        mode, arg = region
        out.append(f"-- {path} rule={rule} region={mode} "
                   f"{'' if arg is None else (len(arg) if mode == 'exempt' else arg)}")
        for sec in sorted(d, key=lambda x: (x is not None, x or "")):
            graded, ungraded = d[sec]
            out.append(f"   {'<no section>' if sec is None else sec}\tgraded={graded}\tungraded={ungraded}")
    out.append("")
    out.append("== FENCE SENSITIVITY")
    out.append(f"deleted lines inside a parent fence: "
               f"{dict(sorted(fenced_deleted.items()))}")
    out.append(f"deletions whose parent section differs fence-aware vs fence-blind: "
               f"{len(grade_flips)}")
    for f in grade_flips:
        out.append("  " + repr(f))
    out.append("")
    out.append("== A-ROW PERMITTED DETAIL")
    out.append(f"reasons: {dict(sorted(arow_reasons.items()))}")
    out.append("not permitted (these are the graded A-row lines):")
    for r in arow_not_permitted:
        out.append(f"  {r[0][:12]} {r[1]} reason={r[2]} immutable_cell_indices_changed={r[3]}")

    out.append("")
    out.append("== DISCLOSED (UNHELD) LINE CONTENT AND DUPLICATE RISK")
    tip_sources = rc2.split_lines(rc2.blob(repo, tip, "corpus/SOURCES.md"))
    tip_ids = {}
    for nl in tip_sources:
        rid = rc2.row_id(nl)
        if rid:
            tip_ids.setdefault("S" + rid, 0)
            tip_ids["S" + rid] += 1
    errata = rc2.blob(repo, tip, "registry/report-landing-errata.tsv").decode().splitlines()
    errata_keys = {"\t".join(r.split("\t")[:3]) for r in errata
                   if r.strip() and not r.startswith("#")}
    for u in eng["unheld"]:
        c = u["commit"]
        plines = rc2.split_lines(rc2.blob(repo, c + "^", u["file"]))
        hits = [l for l in plines if rc2.key(l) == u["line_sha256"]]
        text = hits[0].decode("utf-8", "replace") if hits else "<line not found>"
        subj = rc2.git(repo, "log", "-1", "--format=%s", c).decode().strip()
        extra = ""
        if u["file"] == "corpus/SOURCES.md":
            rid = rc2.row_id(hits[0]) if hits else None
            extra = f" id_in_tip={'S' + rid in tip_ids if rid else None}"
        elif u["file"] == "registry/report-landing-errata.tsv" and hits:
            k = "\t".join(hits[0].decode().split("\t")[:3])
            extra = f" key_in_tip={k in errata_keys}"
        out.append(f"-- {c[:12]} {u['file']} {u['line_sha256'][:12]} count={u['count']}{extra}")
        out.append(f"   commit: {subj[:110]}")
        out.append(f"   line:   {text[:220]}")
    sys.stdout.write("\n".join(out) + "\n")


if __name__ == "__main__":
    main()
