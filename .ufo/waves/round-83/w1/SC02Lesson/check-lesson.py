#!/usr/bin/env python3
"""SC02Lesson gate: shape of the round-83 lesson draft against the frozen plan.

Read-only over the lane. Exit 0 only when every check holds; prints one line per check.
"""
from __future__ import annotations

import re
import sys

LANE = "/home/vgpnk/Projects/shokunin/kama-shokunin"
LESSON = f"{LANE}/.ufo/waves/round-83/w1/SC02Lesson/round-83.md"
PLAN = f"{LANE}/plans/round-83-claims.md"
DATE = "2026-11-04"

text = open(LESSON, encoding="utf-8").read()
plan = open(PLAN, encoding="utf-8").read()
lines = text.splitlines()
fail = 0
total = 0


def check(name, ok, detail=""):
    global fail, total
    total += 1
    print(f"{'PASS' if ok else 'FAIL'} {name}" + (f" {detail}" if detail else ""))
    if not ok:
        fail += 1


check("lesson-lines<=120", len(lines) <= 120, f"lines={len(lines)}")

headings = [line for line in lines if line.startswith("## ")]
check("section-order",
      headings == ["## Gate", "## Corrections", "## Mistakes", "## Frontier"],
      f"headings={headings}")
check("corrections-heading-exact",
      sum(1 for line in lines if line == "## Corrections") == 1)

gate = [line for line in lines if line.startswith("| S5")]
check("gate-rows=6", len(gate) == 6, f"rows={len(gate)}")
expected_ids = [f"S{n}" for n in range(566, 572)]
ids = [row.strip().strip("|").split("|")[0].strip() for row in gate]
check("gate-ids=S566..S571", ids == expected_ids, f"ids={ids}")
statuses = [row.strip().strip("|").split("|")[2].strip() for row in gate]
check("gate-status=200", statuses == ["200"] * 6, f"status={statuses}")
dates = [row.strip().strip("|").split("|")[8].strip() for row in gate]
check("gate-date-in-every-row", dates == [DATE] * 6, f"dates={dates}")
verdicts = [row.strip().strip("|").split("|")[6].strip() for row in gate]
check("gate-verdicts-are-verdicts",
      all(v in {"admit", "reject"} for v in verdicts), f"verdicts={verdicts}")
words = []
for row in gate:
    quote = row.strip().strip("|").split("|")[5].strip()
    words.append(len([w for w in re.split(r"\s+", quote) if w]))
check("gate-quote-words<=25", all(w <= 25 for w in words), f"words={words}")

block = re.findall(r"```\n(corrected F1 .*?)\n```", text, re.S)
plan_block = re.findall(r"```\n(corrected F1 .*?)\n```", plan, re.S)
check("corrections-block-present", len(block) == 1 and len(plan_block) == 1)
check("corrections-byte-equal-plan", block and plan_block and block[0] == plan_block[0])
check("corrections-lines=3", bool(block) and len(block[0].splitlines()) == 3,
      f"n={len(block[0].splitlines()) if block else 0}")
check("corrections-facts=F1..F3",
      bool(block) and [line.split()[1] for line in block[0].splitlines()] == ["F1", "F2", "F3"])
check("corrections-at-sealed",
      bool(block) and all("at=b1ba614b51255a3dcfe3e0946f32f8e31bd65c09" in line
                          for line in block[0].splitlines()))
check("corrections-date=" + DATE,
      bool(block) and all(f"date={DATE}" in line for line in block[0].splitlines()))

mistakes = [line for line in lines if line.startswith("| `caller-path-unbound`")]
check("mistakes-rows=1", len(mistakes) == 1, f"rows={len(mistakes)}")
check("mistakes-cells=4",
      bool(mistakes) and len(mistakes[0].strip().strip("|").split("|")) == 4)

check("frontier-assimilation-none", "Assimilation: none" in text)

print(f"SC02LESSON_GATE pass={total - fail} fail={fail}")
sys.exit(0 if fail == 0 else 1)
