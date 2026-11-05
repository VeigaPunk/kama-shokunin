#!/usr/bin/env python3
"""Counterexamples for the two surviving C1 selector mutants (MD paragraph coupling,
ME row first-wins).  Usage: demo.py <instrument.py> <case:md|me>
Builds a DictTree fixture that the frozen contract must grade RED and prints the graded line."""
import importlib.util
import pathlib
import sys

path, case = sys.argv[1], sys.argv[2]
spec = importlib.util.spec_from_file_location("inst", path)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

if case == "md":
    # Banner carries revision + command + receipt path but NO token; the token lives in a
    # separate rendered paragraph.  Frozen clause 1 is ONE coupled assertion -> must be red.
    tree = mod.fixture(stale_live=False, token="")
    tree.files["SCORECARD.md"] += (
        "\nA later paragraph: `PRE_REPORT round=85 arms=13 failed=1 uncommitted=0`\n")
else:
    # First top-level calibration row is stale, a later duplicate names round-85.  Frozen:
    # "the FIRST top-level `| calibration |` row" -> must be red.
    tree = mod.fixture(stale_live=False, row=mod.STALE_ROW + "\n" + mod.GOOD_ROW)

try:
    result = mod.grade(tree)
    print(mod.render(result))
    for fact, detail in result["findings"]:
        print(f"RENDERED_CELLS_FINDING {fact} {detail}")
    print(f"exit={0 if result['mismatches'] == 0 else 1}")
except mod.CouldNotEvaluate as exc:
    print(f"could-not-evaluate: {exc}")
    print("exit=2")
