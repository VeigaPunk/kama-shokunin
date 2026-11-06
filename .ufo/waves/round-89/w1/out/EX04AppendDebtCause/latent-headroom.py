#!/usr/bin/env python3
"""latent-headroom.py - how many lines of growth an exempt SCORECARD head can absorb before
a currently-graded deletion event becomes retroactively ungraded.

For every SCORECARD event the audit at <to> still grades, report the minimum over its deleted
lines in an exempt head title of `parent section count - max section count over the window`:
a positive value is the headroom the title currently has; when a later commit grows that title
by more than the headroom, the carve-out becomes eligible and the event's graded lines turn
ungraded (tools/append-only-audit.py:649-669), stranding any register row that accepted them.

Read-only. Usage: latent-headroom.py --repo DIR [--audit-json FILE] [--limit 10]
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import subprocess
import sys
from pathlib import Path

EXEMPT = ("## Axes", "## Planned", "## Retired", "## Saturation", "## Capabilities")


def load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--repo", default=".")
    ap.add_argument("--audit-json")
    ap.add_argument("--limit", type=int, default=10)
    args = ap.parse_args()
    repo = Path(args.repo).resolve()
    audit = load(repo / "tools/append-only-audit.py", "append_only_audit")
    if args.audit_json:
        data = json.loads(Path(args.audit_json).read_text(encoding="utf-8"))
    else:
        proc = subprocess.run([sys.executable, str(repo / "tools/append-only-audit.py"),
                               "--repo", str(repo), "--json"], capture_output=True, text=True)
        data = json.loads(proc.stdout)
    r = audit.Repo(str(repo))
    revs = subprocess.run(["git", "-C", str(repo), "rev-list", "--reverse", "HEAD"],
                          capture_output=True, text=True).stdout.split()
    index = {c: i for i, c in enumerate(revs)}
    counts = {}
    for c in revs:
        ref = f"{c}:SCORECARD.md"
        blob = r.blobs([ref]).get(ref)
        counts[c] = r.section_counts(blob) if blob else {}
    rows = []
    for event in data["events"]:
        if event["file"] != "SCORECARD.md" or event["graded"] == 0:
            continue
        commit = event["commit"]
        if commit not in index:
            continue
        parent = subprocess.run(["git", "-C", str(repo), "rev-parse", commit + "^"],
                                capture_output=True, text=True).stdout.strip()
        deleted = audit.deleted_lines(str(repo), parent, commit, "SCORECARD.md")
        ref = f"{parent}:SCORECARD.md"
        blob = r.blobs([ref])[ref]
        psec, pcount = audit.sections(r.list_lines(blob)), r.section_counts(blob)
        heads = []
        for pos, _text, _na in deleted:
            title = psec[pos - 1]
            if title in EXEMPT:
                top = max(counts[x].get(title, 0) for x in revs[index[commit]:])
                if pcount[title] > top:
                    heads.append(pcount[title] - top)
        if heads:
            rows.append((min(heads), commit, event["graded"]))
    rows.sort()
    for headroom, commit, graded in rows[:args.limit]:
        print(f"LATENT_HEADROOM headroom={headroom} event={commit} graded={graded}")
    print(f"LATENT_HEADROOM_TOTAL events={len(rows)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
