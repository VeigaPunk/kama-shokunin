#!/usr/bin/env python3
"""Bounded behavioral detector for the R36-D1 leg of the C1 counter.

Usage: d1_harness.py <counter.py> <row.md> {committed|ondisk}

committed : census bytes come from git_show at tip (what the counter really does)
ondisk    : census bytes come from the working-tree file (counter does NOT do this)

Read-only with respect to the lane repo: it only calls the counter's own
load_facts()/holds()/score() and prints what they return.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

REPO = Path("/home/vgpnk/Projects/shokunin/kama-shokunin")
BASE = "6a4afdfe48b0b54239d127761d21a5cf21b5b0ea"
CENSUS_REL = ".ufo/waves/round-36/census-end.out"


def load(path: Path):
    spec = importlib.util.spec_from_file_location("counter_under_test", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def main() -> int:
    counter_path, row_path, mode = Path(sys.argv[1]), Path(sys.argv[2]), sys.argv[3]
    tip = sys.argv[4] if len(sys.argv) > 4 else BASE
    m = load(counter_path)
    append, census_tip, census_base, exitcodes, seatlogs, lesson_blob, report_blob = m.load_facts(REPO, tip)
    row = row_path.read_text(encoding="utf-8")
    ondisk = (REPO / CENSUS_REL).read_text(encoding="utf-8")
    ctip = census_tip if mode == "committed" else ondisk

    d1 = m.holds(
        "R36-D1", row,
        append=append, census_tip=ctip, census_base=census_base,
        exitcodes=exitcodes, seatlogs=seatlogs,
    )
    forb = m.forbidden_in("R36-D1", row)
    full = m.score(
        row,
        append=append, census_tip=ctip, census_base=census_base,
        exitcodes=exitcodes, seatlogs=seatlogs,
        lesson_blob=lesson_blob, report_blob=report_blob,
    )
    print(f"mode={mode}")
    print(f"census_tip_from_git={census_tip is not None} census_base_from_git={census_base is not None}")
    print(f"D1_holds={d1} forbidden={forb!r}")
    print("full_score " + m.emit(full))
    return 0 if d1 else 1


if __name__ == "__main__":
    sys.exit(main())
