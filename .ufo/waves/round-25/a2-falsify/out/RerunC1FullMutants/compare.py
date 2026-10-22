#!/usr/bin/env python3
"""Compare the re-run isolation mutant JSON against the committed one.

Usage: compare.py <rerun.json> <committed.json> [out.md]
Exit 0 when identical, 1 when any difference is found.
"""
import hashlib
import json
import sys

rerun_path, committed_path = sys.argv[1], sys.argv[2]
out_path = sys.argv[3] if len(sys.argv) > 3 else None

rerun = json.load(open(rerun_path))
committed = json.load(open(committed_path))

lines = []
diffs = []

lines.append("# Diff table: re-run at fa3b62ae vs committed c1-tip-mutants.json\n")
lines.append("")
lines.append("| item | committed | re-run | same |")
lines.append("|---|---|---|---|")


def add(item, a, b):
    same = "yes" if a == b else "NO"
    if a != b:
        diffs.append((item, a, b))
    lines.append(f"| {item} | {a} | {b} | {same} |")


add("pristine", committed.get("pristine"), rerun.get("pristine"))
add("mutants", committed.get("mutants"), rerun.get("mutants"))
add("killed", committed.get("killed"), rerun.get("killed"))
add("surviving", committed.get("surviving"), rerun.get("surviving"))
add("retired", committed.get("retired"), rerun.get("retired"))
add("retired_detail", json.dumps(committed.get("retired_detail"), sort_keys=True),
    json.dumps(rerun.get("retired_detail"), sort_keys=True))

crows = {r["mutant"]: r for r in committed.get("rows", [])}
rrows = {r["mutant"]: r for r in rerun.get("rows", [])}
lines.append("")
lines.append("## Per-mutant rows\n")
lines.append("")
lines.append("| mutant | committed killed | re-run killed | committed grid_exit | re-run grid_exit | committed failed_rows | re-run failed_rows | same |")
lines.append("|---|---|---|---|---|---|---|---|")

for name in sorted(set(crows) | set(rrows)):
    c = crows.get(name, {})
    r = rrows.get(name, {})
    same = (c.get("killed") == r.get("killed")
            and c.get("grid_exit") == r.get("grid_exit")
            and c.get("failed_rows") == r.get("failed_rows")
            and c.get("error") == r.get("error"))
    if not same:
        diffs.append((f"row:{name}",
                      (c.get("killed"), c.get("grid_exit"), c.get("failed_rows"), c.get("error")),
                      (r.get("killed"), r.get("grid_exit"), r.get("failed_rows"), r.get("error"))))
    lines.append(
        f"| {name} | {c.get('killed')} | {r.get('killed')} | "
        f"{c.get('grid_exit')} | {r.get('grid_exit')} | "
        f"{c.get('failed_rows')} | {r.get('failed_rows')} | "
        f"{'yes' if same else 'NO'} |")

lines.append("")
lines.append("## Verdict")
lines.append("")
lines.append(f"differences: {len(diffs)}")
for item, a, b in diffs:
    lines.append(f"- {item}: committed={a!r} rerun={b!r}")
lines.append("")
lines.append("## sha256")
lines.append("")
lines.append(f"- committed {committed_path}: {hashlib.sha256(open(committed_path,'rb').read()).hexdigest()}")
lines.append(f"- re-run    {rerun_path}: {hashlib.sha256(open(rerun_path,'rb').read()).hexdigest()}")

text = "\n".join(lines) + "\n"
if out_path:
    with open(out_path, "w") as fh:
        fh.write(text)
print(text)
sys.exit(1 if diffs else 0)
