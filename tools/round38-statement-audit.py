#!/usr/bin/env python3
"""Round-38 C1 counter. The R36-D2 third sub-fact correction, by append only.

Predicate (identical in the preregistration, this file, and the receipt):
A round-36 verifier routed statement (D2 third sub-fact) is corrected iff
corpus/lessons/round-38.md contains a correction row naming R36-D2C, the
counter re-derives the cited committed-byte fact (the five staged rows
S332/S336/S337/S338/S339 exist in the read-only package at the named lines),
the row carries no wrong-id restatement that its own statement forbids, and
the r37 lesson blob and the r37 fleet report blob are unchanged.

Exit 0 when met is True, 1 when met is False, 2 on usage.
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

PREDICATE = (
    "A round-36 verifier routed statement (D2 third sub-fact) is corrected iff "
    "corpus/lessons/round-38.md contains a correction row naming R36-D2C, the "
    "counter re-derives the cited committed-byte fact (the five staged rows "
    "S332/S336/S337/S338/S339 exist in the read-only package at the named "
    "lines), the row carries no wrong-id restatement that its own statement "
    "forbids, and the r37 lesson blob and the r37 fleet report blob are "
    "unchanged."
)
ROW_ID = "R36-D2C"
NEED = ("S332", "S336", "S337", "S338", "S339")
WRONG = ("S331", "S334")
BASE = "2a4a97dc890fe393035986c951797c5d65b6cc69"
LESSON_BLOB = "20f7909b6c8161f2bcc868a4472585733c81ae83"
REPORT_BLOB = "1c6ea9faa0e25d48f70d354e0a140bcb709ca7db"
FLEET = Path("/home/vgpnk/Projects/shokunin")
STAGED = Path("/home/vgpnk/Projects/shokuknow/merge/kama/SOURCES.append.md")
STAGED_LINES = (9, 13, 14, 15, 16)


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


def git_blob(repo: Path, rev: str, path: str) -> str | None:
    proc = subprocess.run(
        ["git", "-C", str(repo), "rev-parse", f"{rev}:{path}"],
        check=False,
        capture_output=True,
        text=True,
    )
    if proc.returncode != 0:
        return None
    return proc.stdout.strip()


def staged_rows_ok() -> tuple[bool, str]:
    """Five staged rows at the named lines carry the five ids."""
    if not STAGED.exists():
        return False, "staged package missing"
    try:
        lines = STAGED.read_text(encoding="utf-8").splitlines()
    except OSError:
        return False, "staged package unreadable"
    found: set[str] = set()
    for ln in STAGED_LINES:
        if ln > len(lines):
            return False, f"staged line {ln} missing"
        line = lines[ln - 1]
        m = re.search(r"\b(S[0-9]{3,})\b", line)
        if not m:
            return False, f"staged line {ln} carries no id"
        found.add(m.group(1))
    missing = set(NEED) - found
    if missing:
        return False, f"missing staged ids: {sorted(missing)}"
    return True, "staged rows present"


def evaluate(repo: Path, tip: str) -> dict:
    lesson = git_show(repo, tip, "corpus/lessons/round-38.md")
    if lesson is None:
        return dict(uncorrected=1, false_corrections=0, lesson_unchanged=1,
                    report_unchanged=1, met=False)
    rows = [ln for ln in lesson.splitlines() if ROW_ID in ln]
    uncorrected = 1 if not rows else 0
    row = "\n".join(rows)
    wrong_hits = [w for w in WRONG if re.search(r"\b" + re.escape(w) + r"\b", row)]
    false_corrections = 1 if wrong_hits else 0
    has_all = all(re.search(r"\b" + re.escape(n) + r"\b", row) for n in NEED)
    staged_ok, staged_note = staged_rows_ok()
    lesson_blob = git_blob(repo, tip, "corpus/lessons/round-37.md")
    report_blob = git_blob(FLEET, "HEAD", ".ufo/reports/round-37/kama.md")
    lesson_unchanged = 1 if lesson_blob == LESSON_BLOB else 0
    report_unchanged = 1 if report_blob == REPORT_BLOB else 0
    met = (
        uncorrected == 0
        and false_corrections == 0
        and has_all
        and staged_ok
        and lesson_unchanged == 1
        and report_unchanged == 1
    )
    return dict(uncorrected=uncorrected, false_corrections=false_corrections,
                lesson_unchanged=lesson_unchanged, report_unchanged=report_unchanged,
                met=met, staged_note=staged_note)


def main() -> int:
    ap = argparse.ArgumentParser(description=PREDICATE)
    ap.add_argument("--repo", required=True, type=Path)
    ap.add_argument("--tip", required=True)
    args = ap.parse_args()
    r = evaluate(args.repo, args.tip)
    note = r.get("staged_note", "")
    print(
        f"uncorrected {r['uncorrected']} false_corrections {r['false_corrections']} "
        f"lesson_unchanged {r['lesson_unchanged']} report_unchanged {r['report_unchanged']} "
        f"met {str(r['met']).lower()}"
    )
    if note:
        print(f"note: {note}")
    return 0 if r["met"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
