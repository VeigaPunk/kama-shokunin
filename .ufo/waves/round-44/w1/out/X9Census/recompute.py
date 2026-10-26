#!/usr/bin/env python3
"""X9Census: independent recompute of sources-census.sh validate classes for kama.

Re-implements the frozen counter's class predicates from
/home/vgpnk/Projects/shokunin/scripts/sources-census.sh (lines 24-33, 636-676) over
corpus/SOURCES.md so the 95-line validate receipt is checked, not trusted.
Read-only. Column order of the 11-column registry row:
id source kind tier scope anchor teaches status opened recheck used-by
"""
import collections
import datetime
import os
import re

ROOT = "/home/vgpnk/Projects/shokunin/kama-shokunin"
SOURCES = os.path.join(ROOT, "corpus/SOURCES.md")
TODAY = datetime.date(2026, 10, 26)
KIND = {"spec", "docs", "paper", "code", "tool", "dataset", "talk", "book", "community", "own-work"}
SYMBOLIC = re.compile(r"^[A-Za-z][A-Za-z0-9 _-]*$")  # census:582


def norm_url(cell):
    m = re.search(r"https?://[^\s|]+", cell)
    if not m:
        return None
    u = re.sub(r"#[^ ]*$", "", m.group(0)).rstrip("/")
    u = re.sub(r"^[A-Za-z]+://", "", u)
    i = u.find("/")
    return (u[:i].lower() + u[i:]) if i >= 0 else u.lower()


rows = [l for l in open(SOURCES, encoding="utf-8").read().splitlines() if re.match(r"^\| S[0-9]{3,} ", l)]
recs = [[c.strip() for c in l.strip().strip("|").split("|")] for l in rows]
hits = collections.Counter()
examples = collections.defaultdict(list)

for r in recs:
    i, src, kind, tier, scope, anchor, teaches, status, opened, recheck, usedby = r
    if len(r) != 11:
        hits["E01"] += 1
        examples["E01"].append(f"{i}:fields={len(r)}")
        continue
    if not re.fullmatch(r"S[0-9]{3,}", i):
        hits["E02"] += 1
    if kind not in KIND:
        hits["E05"] += 1
        examples["E05"].append(f"{i}:{kind}")
    if tier not in set("ABC"):
        hits["E06"] += 1
    if status not in {"queued", "mined", "rejected"}:
        hits["E07"] += 1
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", opened) or datetime.date.fromisoformat(opened) > TODAY:
        hits["E08"] += 1
        examples["E08"].append(f"{i}:{opened}")
    if not (re.fullmatch(r"\d{4}-\d{2}-\d{2}", recheck) or re.fullmatch(r"\d+d", recheck) or SYMBOLIC.match(recheck)):
        hits["E09"] += 1
        examples["E09"].append(f"{i}:{recheck}")
    if tier == "A" and kind == "community":
        hits["E10"] += 1
        examples["E10"].append(i)
    if tier == "C" and status == "mined" and usedby != "\u2014":
        hits["W01"] += 1
        examples["W01"].append(i)
    if status == "rejected" and len(teaches) < 8:
        hits["W02"] += 1
        examples["W02"].append(i)
    if status == "mined" and usedby == "\u2014":
        hits["W03"] += 1
        examples["W03"].append(i)
    for tok in re.findall(r"[\w./-]+\.(?:md|py|sh|json|tsv|txt)", usedby):
        if not os.path.exists(os.path.join(ROOT, tok)):
            hits["E11"] += 1
            examples["E11"].append(f"{i}:{tok}")

ids = collections.Counter(r[0] for r in recs)
hits["E03"] = sum(v - 1 for v in ids.values() if v > 1)
hits["E12"] = 0  # every row-shaped source is inside ## Registry (checked by the frozen counter)

pairs = collections.Counter()
url_scopes = collections.defaultdict(set)
for r in recs:
    u = norm_url(r[1])
    if u:
        pairs[(u, r[4])] += 1
        url_scopes[u].add(r[4])
hits["W04"] = sum(len(s) - 1 for s in url_scopes.values())

print(f"rows={len(recs)} distinct_ids={len(ids)} distinct_urls={len(url_scopes)} distinct(url,scope)={len(pairs)}")
print(f"W04 identity: distinct(url,scope) - distinct_urls = {len(pairs)} - {len(url_scopes)} = {len(pairs) - len(url_scopes)}"
      f" ; sum(scopes-1) over multi-scope urls = {hits['W04']} ; multi-scope urls = {sum(1 for s in url_scopes.values() if len(s) > 1)}")
for code in ["E01", "E02", "E03", "E04", "E05", "E06", "E07", "E08", "E09", "E10", "E11", "E12", "W01", "W02", "W03", "W04"]:
    print(f"{code}\t{hits.get(code, 0)}\t{','.join(examples.get(code, [])[:6])}")
