#!/usr/bin/env python3
"""Count one round-21 wave: spawned seats, report presence and first-line verdicts.

Usage: wave-accounting.py WAVE_DIR [--dead NAME=REASON ...]
Reads WAVE_DIR/spec.json and assignments.json; a seat's report is
advice/<Name>.md, else the first *.md under out/ whose path names the seat.
Writes WAVE_DIR/completion-summary.json and verdict-count.json.
"""
import collections
import json
from pathlib import Path
import re
import sys


def first_verdict(path):
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        m = re.search(r"VERDICT:?\**\s*\**\s*(confirm|partial|refute)", line,
                      re.I)
        if m:
            return m.group(1).lower()
    return "nonconformant"


def main():
    wave = Path(sys.argv[1])
    dead = dict(a.split("=", 1) for a in sys.argv[2:] if "=" in a)
    spec = json.loads((wave / "spec.json").read_text())
    assigned = json.loads((wave / "assignments.json").read_text())
    rows = []
    for item in spec["items"]:
        name = item["name"]
        report = wave / "advice" / f"{name}.md"
        if not report.is_file():
            hits = sorted(p for p in (wave / "out").rglob("*.md")
                          if name in str(p.relative_to(wave / "out")))
            report = hits[0] if hits else None
        rows.append({"name": name, "role": item["role"],
                     "agent": assigned.get(name),
                     "report": str(report.relative_to(wave)) if report else None,
                     "verdict": first_verdict(report) if report else None,
                     "dead": dead.get(name)})
    roles = collections.Counter(r["role"] for r in rows)
    verdicts = collections.Counter(r["verdict"] for r in rows if r["verdict"])
    summary = {"spawned": len(rows), "with_report": sum(bool(r["report"]) for r in rows),
               "dead": [r["name"] for r in rows if r["dead"]],
               "no_report": [r["name"] for r in rows if not r["report"]],
               "roles": dict(roles), "seats": rows}
    (wave / "completion-summary.json").write_text(json.dumps(summary, indent=1) + "\n")
    (wave / "verdict-count.json").write_text(json.dumps(dict(verdicts), indent=1) + "\n")
    print(json.dumps({k: v for k, v in summary.items() if k != "seats"}))
    print(json.dumps(dict(verdicts)))


if __name__ == "__main__":
    main()
