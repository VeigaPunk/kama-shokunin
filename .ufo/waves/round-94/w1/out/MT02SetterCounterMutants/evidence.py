#!/usr/bin/env python3
"""Final receipt table: every pristine forgery rejection reason and every mutant met."""
import re
from pathlib import Path

OUT = Path(__file__).resolve().parent
RUNS = OUT / "runs"


def met(p: Path):
    t = p.read_text()
    m = re.search(r"SETTER_SWEEP .* met=(True|False)", t)
    return m.group(1) if m else "?"


def unbound(p: Path):
    return [l for l in p.read_text().splitlines()
            if " unbound " in l and (l.startswith("SETTER_ROW") or l.startswith("SETTER_DECISION"))]


print("== pristine verdict on every forged input ==")
for p in sorted(RUNS.glob("forge-pri-*.out")):
    name = p.name[len("forge-pri-"):-len(".out")]
    print(f"{name:24s} met={met(p):5s} " + ("; ".join(unbound(p)[:2]) if unbound(p) else "(no unbound row)"))

print("\n== extra probes ==")
for p in sorted(RUNS.glob("forge-pri-*.md")):
    print(f"{p.name:24s} met={met(p):5s} " + "; ".join(unbound(p)[:2]))
for p in sorted(RUNS.glob("forge-m*-*.md")):
    pass

print("\n== m26 duplicate-row evidence ==")
t = (RUNS / "forge-m26-f20_duplicate_row.out").read_text()
for l in t.splitlines():
    if l.startswith("SETTER_DECISION") or l.startswith("SETTER_SWEEP") or "P93" in l:
        print(l)
print("--- pristine on same input ---")
t = (RUNS / "forge-pri-f20_duplicate_row.out").read_text()
for l in t.splitlines():
    if l.startswith("SETTER_SWEEP") or "P93" in l:
        print(l)

print("\n== baseline vs committed ==")
print((RUNS / "baseline.out").read_text() ==
      Path("/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-94/measured/c2.out").read_text())
