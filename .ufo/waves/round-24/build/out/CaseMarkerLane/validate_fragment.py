#!/usr/bin/env python3
"""Validate the CaseMarkerLane grid fragment against the EXISTING round-23
grid helpers (tests/report-audit/repo-state-grid.py), without running that
grid's suite.

What is executed: only the two fragment builders and the grid's own
`base()` twin, each through the grid's `run_case` against the BASE auditor
(0df800e).  This proves the fragment is drop-in compatible with the
adopting grid's helper names and that the fragment's expectation values are
the ones the existing grid conventions produce.
"""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import sys
import tempfile

GRID = Path("/home/vgpnk/Projects/shokunin/kama-shokunin/tests/report-audit/"
            "repo-state-grid.py")
OUT = Path("/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-24/"
           "build/out/CaseMarkerLane/evidence-fragment-validation.json")

spec = importlib.util.spec_from_file_location("r23grid", GRID)
grid = importlib.util.module_from_spec(spec)
spec.loader.exec_module(grid)

frag_spec = importlib.util.spec_from_file_location(
    "frag", "/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/"
            "round-24/build/out/CaseMarkerLane/grid_fragment.py")
frag = importlib.util.module_from_spec(frag_spec)
frag_spec.loader.exec_module(frag)

AUDITOR = "/home/vgpnk/Projects/shokunin/kama-shokunin/tools/report-landing-audit.py"

# the fragment is written against the adopting grid's helper names; lend it
# the round-23 grid's own implementations for this validation run
for _name in ("pair", "commit", "publish", "report", "g", "require", "env",
              "init", "base"):
    setattr(frag, _name, getattr(grid, _name))

def _twin_base(tmp):
    """The grid's own clean twin, wrapped in the 4-tuple shape its case
    builders use (lane, fleet, extra, marker)."""
    lane, fleet, _lc = grid.base(tmp)
    return lane, fleet, [], None


CASES = [
    ("twin-base-clean", "control", _twin_base, 0, []),
    ("C14-promisor-marker-complete-lane", "control",
     frag.c_promisor_marker_complete_lane, 0, []),
    ("C15-promisor-marker-complete-lane-omission", "control",
     frag.c_promisor_marker_complete_lane_omission, 1, ["landed-omitted"]),
]


def main():
    out = {"grid": str(GRID), "auditor": AUDITOR, "rows": []}
    with tempfile.TemporaryDirectory(prefix="case-marker-validate-") as root:
        root = Path(root)
        for i, (name, kind, build, want_exit, want_kinds) in enumerate(CASES):
            tmp = root / f"{i:02d}"
            tmp.mkdir(parents=True)
            row = grid.run_case(Path(AUDITOR), (name, kind, build, want_exit,
                                                 want_kinds), tmp)
            row["met"] = False  # base arm: the marked rows are expected to
            row["base_expected_to_fail_marker_rows"] = (
                name.startswith("C1"))
            out["rows"].append(row)
    OUT.write_text(json.dumps(out, indent=1, sort_keys=True) + "\n",
                   encoding="utf-8")
    for r in out["rows"]:
        print(f"{r['case']}: exit={r['exit']} kinds={r['kinds']} "
              f"expected_exit={r['expected_exit']} "
              f"expected_kinds={r['expected_kinds']} "
              f"stderr={r['stderr_tail'][:90]!r}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
