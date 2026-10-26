#!/usr/bin/env python3
"""Identify, for the 0718b6ab SCORECARD.md event, the deleted lines v3 left ungraded
(the exempt-section carve-out) and v4 grades (origin outside every exempt title).
Read-only; imports the tip blob of tools/append-only-audit.py."""
import collections, importlib.util, subprocess, sys

REPO = sys.argv[1]
TIP = sys.argv[2]
BLOB = sys.argv[3]

spec = importlib.util.spec_from_file_location("aoa_v4", BLOB)
aoa = importlib.util.module_from_spec(spec)
spec.loader.exec_module(aoa)

r = aoa.Repo(REPO)
commits = []
parents = {}
for line in aoa._text(REPO, "rev-list", "--topo-order", "--reverse", "--parents", TIP).split("\n"):
    parts = line.split()
    if parts:
        commits.append(parts[0]); parents[parts[0]] = parts[1] if len(parts) > 1 else None

contract_text = aoa._text(REPO, "show", f"{TIP}:{aoa.CONTRACT}")
rows = aoa.parse_contract(contract_text)
F = "SCORECARD.md"

c = next(x for x in commits if x.startswith("0718b6ab"))
p = parents[c]
window = commits[commits.index(c):]
print(f"event={c} parent={p} window={len(window)}")

pb = r.blobs([f"{p}:{F}"])[f"{p}:{F}"]
pbody = r.list_lines(pb)
psec = aoa.sections(pbody)
pcount = r.section_counts(pb)
titles, prefixes = aoa.file_regions(rows, F)
wb = r.blobs([f"{x}:{F}" for x in window])
eligible = {t for t in titles
            if max(r.section_counts(wb[f"{x}:{F}"])[t] if wb[f"{x}:{F}"] else 0 for x in window) >= pcount[t]}
print("titles=", sorted(titles), "eligible=", sorted(eligible))

# tool's origin closure, copied verbatim in semantics
orig, seen = {}, set()
bl = r.blobs([f"{x}:{F}" for x in commits])
for x in commits:
    b = bl[f"{x}:{F}"]
    if b is None or b in seen:
        continue
    seen.add(b)
    body = r.list_lines(b)
    fresh = collections.defaultdict(set)
    for ln, t in zip(body, aoa.sections(body)):
        if ln not in orig:
            fresh[ln].add(t)
    orig.update(fresh)

dl = aoa.deleted_lines(REPO, p, c, F)
print(f"deleted={len(dl)} numstat_rows_in_tool=checked")
diff = [(pos, text) for pos, text in dl
        if psec[pos - 1] in eligible and not (orig.get(text, frozenset()) & titles)]
print(f"lines v3 ungraded / v4 graded = {len(diff)}")
for pos, text in diff:
    o = orig.get(text, frozenset())
    print(f"  parent_line={pos} parent_section={psec[pos-1]!r} origin_titles={sorted(t for t in o if t)!r} "
          f"origin_any={sorted(o)!r} text={text[:120]!r}")
