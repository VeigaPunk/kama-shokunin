#!/usr/bin/env python3
"""Per-event sections of ungraded SCORECARD lines at the measured tip (v3 semantics)."""
import importlib.util
import collections
import json
import sys

spec = importlib.util.spec_from_file_location(
    "aoa", "/home/vgpnk/Projects/shokunin/kama-shokunin/tools/append-only-audit.py")
aoa = importlib.util.module_from_spec(spec)
spec.loader.exec_module(aoa)

S = "/fast/scratch/hyaku/kama-r48/K1Regions"
repo = f"{S}/lane"
to = sys.argv[1] if len(sys.argv) > 1 else "380bcdff9c8af06997c482f6eb03db926a794a2b"

r = aoa.Repo(repo)
to_full = aoa._text(repo, "rev-parse", "--verify", to + "^{commit}").strip()

contract_text = aoa._text(repo, "show", f"{to_full}:{aoa.CONTRACT}")
rows = aoa.parse_contract(contract_text)
titles, prefixes = aoa.file_regions(rows, "SCORECARD.md")
print("SCORECARD exempt titles:", sorted(titles), "prefixes:", prefixes)

HEAD_TITLES = {"## Axes", "## Planned", "## Retired", "## Saturation", "## Capabilities"}

commits = []
for line in aoa._text(repo, "rev-list", "--topo-order", "--reverse", "--parents", to_full).split("\n"):
    parts = line.split()
    if parts:
        commits.append((parts[0], parts[1] if len(parts) > 1 else None))
cidx = {c: i for i, (c, _) in enumerate(commits)}

res = json.load(open(f"{S}/lane-v3.json"))
for ev in res["events"]:
    if ev["file"] != "SCORECARD.md":
        continue
    c, p = ev["commit"], dict(commits)[ev["commit"]]
    dl = aoa.deleted_lines(repo, p, c, "SCORECARD.md")
    pb = r.blobs([f"{p}:SCORECARD.md"])[f"{p}:SCORECARD.md"]
    psec = aoa.sections(r.list_lines(pb))
    pcount = r.section_counts(pb)
    window = commits[cidx[c]:]
    wb = r.blobs([f"{x}:SCORECARD.md" for x, _ in window])
    eligible = {t for t in titles if max(
        r.section_counts(wb[f"{x}:SCORECARD.md"])[t] if wb[f"{x}:SCORECARD.md"] else 0
        for x, _ in window) >= pcount[t]}
    ungraded_sec = collections.Counter()
    graded_sec = collections.Counter()
    sample = []
    for pos, text in dl:
        s = psec[pos - 1]
        if s in eligible:
            ungraded_sec[s] += 1
            if len(sample) < 5:
                sample.append((pos, s, text[:60]))
        else:
            graded_sec[s] += 1
    print(f"\nevent {c[:12]} deleted={len(dl)} graded={sum(graded_sec.values())} "
          f"ungraded={sum(ungraded_sec.values())}")
    print("  eligible:", sorted(eligible))
    print("  ungraded by section:", dict(ungraded_sec))
    print("  graded by section:", dict(graded_sec))
    nonhead = {s: n for s, n in ungraded_sec.items() if s not in HEAD_TITLES}
    print("  ungraded sections NOT in head titles:", nonhead)
    for pos, s, t in sample:
        print(f"    sample ungraded pos={pos} section={s!r} line={t!r}")
