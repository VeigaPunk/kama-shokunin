#!/usr/bin/env python3
"""N1: newrow_leg() row parser (0-3 leading spaces etc.) synthetic + real repo."""
import importlib.util
import sys

S = "/fast/scratch/hyaku/kama-r49/V1Counter"
OUT = open(f"{S}/out/newrow.txt", "w")

spec = importlib.util.spec_from_file_location(
    "r49c1", f"{S}/lane/tools/round49-replay-witness-audit.py")
cc = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cc)

def w(s=""):
    print(s)
    OUT.write(s + "\n")

# replicate the inner filter
def rows_filter(lines):
    out = set()
    for ln in lines.split("\n"):
        if ln.lstrip(" ")[:3] == "| S" and ln.lstrip(" ")[3:4].isdigit():
            out.add(ln)
    return out

sample = (
    "| S494 | https://raw.githubusercontent.com/x | /tokenize |\n"
    " | S495 | a | b |\n"
    "  | S496 | c | d |\n"
    "   | S497 | e | f |\n"
    "    | S498 | g | h |\n"          # 4 spaces
    "\t| S499 | i | j |\n"             # tab-indented
    "| S | not a row |\n"
    "|S500 | no space after pipe |\n"
    "| S1234 | four-digit id |\n"
    "## heading | S501 | inside heading |\n"
    "| S12a | id then letter |\n"
)
w("== synthetic parse ==")
for ln in sorted(rows_filter(sample)):
    w(f"  matched: {ln!r}")

w("\n== actual repo SOURCES.md row shapes (grep-style) ==")
import subprocess
p = subprocess.run(["git", "-C", f"{S}/lane", "show", "HEAD:corpus/SOURCES.md"],
                   capture_output=True)
if p.returncode == 0:
    for ln in p.stdout.decode("utf-8", "replace").split("\n"):
        if ln.lstrip(" ")[:3] == "| S" and ln.lstrip(" ")[3:4].isdigit():
            w(f"  {ln[:90]}")
else:
    w("  SOURCES.md missing at HEAD")

w("\n== newrow_leg() live run vs BASE on lane clone ==")
# use the clone HEAD; presentation-only, no mutation
tip = subprocess.run(["git", "-C", f"{S}/lane", "rev-parse", "HEAD"],
                     capture_output=True).stdout.decode().strip()
detail = []
hit = cc.newrow_leg(f"{S}/lane", tip, detail)
for x in detail:
    w(f"  {x}")
w(f"  hit={hit}")

OUT.close()
print("DONE")
