#!/usr/bin/env python3
"""SCT01 counter-evidence scan and class-coverage proof."""
import hashlib, importlib.util, json, subprocess
from collections import Counter

LANE = "/home/vgpnk/Projects/shokunin/kama-shokunin"
BASE = "cc6e1d3cf202ee3e17cd07f42fc63d2dca5f3bb7"
import os
S = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("aa", LANE + "/tools/append-only-audit.py")
aa = importlib.util.module_from_spec(spec); spec.loader.exec_module(aa)

def git(*args, check=True):
    p = subprocess.run(["git", "-C", LANE, *args], capture_output=True)
    if check and p.returncode != 0:
        raise RuntimeError(p.stderr.decode())
    return p

def text(*args):
    return git(*args).stdout.decode()

data = json.load(open(S + "/audit-base.json"))
rows = aa.parse_contract(text("show", f"{BASE}:registry/append-only-contract.tsv"))

def tsv(path):
    lines = text("show", f"{BASE}:{path}").split("\n")
    if lines and lines[-1] == "":
        lines.pop()
    h = lines.pop(0).split("\t")
    return [dict(zip(h, x.split("\t"))) for x in lines]

accepted = tsv("registry/append-only-accepted.tsv")
exempt = tsv("registry/append-only-exempt.tsv")

print("== invariant permitted+graded+ungraded == deleted ==")
viol = [(e["commit"], e["file"], e["permitted"], e["graded"], e["ungraded"], e["deleted"])
        for e in data["events"] if e["permitted"] + e["graded"] + e["ungraded"] != e["deleted"]]
print("violations:", len(viol))
for v in viol: print("  ", v)

print("\n== every event carrying permitted lines, with graded/ungraded ==")
for e in data["events"]:
    if e["permitted"]:
        print(f'  {e["commit"]} {e["file"]} status={e["status"]} deleted={e["deleted"]} graded={e["graded"]} ungraded={e["ungraded"]} permitted={e["permitted"]} undisclosed={len(e["undisclosed"])}')

print("\n== six-class coverage over all 241 events (accepted / exempt / permitted / out_of_region / restored / disclosed) ==")
acc_keys = set()
for r in accepted:
    acc_keys.add((r["commit"], r["file"]))
ex_rows = {}
for r in exempt:
    ex_rows.setdefault((r["commit"], r["file"]), []).append(r)

def detail(key):
    commit, file = key
    parent = text("rev-parse", f"{commit}^1").strip()
    body = aa.split_lines(git("show", f"{parent}:{file}").stdout)
    secs = aa.sections(body)
    dl = aa.deleted_lines(LANE, parent, commit, file)
    titles, prefixes = aa.file_regions(rows, file)
    return [(secs[p-1] if 0 < p <= len(secs) else None) for p, _, _ in dl], titles, prefixes

def in_region(sec, prefixes):
    return any(sec is not None and sec.startswith(p) for p in prefixes)

counts = Counter(); falls = []
for e in data["events"]:
    key = (e["commit"], e["file"])
    if e["status"] == "restored":
        counts["restored"] += 1; continue
    if e["status"] == "disclosed":
        counts["disclosed"] += 1; continue
    if key in acc_keys and e["undisclosed"]:
        counts["accepted"] += 1; continue
    if e["status"] == "ungraded":
        if e["permitted"] == e["deleted"] and e["graded"] == 0 and e["ungraded"] == 0:
            counts["permitted"] += 1; continue
        secs, titles, prefixes = detail(key)
        if prefixes and all(not in_region(s, prefixes) for s in secs):
            counts["out_of_region"] += 1; continue
        fit = False
        for r in ex_rows.get(key, []):
            if r["class"] == "exempt-head" and int(r["count"]) == e["ungraded"]:
                want = sorted(set(s for s in secs if s is not None))
                if want == sorted(r["sections"].split("|")):
                    fit = True
        if fit:
            counts["exempt"] += 1; continue
        if secs and set(secs) <= titles and secs:
            counts["head-eligible-unrowed"] += 1; continue
    falls.append((e["commit"], e["file"], e["status"], e["deleted"], e["graded"], e["ungraded"], e["permitted"]))

print("class counts:", dict(counts), "sum", sum(counts.values()))
print("fall-through events:", len(falls))
for f in falls: print("  FALL", f)

print("\n== all baseline receipts under .ufo/waves/*/measured/before/*.out at base: introduction ancestry ==")
paths = text("ls-tree", "-r", "--name-only", BASE).split("\n")
base_receipts = [p for p in paths if p.startswith(".ufo/waves/") and "/measured/before/" in p and p.endswith(".out")]
print("receipts:", len(base_receipts))
bad = []
for p in base_receipts:
    adds = text("log", "--diff-filter=A", "--format=%H", BASE, "--", p).split()
    if not adds:
        bad.append((p, "NO-ADD-COMMIT")); continue
    intro = adds[0]
    rc = git("merge-base", "--is-ancestor", intro, BASE, check=False).returncode
    if rc != 0:
        bad.append((p, intro, f"is-ancestor exit {rc}"))
print("introductions not an ancestor of base:", len(bad))
for b in bad: print("  BAD", b)

print("\n== newest closures in base tree ==")
cl = sorted(p for p in paths if p.startswith("corpus/lessons/") and p.endswith("-verifier-spotcheck.md"))
for p in cl[-5:]: print("  ", p)
