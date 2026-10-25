#!/usr/bin/env python3
"""Round-35 C1 counter. Calibration of four frozen r34 self-assessment statements.

Predicate (identical in the preregistration, this file, and the receipt):
A frozen r34 self-assessment statement is corrected iff corpus/lessons/round-35.md
contains a correction row naming its id, the counter re-derives the cited
committed-byte fact, and the r34 fleet report blob is unchanged.

A correction row is one line beginning '| R34-'. Required tokens must sit on
that line. A row whose tokens disagree with the re-derived fact is a false
correction and does not clear the statement. met is True only when
uncorrected=0, false_corrections=0, and report_unchanged=1.

Exit 0 when met is True, 1 when met is False, 2 on usage.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

PREDICATE = (
    "A frozen r34 self-assessment statement is corrected iff "
    "corpus/lessons/round-35.md contains a correction row naming its id, "
    "the counter re-derives the cited committed-byte fact, and the r34 "
    "fleet report blob is unchanged."
)

FLEET = Path("/home/vgpnk/Projects/shokunin")
REPORT_REV = "16cf603211cd08240e640ef72969d8eddb1410bd"
REPORT_PATH = ".ufo/reports/round-34/kama.md"
REPORT_BLOB = "7610d532696f5c6e214840fa2ec4112584589252"
README_REV = "719655f12517a9ce6b1a5ca44316897fed8420b0"
MANIFEST_REV = "b784e1ab273472eaa750fc10918ca4be67fa7697"
MANIFEST_PATH = ".ufo/waves/round-34/w1/out/dispatch-manifest.json"
SPOT_PATH = "corpus/lessons/round-34-verifier-spotcheck.md"
IDS = ("R34-MAP", "R34-R33COUNT", "R34-LIVE", "R34-MANIFEST")


def git_show(repo: Path, rev: str, path: str) -> str:
    proc = subprocess.run(
        ["git", "-C", str(repo), "show", f"{rev}:{path}"],
        check=False,
        capture_output=True,
        text=True,
    )
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr.strip() or f"git show failed {rev}:{path}")
    return proc.stdout


def git_blob(repo: Path, rev: str, path: str) -> str:
    proc = subprocess.run(
        ["git", "-C", str(repo), "rev-parse", f"{rev}:{path}"],
        check=False,
        capture_output=True,
        text=True,
    )
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr.strip() or "rev-parse failed")
    return proc.stdout.strip()


def correction_line(lesson: str, sid: str) -> str | None:
    prefix = f"| {sid} |"
    for line in lesson.splitlines():
        if line.startswith(prefix):
            return line
    return None


def facts(lane: Path) -> dict[str, bool]:
    report = git_show(FLEET, REPORT_REV, REPORT_PATH)
    readme = git_show(lane, README_REV, "corpus/README.md")
    spot = git_show(lane, README_REV, SPOT_PATH)
    manifest = git_show(lane, MANIFEST_REV, MANIFEST_PATH)
    return {
        "report_has_map_sentence": "coverage map gains two entries" in report,
        "readme_lacks_alias": "serving-alias-contract.md" not in readme,
        "readme_lacks_resolution": "served-model-id-resolution.md" not in readme,
        "report_has_22": "22 untracked" in report,
        "spot_has_23": "23 untracked" in spot,
        "spot_has_modified": "1 modified" in spot,
        "report_has_live": "2 lane processes still live" in report,
        "spot_says_do_not_carry": "Do not carry that live count forward" in spot,
        "report_cites_manifest": "dispatch-manifest.json" in report,
        "manifest_lacks_error": "Cannot combine --prompt with --auto" not in manifest,
        "report_unchanged": git_blob(FLEET, REPORT_REV, REPORT_PATH) == REPORT_BLOB,
    }


def row_ok(sid: str, line: str, got: dict[str, bool]) -> bool:
    if sid == "R34-MAP":
        need = (
            "false" in line
            and "719655f" in line
            and "serving-alias-contract.md" in line
            and "served-model-id-resolution.md" in line
            and "still on the map" not in line
        )
        derived = (
            got["report_has_map_sentence"]
            and got["readme_lacks_alias"]
            and got["readme_lacks_resolution"]
        )
        return need and derived
    if sid == "R34-R33COUNT":
        need = "false" in line and "23 untracked" in line and "1 modified" in line
        need = need and "22 was correct" not in line
        derived = got["report_has_22"] and got["spot_has_23"] and got["spot_has_modified"]
        return need and derived
    if sid == "R34-LIVE":
        need = "not carried forward" in line and "processes are still live" not in line
        derived = got["report_has_live"] and got["spot_says_do_not_carry"]
        return need and derived
    if sid == "R34-MANIFEST":
        need = (
            "b784e1ab" in line
            and "lacks" in line
            and "Cannot combine --prompt with --auto" in line
        )
        derived = got["report_cites_manifest"] and got["manifest_lacks_error"]
        return need and derived
    return False


def audit(lane: Path, lesson_text: str) -> dict[str, int | bool]:
    got = facts(lane)
    uncorrected = 0
    false_corrections = 0
    for sid in IDS:
        line = correction_line(lesson_text, sid)
        if line is None:
            uncorrected += 1
            continue
        if row_ok(sid, line, got):
            continue
        false_corrections += 1
        uncorrected += 1
    met = uncorrected == 0 and false_corrections == 0 and got["report_unchanged"]
    return {
        "uncorrected": uncorrected,
        "false_corrections": false_corrections,
        "report_unchanged": int(got["report_unchanged"]),
        "met": met,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", type=Path, required=True)
    parser.add_argument("--lesson", type=Path, default=None)
    parser.add_argument("--selftest", action="store_true")
    args = parser.parse_args()
    if args.selftest:
        lane = args.repo
        missing = audit(lane, "")
        bad = audit(
            lane,
            "\n".join(
                [
                    "| R34-MAP | true | still on the map |",
                    "| R34-R33COUNT | false | 22 was correct |",
                    "| R34-LIVE | processes are still live |",
                    "| R34-MANIFEST | present in the working tree |",
                ]
            ),
        )
        ok_missing = (not missing["met"]) and missing["uncorrected"] == 4
        ok_bad = (not bad["met"]) and bad["false_corrections"] == 4
        print(
            f"SELFTEST missing_met={missing['met']} bad_met={bad['met']} "
            f"pass={int(ok_missing and ok_bad)}"
        )
        return 0 if ok_missing and ok_bad else 1
    lesson_path = args.lesson or (args.repo / "corpus/lessons/round-35.md")
    text = lesson_path.read_text(encoding="utf-8") if lesson_path.is_file() else ""
    result = audit(args.repo, text)
    met = "True" if result["met"] else "False"
    print(
        "uncorrected {uncorrected} false_corrections {false_corrections} "
        "report_unchanged {report_unchanged} met {met}".format(
            uncorrected=result["uncorrected"],
            false_corrections=result["false_corrections"],
            report_unchanged=result["report_unchanged"],
            met=met,
        )
    )
    return 0 if result["met"] else 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as exc:  # noqa: BLE001 — usage/env boundary
        print(f"error: {exc}", file=sys.stderr)
        sys.exit(2)
