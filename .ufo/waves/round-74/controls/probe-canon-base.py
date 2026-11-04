#!/usr/bin/env python3
"""probe-canon-base.py — round-74 C1 control probe (the do-nothing state).

Runs the byte-frozen `tools/round42-selfdesc-reconcile.py`'s `canon()` over a fixture
SCORECARD.md and prints the resolution the r42 reconciler would grade — the hole the
round's v2 counter must close: demonstrated-capabilities tables newer than the newest
BOLD canonical heading are invisible to it.

    python3 probe-canon-base.py --repo <fixture-or-lane>

Prints one line: `BASE_C1 canon_round=<N> canon_rows=<c>`
Exit: 0 resolved; 2 could-not-evaluate (SCORECARD.md unreadable, module import failed).
"""

from __future__ import annotations

import argparse
import importlib.util
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
LANE = HERE.parents[3]


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", required=True)
    args = ap.parse_args(argv)

    scorecard = Path(args.repo) / "SCORECARD.md"
    if not scorecard.is_file():
        print("BASE_C1 error: {} unreadable".format(scorecard))
        return 2

    spec = importlib.util.spec_from_file_location(
        "r42recon", str(LANE / "tools" / "round42-selfdesc-reconcile.py"))
    module = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(module)
    except Exception as exc:  # could-not-evaluate, never a finding
        print("BASE_C1 error: r42 module import failed: {}".format(exc))
        return 2

    text = scorecard.read_text(encoding="utf-8", errors="replace")
    best, rows = module.canon(text)
    print("BASE_C1 canon_round={} canon_rows={}".format(best, len(rows)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
