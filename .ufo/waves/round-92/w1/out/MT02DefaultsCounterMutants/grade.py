#!/usr/bin/env python3
"""grade.py - regrade the mutant runs on exit AND on the per-case SERVER_DEFAULTS line.

c1-mutbattery.py grades on exit only (the frozen claim's currency). A mutant whose row behaviour
changes but whose exit is masked by another predicate leg is invisible to that rule; this script
reports it as exit-masked. Classification per mutant:
  killed         - some case's exit differs from pristine (the assigned rule)
  exit-masked    - no exit change, but a case's SERVER_DEFAULTS/SERVER_DEFAULT line differs
  survived       - no observable change in any case (either equivalent or a coverage gap)
Usage: grade.py --work DIR
"""
import json, re, sys
from pathlib import Path

CASE_RE = re.compile(r"^CASE (\S+) exit=(\d+) want=\d+ ")
SUM_RE = re.compile(r"^  (SERVER_DEFAULT\S* .*)$", re.M)


def parse(text):
    out, cur = {}, None
    for line in text.splitlines():
        m = CASE_RE.match(line)
        if m:
            cur = m.group(1)
            out[cur] = {"exit": int(m.group(2)), "rows": []}
            continue
        s = SUM_RE.match(line)
        if s and cur:
            out[cur]["rows"].append(re.sub(r" rev=[0-9a-f]+", "", s.group(1)))
    return out


def main():
    work = Path(sys.argv[sys.argv.index("--work") + 1]).resolve()
    base = parse((work / "battery-pristine.log").read_text())
    res = json.loads((work / "results.json").read_text())
    rows = []
    for r in res["results"]:
        log = work / ("battery-" + Path(r["file"]).stem + ".log")
        got = parse(log.read_text()) if log.exists() else {}
        exit_diff = sorted(c for c in base if got.get(c, {}).get("exit") != base[c]["exit"])
        field_diff = sorted(c for c in base
                            if c in got and got[c]["rows"] != base[c]["rows"])
        cls = "killed" if exit_diff else ("exit-masked" if field_diff else "survived")
        rows.append((r["mutant"], cls, exit_diff, field_diff))
    print(f"{'mutant':44s} {'class':12s} exit_diff / field_diff")
    for name, cls, e, f in rows:
        print(f"{name:44s} {cls:12s} exit={e or '-'} fields={f or '-'}")
    k = sum(1 for r in rows if r[1] == "killed")
    m = sum(1 for r in rows if r[1] == "exit-masked")
    print(f"GRADE total={len(rows)} killed={k} exit_masked={m} survived={len(rows)-k-m}")


if __name__ == "__main__":
    main()
