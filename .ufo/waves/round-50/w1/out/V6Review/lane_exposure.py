#!/usr/bin/env python3
"""V6Review: measure live exposure of the first-parent origins() defect on the lane
history at the build commit: for every audited file, compare origin computed with
first-parent-only parsing (tool, audit-v5.py:470) vs all-parent parsing (frozen
counter, round50-append-audit-v5-check.py:418). Divergent keys = deletions the two
definitions grade differently."""
import collections, importlib.util, subprocess, sys

spec = importlib.util.spec_from_file_location("aoa5", "/fast/scratch/hyaku/kama-r50/V6Review/audit-v5.py")
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

LANE = "/fast/scratch/hyaku/kama-r50/V6Review/lane"
TIP = "97c864bead3ee4a2f629574e77263d33834ec98a"

def git(*a, inp=None, binary=False):
    p = subprocess.run(["git", "-C", LANE, *a], input=inp, capture_output=True, check=True)
    return p.stdout if binary else p.stdout.decode("utf-8", "replace")

order = git("rev-list", "--topo-order", "--reverse", "--parents", TIP).split("\n")
commits, firstpar, allpar = [], {}, {}
for line in order:
    parts = line.split()
    if parts:
        commits.append(parts[0])
        firstpar[parts[0]] = parts[1] if len(parts) > 1 else None
        allpar[parts[0]] = parts[1:]
merges = [c for c in commits if len(allpar[c]) > 1]
print(f"commits={len(commits)} merges={len(merges)}")
for c in merges[:10]:
    print("  merge", c[:12], "parents", len(allpar[c]))

contract = git("show", f"{TIP}:registry/append-only-contract.tsv")
rows = m.parse_contract(contract)
patterns = [r[0] for r in rows]
files = m.expand(LANE, TIP, patterns)
print("audited files:", files)

def key(ln):
    return ln[:-1] if ln.endswith(b"\r") else ln

def origins_for(f, parent_map):
    bl = m.Repo(LANE).blobs([f"{x}:{f}" for x in commits]) if False else None
    r = m.Repo(LANE)
    bl = r.blobs([f"{x}:{f}" for x in commits])
    kc = {}
    def body_of(b):
        if b not in kc:
            body = r.list_lines(b) if b else []
            kc[b] = (body, {key(x) for x in body})
        return kc[b]
    def sec_titles(body):
        return m.sections(body)
    orig = collections.defaultdict(set)
    for x in commits:
        b = bl[f"{x}:{f}"]
        if b is None:
            continue
        body, keys = body_of(b)
        pkeys = set()
        for q in parent_map[x]:
            if q and bl.get(f"{q}:{f}") == b:
                pkeys = keys
                break
            qb = bl.get(f"{q}:{f}") if q else None
            if qb is not None:
                pkeys |= body_of(qb)[1]
        if pkeys is keys:
            continue
        for ln, t in zip(body, sec_titles(body)):
            k = key(ln)
            if k not in pkeys:
                orig[k].add(t)
    return orig

total_div = 0
for f in files:
    o_first = origins_for(f, {c: [firstpar[c]] if firstpar[c] else [] for c in commits})
    o_all = origins_for(f, allpar)
    keys = set(o_first) | set(o_all)
    div = {k for k in keys if o_first.get(k, set()) != o_all.get(k, set())}
    total_div += len(div)
    print(f"{f}: keys={len(keys)} divergent={len(div)}")
    for k in sorted(div)[:5]:
        print(f"   key {k!r}: first-parent-origin={sorted(o_first.get(k, set()))} "
              f"all-parent-origin={sorted(o_all.get(k, set()))}")
print(f"TOTAL divergent keys across audited files: {total_div}")
