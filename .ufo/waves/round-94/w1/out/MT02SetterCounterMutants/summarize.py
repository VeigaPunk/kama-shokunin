#!/usr/bin/env python3
"""Summarise saved receipts: baseline vs committed measured/c2.out, pristine met per
forgery, mutant met per (mutant, forge) pair, and the mutation table."""
import re
from pathlib import Path

OUT = Path(__file__).resolve().parent
RUNS = OUT / "runs"
COMMITTED = Path("/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-94/measured/c2.out")


def met(p: Path):
    t = p.read_text()
    m = re.search(r"SETTER_SWEEP .* met=(True|False)", t)
    return m.group(1) if m else "?"


t = (RUNS / "baseline.out").read_text()
print("baseline == committed c2.out:", t == COMMITTED.read_text(), "lines:", len(t.splitlines()))

print("\n== pristine on forgeries ==")
for p in sorted(RUNS.glob("forge-pri-*.md")):
    body = p.read_text()
    un = [l for l in body.splitlines() if l.startswith("SETTER_") and " unbound " in l]
    print(f"{p.name.replace('forge-pri-','').replace('.md',''):24s} met={met(p)} "
          + ("; ".join(un[:2]) if un else "(accepted)"))

print("\n== mutant on paired forgeries ==")
for p in sorted(RUNS.glob("forge-m*.out")):
    print(f"{p.name:48s} met={met(p)}")

print("\n== mutation table ==")
print((RUNS / "summary.tsv").read_text(), end="")

print("\n== forges applied ==")
print((RUNS / "forges.diff.txt").read_text(), end="")
