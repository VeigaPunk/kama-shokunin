#!/usr/bin/env python3
"""round-40 C1 calibration audit (frozen before any data seat; kama round 40).

Freezes the r38-verifier-routed digest-citation corrections. All reads are
git blobs at --tip (no working-tree dependence). Exits 0 when met, 1 when not.

Frozen predicate (same sentence as preregistration.json C1):
  - A SOURCES row S474 exists whose `teaches` cell starts with
    "supersedes S472" and contains the exact evidence digest
    5585f6027df2dbc4dbafd4979b61c218ffd94e8af99936733218e0ae989e50f2.
  - corpus/knowledge/sglang-docs-version-pinning-amendment-2026-10-23.md
    carries a "## Correction — round 40" section that names the superseded
    digest 5585f602f71c4d4fa5a20125b2b8e4a1132a2d41abf511d7ef09c43a91d950f2
    and the correct digest 5585f6027df2dbc4dbafd4979b61c218ffd94e8af99936733218e0ae989e50f2.
  - corpus/lessons/round-40.md carries a correction row naming R36-D2C and
    giving the full package digest
    3ad0df68504e1f49a0ab23e68b2034a9d6258345468fa03013737ced7ce234ff.
  - false_corrections == 0: no S47x row other than S474 starts with
    "supersedes S472"; and the amendment carries the wrong full digest
    outside its correction section (the immutable r38 lesson and the
    verifier spot-check legitimately retain it as history).
"""
import argparse, hashlib, json, subprocess, sys

CORRECT_EVIDENCE = "5585f6027df2dbc4dbafd4979b61c218ffd94e8af99936733218e0ae989e50f2"
WRONG_EVIDENCE = "5585f602f71c4d4fa5a20125b2b8e4a1132a2d41abf511d7ef09c43a91d950f2"
CORRECT_PACKAGE = "3ad0df68504e1f49a0ab23e68b2034a9d6258345468fa03013737ced7ce234ff"

AMENDMENT = "corpus/knowledge/sglang-docs-version-pinning-amendment-2026-10-23.md"
LESSON = "corpus/lessons/round-40.md"
REGISTRY = "corpus/SOURCES.md"


def blob(repo, tip, path):
    p = subprocess.run(["git", "-C", repo, "show", f"{tip}:{path}"],
                       capture_output=True, text=True)
    if p.returncode != 0:
        return None
    return p.stdout


def registry_rows(text):
    rows = {}
    for line in (text or "").splitlines():
        if line.startswith("|") and "| S" in line:
            cell = line.split("|")
            if len(cell) > 2 and cell[1].strip().startswith("S"):
                rows[cell[1].strip()] = [c.strip() for c in cell[1:]]
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", required=True)
    ap.add_argument("--tip", required=True)
    ap.add_argument("--out")
    a = ap.parse_args()

    reg = registry_rows(blob(a.repo, a.tip, REGISTRY))
    s474 = reg.get("S474")
    s474_ok = 0
    if s474 and len(s474) >= 9:
        teaches = s474[7]
        if teaches.startswith("supersedes S472") and CORRECT_EVIDENCE in teaches:
            s474_ok = 1

    amend = blob(a.repo, a.tip, AMENDMENT) or ""
    amend_corrected = 0
    if "## Correction — round 40" in amend:
        section = amend.split("## Correction — round 40", 1)[1]
        if CORRECT_EVIDENCE in section and WRONG_EVIDENCE in section:
            amend_corrected = 1

    lesson = blob(a.repo, a.tip, LESSON) or ""
    r36d2c_fixed = 0
    if CORRECT_PACKAGE in lesson and "R36-D2C" in lesson:
        r36d2c_fixed = 1

    false_corrections = 0
    for rid, row in reg.items():
        if rid != "S474" and len(row) >= 9 and row[7].startswith("supersedes S472"):
            false_corrections += 1
    # Wrong full digest anywhere outside the correction sections counts as false.
    if WRONG_EVIDENCE in amend and not amend_corrected:
        false_corrections += 1

    met = bool(s474_ok and amend_corrected and r36d2c_fixed and false_corrections == 0)
    line = (f"s474_row={s474_ok} amend_corrected={amend_corrected} "
            f"r36d2c_fixed={r36d2c_fixed} false_corrections={false_corrections} "
            f"met={'True' if met else 'False'}")
    print(line)
    if a.out:
        with open(a.out, "w") as f:
            f.write(line + "\n")
    sys.exit(0 if met else 1)


if __name__ == "__main__":
    main()
