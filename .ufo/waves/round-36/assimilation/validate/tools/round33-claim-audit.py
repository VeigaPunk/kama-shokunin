#!/usr/bin/env python3
"""Count corrections to round-32 C2 self-assessment/evidence mismatches.

The counter grades the SCORECARD claim as it was written at --statement-rev,
then verifies its append-only correction in the evaluated --tip. It reads only
Git blobs and never changes the repository.
"""
from __future__ import annotations

import argparse
import re
import subprocess
import sys

STATEMENT_REV = "dc4258bdb08d658f1c5b15abc8378461659bd155"
CORRECTION_HEADING = (
    "### Round 33 — correction of round-32 gate-control receipt references"
)
FAULTS = {
    "thin-row": (
        ".ufo/waves/round-32/c2/controls/thin-row-v2.out",
        ".ufo/waves/round-32/c2/controls/thin-v2.out",
        "defective .ufo/waves/round-29/count-c1.py: thin-row",
    ),
    "empty-exit-map": (
        ".ufo/waves/round-32/c2/controls/empty-exit-v2.out",
        ".ufo/waves/round-32/c2/controls/noexit-v2.out",
        "defective .ufo/waves/round-29/count-c1.py: empty-exit-map",
    ),
    "missing-path": (
        ".ufo/waves/round-32/c2/controls/nonexistent-path-v2.out",
        ".ufo/waves/round-32/c2/controls/badpath-v2.out",
        "defective .ufo/waves/round-29/count-c1.py: missing-path:.ufo/waves/round-999/count-c999.py",
    ),
}
FULL_REV = re.compile(r"^[0-9a-f]{40}$")


class AuditError(Exception):
    pass


def git(repo: str, *args: str) -> bytes:
    proc = subprocess.run(
        ["git", "-C", repo, *args],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if proc.returncode:
        message = proc.stderr.decode("utf-8", "replace").strip()
        raise AuditError(f"git {' '.join(args)} failed ({proc.returncode}): {message}")
    return proc.stdout


def verify_revision(repo: str, revision: str) -> None:
    if not FULL_REV.fullmatch(revision):
        raise AuditError("revision must be a full 40-character commit id")
    resolved = git(repo, "rev-parse", "--verify", f"{revision}^{{commit}}").decode().strip()
    if resolved != revision:
        raise AuditError(f"revision did not resolve exactly: {revision}")


def blob(repo: str, revision: str, path: str) -> str | None:
    proc = subprocess.run(
        ["git", "-C", repo, "show", f"{revision}:{path}"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if proc.returncode:
        return None
    try:
        return proc.stdout.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise AuditError(f"non-UTF-8 evidence blob: {path}") from exc


def claim_line(scorecard: str) -> str | None:
    for line in scorecard.splitlines():
        if line.startswith("| C2 — instrument-registry gate"):
            return line
    return None


def correction_rows(scorecard: str) -> dict[str, list[tuple[str, str]]]:
    lines = scorecard.splitlines()
    try:
        start = lines.index(CORRECTION_HEADING) + 1
    except ValueError:
        return {}
    rows: dict[str, list[tuple[str, str]]] = {}
    for line in lines[start:]:
        if line.startswith("### ") or line.startswith("## "):
            break
        if not line.startswith("|"):
            continue
        cells = [cell.strip().strip("`") for cell in line.strip().strip("|").split("|")]
        if len(cells) == 3 and cells[0] in FAULTS:
            rows.setdefault(cells[0], []).append((cells[1], cells[2]))
    return rows


def run(repo: str, statement_rev: str, tip: str) -> int:
    verify_revision(repo, statement_rev)
    verify_revision(repo, tip)
    written = blob(repo, statement_rev, "SCORECARD.md")
    if written is None:
        raise AuditError("SCORECARD.md is absent at the statement revision")
    line = claim_line(written)
    if line is None or "c2/controls/*-v2.out" not in line or "each fixture exits 1" not in line:
        raise AuditError("the frozen round-32 C2 statement was not found at its declared revision")

    false_at_writing = 0
    for fault, (old_path, _correct_path, expected_line) in FAULTS.items():
        old_receipt = blob(repo, statement_rev, old_path)
        if old_receipt is None:
            raise AuditError(f"the frozen receipt is missing at statement revision: {old_path}")
        if expected_line not in old_receipt:
            false_at_writing += 1

    current = blob(repo, tip, "SCORECARD.md")
    if current is None:
        raise AuditError("SCORECARD.md is absent at the evaluated revision")
    rows = correction_rows(current)
    valid = 0
    legacy_mislabels = 0
    for fault, (old_path, correct_path, expected_line) in FAULTS.items():
        old_receipt = blob(repo, tip, old_path)
        if old_receipt is not None and expected_line not in old_receipt:
            legacy_mislabels += 1
        entries = rows.get(fault, [])
        if len(entries) != 1:
            continue
        cited_path, stated_output = entries[0]
        corrected_receipt = blob(repo, tip, cited_path)
        if (
            cited_path == correct_path
            and stated_output == expected_line
            and corrected_receipt is not None
            and expected_line in corrected_receipt
        ):
            valid += 1

    unresolved = len(FAULTS) - valid
    met = false_at_writing == len(FAULTS) and valid == len(FAULTS) and unresolved == 0
    print(
        "R33_CLAIM_AUDIT "
        f"statement_rev={statement_rev} tip={tip} "
        f"false_at_writing={false_at_writing} valid_corrections={valid} "
        f"unresolved={unresolved} legacy_mislabels_at_tip={legacy_mislabels} "
        f"met={'True' if met else 'False'}"
    )
    return 0 if met else 1


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", default=".", help="lane Git repository")
    parser.add_argument("--statement-rev", default=STATEMENT_REV, help="full commit that wrote the r32 C2 row")
    parser.add_argument("--tip", required=True, help="full commit whose correction is evaluated")
    args = parser.parse_args()
    try:
        return run(args.repo, args.statement_rev, args.tip)
    except AuditError as exc:
        print(f"R33_CLAIM_AUDIT_ERROR {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
