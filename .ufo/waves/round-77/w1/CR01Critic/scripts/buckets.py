#!/usr/bin/env python3
"""Independent C2 bucket arithmetic from the frozen audit JSON + base registers."""
import fnmatch
import importlib.util
import json
import subprocess
from pathlib import Path

S = Path("/fast/scratch/hyaku/kama-r77/CR01Critic")
D = Path((S / "fixture-path.txt").read_text().strip())
BASE = "cc6e1d3cf202ee3e17cd07f42fc63d2dca5f3bb7"
data = json.loads((S / "receipts" / "audit-base.json").read_text())


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


audit_tool = load(D / "tools/append-only-audit.py", "aud")
acc_tool = load(D / "tools/round75-append-accepted.py", "acc")
ctext = subprocess.run(["git", "-C", str(D), "show", f"{BASE}:registry/append-only-contract.tsv"],
                       capture_output=True).stdout.decode()
rows = audit_tool.parse_contract(ctext)
acc_text = subprocess.run(["git", "-C", str(D), "show", f"{BASE}:registry/append-only-accepted.tsv"],
                          capture_output=True).stdout.decode()
exm_text = subprocess.run(["git", "-C", str(D), "show", f"{BASE}:registry/append-only-exempt.tsv"],
                          capture_output=True).stdout.decode()
ev = {(e["commit"], e["file"]): e for e in data["events"]}
print(f"events: {len(ev)} (summary.events={data['summary']['events']})")

restored = {k for k, e in ev.items() if e["status"] == "restored" and e["held_at_to"] == e["graded"]}
status_restored_only = {k for k, e in ev.items() if e["status"] == "restored"}
disclosed = {k for k, e in ev.items() if e["status"] == "disclosed"}
pre_acc = lambda c: subprocess.run(["git", "-C", str(D), "merge-base", "--is-ancestor", c,
                                    "10f37171fb696c542586cbee96ea4a509ab74afc"],
                                   capture_output=True).returncode == 0
g_bound = acc_tool.grade(data, acc_text, pre_acc)
g_free = acc_tool.grade(data, acc_text, None)
print(f"restored(status AND held_at_to==graded)={len(restored)} "
      f"(status==restored alone: {len(status_restored_only)})  disclosed={len(disclosed)}")
print(f"accepted with old temporal bound={g_bound['summary']['accepted']}  "
      f"accepted with NO temporal bound (ruling-(a) superset)={g_free['summary']['accepted']}")

sections = {}
for e in data["events"]:
    if e["status"] != "ungraded":
        continue
    commit, file = e["commit"], e["file"]
    parent = subprocess.run(["git", "-C", str(D), "rev-parse", f"{commit}^1"],
                            capture_output=True).stdout.decode().strip()
    body = audit_tool._git(str(D), "show", f"{parent}:{file}")
    secs = audit_tool.sections(audit_tool.split_lines(body))
    deleted = audit_tool.deleted_lines(str(D), parent, commit, file)
    titles, _ = audit_tool.file_regions(rows, file)
    parents = {secs[pos - 1] for pos, _, _ in deleted}
    sections[(commit, file)] = (sorted(t for t in parents if t is not None),
                                bool(parents) and parents <= titles)

valid_free, valid_bound, seen = set(), set(), set()
for line in exm_text.splitlines()[1:]:
    if not line.strip():
        continue
    cells = line.split("\t")
    if len(cells) != 6:
        continue
    commit, file, klass, count, titles, note = cells
    key = (commit, file)
    if key in seen:
        continue
    seen.add(key)
    e = ev.get(key)
    exp, eligible = sections.get(key, ([], False))
    if (e is not None and e["status"] == "ungraded" and e["graded"] == 0
            and e["ungraded"] == e["deleted"] and eligible and klass == "exempt-head"
            and titles == "|".join(exp) and note.strip() and str(e["ungraded"]) == count):
        valid_free.add(key)
        if pre_acc(commit):
            valid_bound.add(key)
print(f"exempt rows valid under C2 content checks: {len(valid_free)}; "
      f"of those also under the old single cutoff: {len(valid_bound)}")

only_paths = {f for f in {k[1] for k in ev}
              if any(fnmatch.fnmatchcase(f, p[0]) and p[3][0] == "only" for p in rows)}
arow_paths = {f for f in {k[1] for k in ev}
              if any(fnmatch.fnmatchcase(f, p[0]) and p[1] == "A-row" for p in rows)}
print(f"files with only= regions among event files: {sorted(only_paths)}")
print(f"files with A-row rule among event files: {sorted(arow_paths)}")

permitted, out_of_region = set(), set()
for k, e in sorted(ev.items()):
    if e["status"] != "ungraded" or k in valid_free:
        continue
    if e["permitted"] == e["deleted"] and e["graded"] == 0 and e["ungraded"] == 0:
        permitted.add(k)
    elif k[1] in only_paths and e["graded"] == 0 and e["permitted"] == 0:
        out_of_region.add(k)
print(f"permitted bucket (permitted==deleted AND graded==0 AND ungraded==0, uncovered): "
      f"{len(permitted)}; files: {sorted({f for _, f in permitted})}")
print(f"out_of_region bucket (uncovered, only=-file, graded==0, permitted==0): "
      f"{len(out_of_region)}; files: {sorted({f for _, f in out_of_region})}")

mixed = [(k, e) for k, e in sorted(ev.items()) if e["permitted"] > 0 and e["graded"] > 0]
print(f"mixed events (permitted>0 AND graded>0), excluded from the permitted bucket by "
      f"ruling (d): {len(mixed)}")
for k, e in mixed[:8]:
    print(f"   {k[0][:12]} {k[1].split('/')[-1]}: deleted={e['deleted']} "
          f"permitted={e['permitted']} graded={e['graded']} ungraded={e['ungraded']} "
          f"status={e['status']} only-file={k[1] in only_paths} arow={k[1] in arow_paths}")

names = {"restored": restored, "disclosed": disclosed, "exempt": valid_free,
         "permitted": permitted, "out_of_region": out_of_region}
pairwise = []
ks = list(names)
for i in range(len(ks)):
    for j in range(i + 1, len(ks)):
        inter = names[ks[i]] & names[ks[j]]
        if inter:
            pairwise.append((ks[i], ks[j], len(inter)))
print(f"pairwise overlaps among exact buckets: {pairwise if pairwise else 'NONE'}")
exact = restored | disclosed | valid_free | permitted | out_of_region
remainder = set(ev) - exact
print(f"remainder (must equal the accepted bucket): {len(remainder)} "
      f"vs accepted={g_bound['summary']['accepted']}  "
      f"match={len(remainder) == g_bound['summary']['accepted']}")
b = {"restored": len(restored), "disclosed": len(disclosed),
     "accepted": g_bound["summary"]["accepted"], "exempt": len(valid_free),
     "permitted": len(permitted), "out_of_region": len(out_of_region)}
print(f"buckets={b}")
print(f"sum={sum(b.values())} events={len(ev)} -> "
      f"{'EXACT PARTITION' if sum(b.values()) == len(ev) else 'MISMATCH'}")
print(f"plan arithmetic 95+5+53+56+28+4 = {95 + 5 + 53 + 56 + 28 + 4}")
