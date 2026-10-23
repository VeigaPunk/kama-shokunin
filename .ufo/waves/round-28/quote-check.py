#!/usr/bin/env python3
"""Round-28 quote check: does each quote occur in the pinned server-schema.cpp (whitespace-normalised)?
Checks (1) every data-seat quote in w1/out/DataG*/rows.json and (2) every Gate quote in
corpus/lessons/round-28.md. Prints one line per failure and a summary; exit 1 if any check fails."""
import glob, json, re, sys
from pathlib import Path
LANE = Path(__file__).resolve().parents[3]
snap = " ".join((LANE / ".ufo/waves/round-28/sources/llama.cpp-704366d/server-schema.cpp").read_text("utf-8").split())
bad = {"seat": 0, "gate": 0}
n = {"seat": 0, "gate": 0}
for p in sorted(glob.glob(str(LANE / ".ufo/waves/round-28/w1/out/DataG*/rows.json"))):
    for r in json.load(open(p)).get("rows", []):
        n["seat"] += 1
        q = " ".join(r["source"]["quote"].split())
        if q not in snap:
            bad["seat"] += 1
            print(f"seat-quote-not-verbatim {Path(p).parent.name} {r['field']}")
for line in (LANE / "corpus/lessons/round-28.md").read_text("utf-8").splitlines():
    m = re.match(r"^\| (S1[4-7]\d) \|.*?\| `(.*)` \(\d+ words\) \|", line)
    if m:
        n["gate"] += 1
        q = m.group(2).replace("/", "|")
        if q not in snap and m.group(2) not in snap:
            bad["gate"] += 1
            print(f"gate-quote-not-verbatim {m.group(1)}")
print(f"seat quotes {n['seat']} not-verbatim {bad['seat']}; gate quotes {n['gate']} not-verbatim {bad['gate']}")
sys.exit(1 if bad["gate"] else 0)
