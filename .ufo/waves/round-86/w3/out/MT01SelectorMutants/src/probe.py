#!/usr/bin/env python3
"""Selector-vs-contract probes (no source mutation).  Usage: probe.py <instrument.py> <p1|p2>
p1: the FIRST `## Axes` section carries no `| calibration |` row; a LATER `## Axes` section does.
    Frozen C1 population 2 says the row must be inside the FIRST `## Axes` section -> must be red.
p2: the first top-level authority cell is stale-by-construction (round 84 banner) and a SECOND
    top-level banner below it is correct -> frozen clause 1 says the first cell is the live cell,
    so the document must be red.
"""
import importlib.util
import sys

path, case = sys.argv[1], sys.argv[2]
spec = importlib.util.spec_from_file_location("inst", path)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

if case == "p1":
    tree = mod.fixture(stale_live=False)
    score = tree.files["SCORECARD.md"]
    # move the calibration row out of the first Axes section into a second one
    tree.files["SCORECARD.md"] = score.replace(
        mod.GOOD_ROW + "\n", "") + "\n## Axes\n\n" + mod.GOOD_ROW + "\n"
else:
    tree = mod.fixture(stale_live=False)
    live = tree.files["SCORECARD.md"]
    stale = ("**Current authority (round 84):** Latest measured round: 84. Terminal gate measured at "
             f"`{mod.A}`: `python3 tools/pre-report-gate.py --repo . --round 84 --tip master` printed "
             "`PRE_REPORT round=84 arms=13 failed=0 uncommitted=0`, exit0; receipt "
             "`.ufo/waves/round-84/measured/after/gate-final-green.out`.")
    tree.files["SCORECARD.md"] = live.replace("## Axes\n\n", "## Axes\n\n" + stale + "\n", 1)

try:
    result = mod.grade(tree)
    print(mod.render(result))
    for fact, detail in result["findings"]:
        print(f"RENDERED_CELLS_FINDING {fact} {detail}")
    print(f"exit={0 if result['mismatches'] == 0 else 1}")
except mod.CouldNotEvaluate as exc:
    print(f"could-not-evaluate: {exc}")
    print("exit=2")
