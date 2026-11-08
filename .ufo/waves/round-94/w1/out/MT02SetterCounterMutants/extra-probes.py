#!/usr/bin/env python3
"""Extra probes for the three control-survivors that had no paired forgery (m20/m25/m29),
plus a 92-row duplicate-swap input for m26. Imports the harness for forge()/run()."""
import importlib.util
import sys
from pathlib import Path

OUT = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("mr", OUT / "mutation-run.py")
mr = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mr)

f20b = mr.forge("f20b_dup_swap_92rows", [("copyrow", "P01", "P19")])
f21 = mr.forge("f21_missing_row", [("insert", "P01", "@@DROP@@")])
# f21: actually delete the P01 row.
lines = f21.read_text().split("\n")
lines = [l for l in lines if l.strip() != "@@DROP@@"]
mr.find_row(lines, "P02")  # sanity: section still parses
# remove the P01 line
lines = [l for l in lines if not l.startswith("| P01 |")]
f21.write_text("\n".join(lines))

cases = [
    ("m26", f20b), ("m29", f20b), ("m29", mr.FORGE / "f20_duplicate_row.md"),
    ("m29", f21), ("m25", f21),
]
pris = {}
for name in {c[1].name for c in cases}:
    rc, out = mr.run(mr.PRISTINE, mr.FORGE / name, mr.SOURCES, "x")
    (OUT / "runs" / f"forge-pri-{name}").write_text(out)
    pris[name] = (rc, mr.met_of(out), out)
for mid, p in cases:
    rc, out = mr.run(OUT / "mutants" / f"{mid}.py", p, mr.SOURCES, f"x-{mid}")
    (OUT / "runs" / f"forge-{mid}-{p.name}").write_text(out)
    print(f"{mid} on {p.name}: mutant_rc={rc} mutant_met={mr.met_of(out)} pristine_met={pris[p.name][1]}")
    for l in out.splitlines():
        if l.startswith("SETTER_SWEEP") or ("unbound" in l and l.startswith("SETTER")):
            print("   ", l)
print("pristine on f20b:", pris["f20b_dup_swap_92rows.md"][1], "on f21:", pris["f21_missing_row.md"][1])
