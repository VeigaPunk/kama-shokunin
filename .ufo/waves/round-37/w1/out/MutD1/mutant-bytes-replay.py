#!/usr/bin/env python3
"""Round-37 C1 counter. Routed r36-spotcheck statements, corrected by append only.

Predicate (identical in the preregistration, this file, and the receipt):
A frozen r36-spotcheck routed statement is corrected iff corpus/lessons/round-37.md
contains a correction row naming its id, the counter re-derives the cited
committed-byte fact, the row carries no wrong-id restatement that its own
statement forbids, and the r36 lesson blob and the r36 fleet report blob are
unchanged.

Exit 0 when met is True, 1 when met is False, 2 on usage.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

PREDICATE = (
    "A frozen r36-spotcheck routed statement is corrected iff "
    "corpus/lessons/round-37.md contains a correction row naming its id, the "
    "counter re-derives the cited committed-byte fact, the row carries no "
    "wrong-id restatement that its own statement forbids, and the r36 lesson "
    "blob and the r36 fleet report blob are unchanged."
)
IDS = ("R36-D1", "R36-D2A", "R36-D2B", "R36-D3")
BASE = "6a4afdfe48b0b54239d127761d21a5cf21b5b0ea"
LESSON_BLOB = "6fb1ec151407b1207e8d540e83ba87d6a909d8ea"
REPORT_BLOB = "8b7408e663c1b1ea95826d240f498637f1961604"
FLEET = Path("/home/vgpnk/Projects/shokunin")
SHOKUKNOW = Path("/home/vgpnk/Projects/shokuknow/merge/kama/SOURCES.append.md")
CENSUS_PATH = ".ufo/waves/round-36/census-end.out"
EXITCODES_PATH = ".ufo/waves/round-36/w3/out/seat-exit-codes.json"
SEATLOGS = (
    ".ufo/waves/round-36/w3/out/ScribeLog/seat.log",
    ".ufo/waves/round-36/w3/out/RevQ206/seat.log",
)


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


def staged_url(append: str, sid: str) -> str | None:
    for line in append.splitlines():
        if line.lstrip().startswith(f"| {sid} "):
            cells = line.split("|")
            if len(cells) >= 3:
                return cells[2]
    return None


def rows_of(lesson: str) -> dict[str, str]:
    found: dict[str, str] = {}
    for line in lesson.splitlines():
        for sid in IDS:
            if sid + ":" in line:
                found[sid] = line
    return found


def forbidden_in(sid: str, row: str) -> str | None:
    """Wrong-id restatements a correction row must not carry."""
    if sid == "R36-D1":
        return None
    if sid == "R36-D2A":
        return None
    if sid == "R36-D2B":
        for bad in ("S359", "S360", "S372", "S391"):
            if bad in row:
                return bad
        return None
    if sid == "R36-D3":
        for bad in ("rc=0", "rc=143"):
            if bad in row:
                return bad
        return None
    return "unknown"


def holds(
    sid: str,
    row: str,
    *,
    append: str,
    census_tip: str | None,
    census_base: str | None,
    exitcodes: str,
    seatlogs: str,
) -> bool:
    if sid == "R36-D1":
        return (
            census_base is None
            and "kama\tok" in (census_tip or row)
            and CENSUS_PATH in row
        )
    if sid == "R36-D2A":
        url371 = staged_url(append, "S371") or ""
        url366 = staged_url(append, "S366") or ""
        return (
            "native_api.mdx" in url371
            and "native_api.mdx" not in url366
            and "S371" in row
            and "native_api" in row
            and "miswritten" in row
        )
    if sid == "R36-D2B":
        ok = all("http_server.py" in (staged_url(append, s) or "") for s in ("S364", "S365", "S377", "S396"))
        return (
            ok
            and "http_server.py" in row
            and all(s in row for s in ("S364", "S365", "S377", "S396"))
        )
    if sid == "R36-D3":
        need = (
            '"name": "ScribeLog"' in exitcodes and '"name": "RevQ206"' in exitcodes
        )
        rc1 = exitcodes.count('"rc": 1') >= 2
        rate = "rate_limit" in seatlogs and "429" in seatlogs
        return (
            need
            and rc1
            and rate
            and "ScribeLog" in row
            and "RevQ206" in row
            and "429" in row
        )
    return False


def score(
    lesson: str,
    *,
    append: str,
    census_tip: str | None,
    census_base: str | None,
    exitcodes: str,
    seatlogs: str,
    lesson_blob: str | None,
    report_blob: str | None,
) -> dict[str, int]:
    rows = rows_of(lesson)
    uncorrected = 0
    false_corrections = 0
    for sid in IDS:
        row = rows.get(sid)
        if row is None:
            uncorrected += 1
            continue
        bad = forbidden_in(sid, row)
        if bad is not None or not holds(
            sid, row,
            append=append, census_tip=census_tip, census_base=census_base,
            exitcodes=exitcodes, seatlogs=seatlogs,
        ):
            false_corrections += 1
    lesson_unchanged = 1 if lesson_blob == LESSON_BLOB else 0
    report_unchanged = 1 if report_blob == REPORT_BLOB else 0
    met = (
        uncorrected == 0
        and false_corrections == 0
        and lesson_unchanged == 1
        and report_unchanged == 1
    )
    return {
        "uncorrected": uncorrected,
        "false_corrections": false_corrections,
        "lesson_unchanged": lesson_unchanged,
        "report_unchanged": report_unchanged,
        "met": int(met),
    }


def emit(result: dict[str, int]) -> str:
    met = "True" if result["met"] else "False"
    return (
        f"uncorrected {result['uncorrected']} "
        f"false_corrections {result['false_corrections']} "
        f"lesson_unchanged {result['lesson_unchanged']} "
        f"report_unchanged {result['report_unchanged']} met {met}"
    )


def load_facts(repo: Path, tip: str) -> tuple[str, str | None, str | None, str, str, str | None, str | None]:
    append = SHOKUKNOW.read_text(encoding="utf-8")
    census_tip = git_show(repo, tip, CENSUS_PATH)
    census_base = git_show(repo, BASE, CENSUS_PATH)
    exitcodes = git_show(repo, tip, EXITCODES_PATH) or ""
    seatlogs = "".join(
        (git_show(repo, tip, p) or "") for p in SEATLOGS
    )
    return (
        append,
        census_tip,
        census_base,
        exitcodes,
        seatlogs,
        git_blob(repo, tip, "corpus/lessons/round-36.md"),
        git_blob(FLEET, "HEAD", ".ufo/reports/round-36/kama.md"),
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", type=Path, required=True)
    parser.add_argument("--tip", required=True)
    parser.add_argument("--selftest", action="store_true")
    args = parser.parse_args()
    facts = load_facts(args.repo, args.tip)
    if args.selftest:
        empty = score(
            "",
            append=facts[0], census_tip=facts[1], census_base=facts[2],
            exitcodes=facts[3], seatlogs=facts[4],
            lesson_blob=facts[5], report_blob=facts[6],
        )
        good_census = "kama\tW04\tx\nkama\tok\t/home/vgpnk/Projects/shokunin/kama-shokunin/corpus/SOURCES.md\n"
        bad_row = (
            "R36-D1: .ufo/waves/round-36/census-end.out\n"
            "R36-D2A: S371 native_api miswritten\n"
            "R36-D2B: http_server.py S364 S365 S377 S396 S359\n"
            "R36-D3: ScribeLog RevQ206 429\n"
        )
        bad = score(
            bad_row,
            append=facts[0], census_tip=good_census, census_base=facts[2],
            exitcodes=facts[3], seatlogs=facts[4],
            lesson_blob=facts[5], report_blob=facts[6],
        )
        good_row = (
            "R36-D1: .ufo/waves/round-36/census-end.out\n"
            "R36-D2A: S371 native_api miswritten\n"
            "R36-D2B: http_server.py S364 S365 S377 S396\n"
            "R36-D3: ScribeLog RevQ206 429\n"
        )
        good = score(
            good_row,
            append=facts[0], census_tip=good_census, census_base=facts[2],
            exitcodes=facts[3], seatlogs=facts[4],
            lesson_blob=facts[5], report_blob=facts[6],
        )
        empty_ok = empty["met"] == 0 and empty["uncorrected"] == 4
        bad_ok = bad["met"] == 0 and bad["false_corrections"] >= 1
        good_ok = good["met"] == 1 and good["false_corrections"] == 0
        print(
            f"SELFTEST empty_met={bool(empty['met'])} bad_met={bool(bad['met'])} "
            f"good_met={bool(good['met'])} pass={int(empty_ok and bad_ok and good_ok)}"
        )
        print("empty " + emit(empty))
        return 0 if empty_ok and bad_ok and good_ok else 1
    lesson = git_show(args.repo, args.tip, "corpus/lessons/round-37.md") or ""
    result = score(
        lesson,
        append=facts[0], census_tip=facts[1], census_base=facts[2],
        exitcodes=facts[3], seatlogs=facts[4],
        lesson_blob=facts[5], report_blob=facts[6],
    )
    print(emit(result))
    return 0 if result["met"] else 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as exc:  # noqa: BLE001 — usage/env boundary
        print(f"error: {exc}", file=sys.stderr)
        sys.exit(2)
