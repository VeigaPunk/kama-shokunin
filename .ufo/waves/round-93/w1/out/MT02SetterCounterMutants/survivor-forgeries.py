#!/usr/bin/env python3
"""Killing forgeries for the mutants the committed battery does not kill.

For every surviving mutant a single forgery of the candidate section is built. Each
forgery is graded twice:
  * frozen counter at M2 (mutants/m2-counter.py) must reject it with the named reason
    (so the check the mutant removes is load-bearing on this input);
  * the mutant must report the section green (`unbound=0 missing=0 duplicates=0
    fabricated=0 ... decisions_bound=2`, `derived_disagree=0`), i.e. the forged section
    would be accepted -- a false green the committed battery misses.
Cases F07/F11/F12 have no green forge: they are probed for what does/does not change.
"""
import os
import re
import subprocess
import sys
from pathlib import Path

LANE = Path("/home/vgpnk/Projects/shokunin/kama-shokunin")
OUT = LANE / ".ufo/waves/round-93/w1/out/MT02SetterCounterMutants"
SCR = Path("/fast/scratch/hyaku/kama-r93/MT02SetterCounterMutants")
C = LANE / ".ufo/waves/round-93/controls"
BASE = "5af794958b0fc08f574aa2e67650282269549b02"
ARCHIVE = SCR / "b12177.tar.gz"
WORK = SCR / "forgeries"

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


def sub(text, old, new):
    assert text.count(old) == 1, old
    return text.replace(old, new)


def drop_phrase(text, rid, phrase):
    old = row(text, rid)
    assert old.count(phrase) == 1, (rid, phrase)
    return text.replace(old, old.replace(phrase, ""))


dup = sub(sec, row(sec, "P12") + "\n", row(sec, "P12") + "\n" + row(sec, "P12") + "\n")
short = sub(sec, "\n".join(row(sec, f"P{i:02d}") for i in range(6, 49)) + "\n", "\n")

CASES = [
    # id, mutant, section, frozen reason the frozen counter must print, mutant must be green?
    ("F04", "04-text-substring", put(sec, "P09", 3, "`params.port`"), "P09 unbound text", True),
    ("F05", "05-source-check-removed", put(sec, "P09", 9, "S600"), "P09 unbound source", True),
    ("F07", "07-opt-index-last", None, "-", None),
    ("F08", "08-decision-names-removed",
     drop_phrase(sec, "R17", "P20 `--gpt-oss-20b-default` and "), "R17 unbound decision-names", True),
    ("F11", "11-min-pop-1", short, "rows=5", None),
    ("F12", "12-duplicate-removed", dup, "duplicates=1", None),
    ("F13", "13-unrelated-pairing-removed", put(sec, "P08", 7, "unrelated"), "P08 unbound unrelated-pairing", True),
    ("F14", "14-np-token-removed", put(sec, "P08", 4, "n_parallel"), "P08 unbound parameter-token", True),
    ("F16", "16-supersedes-removed", put(sec, "R16", 2, "R08"), "R16 unbound header", True),
    ("F17", "17-ex-condition-removed",
     sub(sec, "`ex == LLAMA_EXAMPLE_SERVER`", "`ex == LLAMA_EXAMPLE_EMBEDDING`"),
     "P01 unbound derived", True),
    ("F18", "18-value-empty-removed", put(sec, "P09", 8, "-"), "P09 unbound value-empty", True),
    ("F19", "19-effect-enum-removed", put(sec, "P02", 7, "declarez"), "P02 unbound effect-enum", True),
    ("F20", "20-param-enum-removed", put(sec, "P02", 4, "parallel"), "P02 unbound parameter-enum", True),
    ("F24", "24-decision-value-removed", put(sec, "R16", 3, "9999"), "R16 unbound value", True),
    ("F25", "25-value-dash-removed", put(sec, "P08", 8, "5"), "P08 unbound value-not-dash", True),
    ("F26", "26-condition-empty-removed", put(sec, "P36", 6, ""), "P36 unbound condition-empty", True),
]

TOTAL = "SETTER_ROWS population="
GREEN = ("unbound=0 missing=0 duplicates=0 fabricated=0", "decisions_bound=2", "derived_disagree=0")

WORK.mkdir(parents=True, exist_ok=True)
fails = 0
for fid, mid, section, reason, want_green in CASES:
    counter = OUT / f"mutants/{mid}.py"
    if section is None:
        print(f"FORGERY {fid} mutant={mid} no-forgery (arg_block sees 0 population blocks with >1 long option)")
        continue
    sk = WORK / f"{fid}-SKILL.md"
    so = WORK / f"{fid}-SOURCES.md"
    sk.write_text(skill0 + "\n" + section)
    so.write_text(srcs)
    line = {"frozen": None, "mutant": None}
    for tag, cpath in (("frozen", OUT / "mutants/m2-counter.py"), ("mutant", counter)):
        p = subprocess.run([sys.executable, str(cpath), "--repo", str(LANE), "--rev", BASE,
                            "--work", str(WORK / f"{fid}-{tag}"), "--archive", str(ARCHIVE),
                            "--skill-file", str(sk), "--sources-file", str(so)],
                           capture_output=True, text=True, cwd=str(LANE))
        final = [l for l in p.stdout.splitlines() if l.startswith(TOTAL)]
        unbound = [l for l in p.stdout.splitlines() if l.startswith("SETTER_ROW ") and " unbound " in l]
        unbound += [l for l in p.stdout.splitlines() if l.startswith("SETTER_DECISION ") and " unbound " in l]
        line[tag] = final[-1] if final else f"<no {TOTAL} line> rc={p.returncode} {p.stdout[-300:]}"
        if tag == "frozen":
            okf = p.returncode == 1 and reason in line[tag] + " " + " ".join(unbound)
            print(f"FORGERY {fid} frozen  rc={p.returncode} reason_ok={int(okf)} :: {line[tag]}")
            for u in unbound:
                print(f"    {u}")
            fails += 0 if okf else 1
        else:
            green = all(g in line[tag] for g in GREEN)
            okm = (green if want_green else True) and p.returncode == 1
            print(f"FORGERY {fid} {mid} rc={p.returncode} green={int(green)} as_expected={int(okm)} :: {line[tag]}")
            fails += 0 if okm else 1

print(f"MT02_FORGERIES total={len(CASES)} failures={fails}")
sys.exit(0 if fails == 0 else 1)
