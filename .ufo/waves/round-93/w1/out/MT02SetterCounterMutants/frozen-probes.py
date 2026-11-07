#!/usr/bin/env python3
"""Frozen-counter false-green probes (no counter mutation).

Three forged sections the committed C2 battery does not exercise, graded by the frozen
counter at M2 exactly as a section author could write them:
  G1 non-literal overrides value     P09 value 'the parsed PORT' -> '8080'
  G2 non-arg.cpp scope cell          P36 scope -> '' (empty)
  G3 non-arg.cpp condition cell      P36 condition -> 'banana'
Each prints the counter's final SETTER_ROWS line; a bind is unbound=0 missing=0
duplicates=0 fabricated=0 and decisions_bound=2 with exit 1 (skill=override always 1).
"""
import re
import subprocess
import sys
from pathlib import Path

LANE = Path("/home/vgpnk/Projects/shokunin/kama-shokunin")
OUT = LANE / ".ufo/waves/round-93/w1/out/MT02SetterCounterMutants"
SCR = Path("/fast/scratch/hyaku/kama-r93/MT02SetterCounterMutants")
C = LANE / ".ufo/waves/round-93/controls"
BASE = "5af794958b0fc08f574aa2e67650282269549b02"

skill0 = subprocess.run(["git", "-C", str(LANE), "show", f"{BASE}:SKILL.md"],
                        capture_output=True, check=True).stdout.decode()
src0 = subprocess.run(["git", "-C", str(LANE), "show", f"{BASE}:corpus/SOURCES.md"],
                      capture_output=True, check=True).stdout.decode()
sec = (C / "c2-candidate-section.md").read_text()
srcs = src0 + (C / "c2-candidate-sources.md").read_text()


def row(text, rid):
    m = re.search(r"^\| " + rid + r" \|.*$", text, re.M)
    assert m, rid
    return m.group(0)


def cells(line):
    return [c.strip() for c in line.strip().strip("|").split("|")]


def put(text, rid, idx, val):
    old = row(text, rid)
    c = cells(old)
    c[idx] = val
    return text.replace(old, "| " + " | ".join(c) + " |")


PROBES = [
    ("G1", put(sec, "P09", 8, "8080"), "B5: non-literal overrides value only non-empty"),
    ("G2", put(sec, "P36", 5, ""), "B7 derived scope rule is arg.cpp-only"),
    ("G3", put(sec, "P36", 6, "banana"), "claim L1: non-arg.cpp condition is reviewer read"),
]
WORK = SCR / "probes"
WORK.mkdir(parents=True, exist_ok=True)
for pid, section, note in PROBES:
    sk = WORK / f"{pid}-SKILL.md"
    so = WORK / f"{pid}-SOURCES.md"
    sk.write_text(skill0 + "\n" + section)
    so.write_text(srcs)
    p = subprocess.run([sys.executable, str(OUT / "mutants/m2-counter.py"), "--repo", str(LANE), "--rev", BASE,
                        "--work", str(WORK / pid), "--archive", str(SCR / "b12177.tar.gz"),
                        "--skill-file", str(sk), "--sources-file", str(so)],
                       capture_output=True, text=True, cwd=str(LANE))
    final = [l for l in p.stdout.splitlines() if l.startswith("SETTER_ROWS population=")]
    unbound = [l for l in p.stdout.splitlines() if (" unbound " in l and l.startswith(("SETTER_ROW", "SETTER_DECISION")))]
    print(f"PROBE {pid} rc={p.returncode} note={note}")
    print(f"  {final[-1] if final else p.stdout[-400:]}")
    for u in unbound:
        print(f"  {u}")
