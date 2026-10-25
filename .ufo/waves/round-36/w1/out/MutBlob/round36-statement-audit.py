#!/usr/bin/env python3
"""Round-36 C1 counter. Routed r35 statements, corrected by append only.

Predicate (identical in the preregistration, this file, and the receipt):
A frozen r35 routed statement is corrected iff corpus/lessons/round-36.md contains a correction row naming its id, the counter re-derives the cited committed-byte fact, the correction row does not contain the token 429, and the r35 lesson blob and the r35 fleet report blob are unchanged.

Exit 0 when met is True, 1 when met is False, 2 on usage.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

PREDICATE = (
    "A frozen r35 routed statement is corrected iff corpus/lessons/round-36.md "
    "contains a correction row naming its id, the counter re-derives the cited "
    "committed-byte fact, the correction row does not contain the token 429, "
    "and the r35 lesson blob and the r35 fleet report blob are unchanged."
)
IDS = ("R35-S211", "R35-WORDS", "R35-MIRROR", "R35-KEEP")
BASE = "e5a8ececf3d60fd53b36bb74299693a29e8f74b6"
LESSON_BLOB = "428f1f8a0e8871022f7c1e8ea47e50ba5a8d6412"
REPORT_BLOB = "6d8f317378ba6048d8a3dfb4944adaf24f341eea"
DISP_BLOB = "9307c5d61c1942857a17cb259b4313460b37d0da"
FLEET = Path("/home/vgpnk/Projects/shokunin")
QUOTE = (
    "When the limit is reached, new requests are rejected with HTTP 503 "
    "so the client can retry on another instance."
)
KEEP_PATHS = (
    ".ufo/waves/round-35/w1/out/ConnSibling/seat.log",
    ".ufo/waves/round-35/w1/out/ExecDisposition/seat.log",
    ".ufo/waves/round-35/w1/out/ScoutCoverageAbsence/seat.log",
    ".ufo/waves/round-35/w1/out/ExecDisposition.md",
    ".ufo/waves/round-35/assimilation/validate/",
    ".ufo/waves/round-35/w1/out/ScribeGate/fetch/docker-dockerfile.html",
    ".ufo/waves/round-35/w1/out/ScribeGate/fetch/dockerfile.html",
)
HTML_PATHS = (
    ".ufo/waves/round-35/w1/out/ScribeGate/fetch/docker-dockerfile.html",
    ".ufo/waves/round-35/w1/out/ScribeGate/fetch/dockerfile.html",
)
FORBIDDEN = "429"


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


def git_paths(repo: Path, rev: str) -> set[str]:
    proc = subprocess.run(
        ["git", "-C", str(repo), "ls-tree", "-r", "--name-only", rev],
        check=False,
        capture_output=True,
        text=True,
    )
    if proc.returncode != 0:
        return set()
    return {line for line in proc.stdout.splitlines() if line}


def rows_of(lesson: str) -> dict[str, str]:
    found: dict[str, str] = {}
    for line in lesson.splitlines():
        for sid in IDS:
            if line.startswith(sid + ":"):
                found[sid] = line
    return found


def quote_words(lesson: str) -> int:
    marker = 'Quote: "'
    start = lesson.find(marker)
    if start < 0:
        return -1
    rest = lesson[start + len(marker) :]
    end = rest.find('"')
    if end < 0:
        return -1
    return len(rest[:end].split())


def score(
    lesson: str,
    *,
    scout: str,
    spot: str,
    old_lesson: str,
    report: str,
    lesson_blob: str | None,
    report_blob: str | None,
    disp_blob: str | None,
    tracked: set[str],
) -> dict[str, int]:
    rows = rows_of(lesson)
    uncorrected = 0
    false_corrections = 0
    for sid in IDS:
        row = rows.get(sid)
        if row is None:
            uncorrected += 1
            continue
        if FORBIDDEN in row or not holds(sid, row, scout, spot, old_lesson, report, disp_blob, tracked):
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


def holds(
    sid: str,
    row: str,
    scout: str,
    spot: str,
    old_lesson: str,
    report: str,
    disp_blob: str | None,
    tracked: set[str],
) -> bool:
    if sid == "R35-S211":
        return (
            "fetched successfully" in scout
            and "still-live" in scout
            and "absent" in scout
            and "HTTP 200" in spot
            and "still-live" in spot
            and "ScoutQuarantineS211.md" in row
            and "still-live" in row
            and "200" in row
        )
    if sid == "R35-WORDS":
        return (
            quote_words(old_lesson) == 20
            and QUOTE in old_lesson
            and "18 words" in old_lesson
            and "20 words" in row
        )
    if sid == "R35-MIRROR":
        return (
            "11 symlinks" in spot
            and "84 regular files" in spot
            and "symlink tree" in report
            and "mixed" in row
            and "11" in row
            and "84" in row
        )
    if sid == "R35-KEEP":
        html_clear = all(path not in tracked for path in HTML_PATHS)
        mirror_clear = not any(
            path.startswith(".ufo/waves/round-35/assimilation/validate/") for path in tracked
        )
        return (
            all(path in row for path in KEEP_PATHS)
            and "seat-log-flush" in row
            and "overwrite-not-committed" in row
            and "mixed-mirror-not-committed" in row
            and "helper-skipped" in row
            and "1066624" in row
            and "1066624" in spot
            and disp_blob == DISP_BLOB
            and html_clear
            and mirror_clear
        )
    return False


def emit(result: dict[str, int]) -> str:
    met = "True" if result["met"] else "False"
    return (
        f"uncorrected {result['uncorrected']} "
        f"false_corrections {result['false_corrections']} "
        f"lesson_unchanged {result['lesson_unchanged']} "
        f"report_unchanged {result['report_unchanged']} met {met}"
    )


def load_facts(repo: Path, tip: str) -> tuple[str, str, str, str, str | None, str | None, str | None, set[str]]:
    scout = git_show(repo, tip, ".ufo/waves/round-35/w1/out/ScoutQuarantineS211.md") or ""
    spot = git_show(repo, tip, "corpus/lessons/round-35-verifier-spotcheck.md") or ""
    old_lesson = git_show(repo, tip, "corpus/lessons/round-35.md") or ""
    report = git_show(FLEET, "HEAD", ".ufo/reports/round-35/kama.md") or ""
    return (
        scout,
        spot,
        old_lesson,
        report,
        git_blob(repo, tip, "corpus/lessons/round-35.md"),
        git_blob(FLEET, "HEAD", ".ufo/reports/round-35/kama.md"),
        git_blob(repo, tip, ".ufo/waves/round-35/w1/out/ExecDisposition.md"),
        git_paths(repo, tip),
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", type=Path, required=True)
    parser.add_argument("--tip", required=True)
    parser.add_argument("--selftest", action="store_true")
    args = parser.parse_args()
    if args.selftest:
        scout, spot, old_lesson, report, lesson_blob, report_blob, disp_blob, tracked = load_facts(
            args.repo, args.tip
        )
        empty = score(
            "",
            scout=scout,
            spot=spot,
            old_lesson=old_lesson,
            report=report,
            lesson_blob=lesson_blob,
            report_blob=report_blob,
            disp_blob=disp_blob,
            tracked=tracked,
        )
        bad_row = (
            "R35-S211: ScoutQuarantineS211.md still-live 200 token 429\n"
            "R35-WORDS: 20 words\n"
            "R35-MIRROR: mixed 11 84\n"
            "R35-KEEP: seat-log-flush overwrite-not-committed "
            "mixed-mirror-not-committed helper-skipped 1066624 "
            + " ".join(KEEP_PATHS)
        )
        bad = score(
            bad_row,
            scout=scout,
            spot=spot,
            old_lesson=old_lesson,
            report=report,
            lesson_blob=lesson_blob,
            report_blob=report_blob,
            disp_blob=disp_blob,
            tracked=tracked,
        )
        words_ok = quote_words(old_lesson) == 20
        empty_ok = empty["met"] == 0 and empty["uncorrected"] == 4
        bad_ok = bad["met"] == 0 and bad["false_corrections"] >= 1
        print(
            f"SELFTEST empty_met={bool(empty['met'])} bad_met={bool(bad['met'])} "
            f"words={quote_words(old_lesson)} pass={int(empty_ok and bad_ok and words_ok)}"
        )
        print("empty " + emit(empty))
        return 0 if empty_ok and bad_ok and words_ok else 1
    lesson = git_show(args.repo, args.tip, "corpus/lessons/round-36.md") or ""
    facts = load_facts(args.repo, args.tip)
    result = score(lesson, scout=facts[0], spot=facts[1], old_lesson=facts[2], report=facts[3], lesson_blob=facts[4], report_blob=facts[5], disp_blob=facts[6], tracked=facts[7])
    print(emit(result))
    return 0 if result["met"] else 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as exc:  # noqa: BLE001 — usage/env boundary
        print(f"error: {exc}", file=sys.stderr)
        sys.exit(2)
