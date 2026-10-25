#!/usr/bin/env python3
"""Round-38 C3 counter. The round-37 counting instruments become reproducible
from landed bytes.

Predicate (identical in the preregistration, this file, and the receipt):
tools/round37-statement-audit.py and tools/round37-coverage-audit.py exist at
the tip under tools/ and are absent at base
2a4a97dc890fe393035986c951797c5d65b6cc69; each exits 0 on --help; each exits 0
(met True) when re-run at the r37 tip against this repo; and the round-37
wave's 37th seat report (CriticEntries.md) and a parsed seat-exit-codes.json
covering all 37 members exist at the tip.

met is True only when found=2, help_ok=2, rerun_ok=2, report_37=1 and
receipt_ok=1.

Exit 0 when met is True, 1 when met is False, 2 on usage.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

PREDICATE = (
    "tools/round37-statement-audit.py and tools/round37-coverage-audit.py "
    "exist at the tip under tools/ and are absent at base "
    "2a4a97dc890fe393035986c951797c5d65b6cc69; each exits 0 on --help; each "
    "exits 0 (met True) when re-run at the r37 tip against this repo; and the "
    "round-37 wave's 37th seat report (CriticEntries.md) and a parsed "
    "seat-exit-codes.json covering all 37 members exist at the tip."
)
INSTRUMENTS = (
    "tools/round37-statement-audit.py",
    "tools/round37-coverage-audit.py",
)
BASE = "2a4a97dc890fe393035986c951797c5d65b6cc69"
R37_TIP = "2a4a97dc890fe393035986c951797c5d65b6cc69"
SEAT_REPORT = ".ufo/waves/round-37/w1/out/CriticEntries.md"
RECEIPT = ".ufo/waves/round-37/w1/out/seat-exit-codes.json"
EXPECTED_MEMBERS = 37


def git_show(repo: Path, rev: str, path: str) -> str | None:
    proc = subprocess.run(
        ["git", "-C", str(repo), "show", f"{rev}:{path}"],
        check=False,
        capture_output=True,
        text=True,
    )
    if proc.returncode != 0:
        return None
    return proc.stdout


def at_rev(repo: Path, rev: str, path: str) -> bool:
    proc = subprocess.run(
        ["git", "-C", str(repo), "cat-file", "-e", f"{rev}:{path}"],
        check=False, capture_output=True,
    )
    return proc.returncode == 0


def main() -> int:
    ap = argparse.ArgumentParser(description=PREDICATE)
    ap.add_argument("--repo", required=True, type=Path)
    ap.add_argument("--tip", required=True)
    args = ap.parse_args()
    found = sum(1 for i in INSTRUMENTS if at_rev(args.repo, args.tip, i))
    base_found = sum(1 for i in INSTRUMENTS if at_rev(args.repo, BASE, i))
    help_ok = 0
    rerun_ok = 0
    for i in INSTRUMENTS:
        p = args.repo / i
        if not p.exists():
            continue
        hp = subprocess.run([sys.executable, str(p), "--help"],
                            check=False, capture_output=True)
        if hp.returncode == 0:
            help_ok += 1
        rp = subprocess.run(
            [sys.executable, str(p), "--repo", str(args.repo),
             "--tip", R37_TIP],
            check=False, capture_output=True, text=True,
        )
        if rp.returncode == 0:
            rerun_ok += 1
    report_37 = 1 if at_rev(args.repo, args.tip, SEAT_REPORT) else 0
    receipt_ok = 0
    receipt_text = git_show(args.repo, args.tip, RECEIPT)
    if receipt_text is not None:
        try:
            data = json.loads(receipt_text)
            if isinstance(data, list) and len(data) == EXPECTED_MEMBERS:
                receipt_ok = 1
        except (json.JSONDecodeError, UnicodeDecodeError):
            pass
    met = (
        found == 2 and base_found == 0 and help_ok == 2 and rerun_ok == 2
        and report_37 == 1 and receipt_ok == 1
    )
    print(
        f"found {found} base_found {base_found} help_ok {help_ok} "
        f"rerun_ok {rerun_ok} report_37 {report_37} receipt_ok {receipt_ok} "
        f"met {str(met).lower()}"
    )
    return 0 if met else 1


if __name__ == "__main__":
    raise SystemExit(main())
