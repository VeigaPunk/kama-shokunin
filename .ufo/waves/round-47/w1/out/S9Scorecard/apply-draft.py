#!/usr/bin/env python3
"""apply-draft.py - apply the round-47 SCORECARD draft to a scratch clone.

usage: apply-draft.py <clone> section|full

section  append the drafted `## Round 47` section at the end of SCORECARD.md
         (the shape the L1 integrates before the measured commit).
full     section + the six head re-anchors the round must make, plus the one
         PROVINCE.md line the restated capability needs and the coverage row's
         PROVINCE hash/line facts recomputed from the edited blob.

Every replacement asserts the old text occurs exactly once. Writes only the
clone; never reads or writes the lane.
"""
import hashlib
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SECTION = os.path.join(HERE, "round-47-section.md")

CANON = os.path.join(HERE, "canon-round-47.md")


def canon_rows():
    rows = [l for l in read(CANON).split("\n")
            if l.startswith("| append-only-audit") or l.startswith("| live-receipt-replay")]
    if len(rows) != 2:
        raise SystemExit(f"canon-round-47.md: expected two restated rows, found {len(rows)}")
    return "\n".join(rows)


NEW_CAP_ROW_UNUSED = (
    "| append-only-audit | Set every path a machine-readable contract declares "
    "append-only against the lane's git history: expand `registry/append-only-contract.tsv` "
    "(each row naming the lane line that declares the rule) over the audited tree, list "
    "every commit deleting >= 20 lines from one of those files with the deletion count equal "
    "to `git diff --numstat`, report the byte-exact maximum number of those lines the file "
    "holds again at any commit from the event to the audited revision and the first commit "
    "that restored all of them, and exit 1 on a partial or unrestored mass deletion "
    "| `tools/append-only-audit.py`; `registry/append-only-contract.tsv`; run "
    "`python3 tools/append-only-audit.py --repo . --to <commit> --json` | 46 |")

EDITS = [
    # 1. banner (SCORECARD.md:6)
    ("SCORECARD.md", "**Current authority (round 46):**", "**Current authority (round 47):**"),
    ("SCORECARD.md", "Latest measured round: 46.", "Latest measured round: 47."),
    ("SCORECARD.md", "kept current in rounds 43, 44, 45 and 46;",
     "kept current in rounds 43, 44, 45, 46 and 47;"),
    # 2. calibration row (SCORECARD.md:18)
    ("SCORECARD.md", "→ `32` (outside closures on record)", "→ `33` (outside closures on record)"),
    ("SCORECARD.md",
     "latest outside closure `corpus/lessons/round-45-verifier-spotcheck.md` "
     "(rejected-honest-stop; re-anchored round 46)",
     "latest outside closure `corpus/lessons/round-46-verifier-spotcheck.md` "
     "(admitted; re-anchored round 47)"),
    ("SCORECARD.md", "| score round 1; evidence re-anchored round 45 |",
     "| score round 1; evidence re-anchored round 47 |"),
    # 3. Planned pointer (SCORECARD.md:53)
    ("SCORECARD.md", "The live plan is `### Planned (round 47)` at the end of this file",
     "The live plan is `### Planned (round 48)` at the end of this file"),
    # 4. head capability mirror (SCORECARD.md:117) and the restated row (SCORECARD.md:130)
    ("SCORECARD.md",
     "Mirror of the round-46 canonical capability list that §Round 46 carries",
     "Mirror of the round-47 canonical capability list that §Round 47 carries"),
    ("SCORECARD.md#head-row",
     "| append-only-audit | Set the lane's five append-only self-description files "
     "(SCORECARD.md, LOG.md, corpus/QUALITY.md, corpus/README.md, corpus/SOURCES.md) against "
     "its git history: list every commit that deletes >= 20 lines from one of them, report "
     "how many of those lines the file holds again at the audited revision and which later "
     "commit first restored all of them, and exit 1 on a partial or unrestored mass deletion "
     "| `tools/append-only-audit.py`; `tools/round46-append-audit-check.py`; run "
     "`python3 tools/append-only-audit.py --repo . --to <commit> --json` | 46 |",
     "@@CANON@@"),
    # 5. saturation sentence (SCORECARD.md:136)
    ("SCORECARD.md", "(kept current in round 46)", "(kept current in round 47)"),
    ("SCORECARD.md",
     "capability first-working rounds 10, 14, 16, 20, 25, 30, 41, 42, 43, 46 (highest "
     "canonical list)",
     "capability first-working rounds 10, 14, 16, 20, 25, 30, 41, 42, 43, 46, 47 (highest "
     "canonical list)"),
    ("SCORECARD.md",
     "A capability entered in round 46, so the window is not exhausted either.",
     "A capability entered in round 47, so the window is not exhausted either."),
    ("SCORECARD.md", "None. 6 axes and 10 capabilities remain active.",
     "None. 6 axes and 11 capabilities remain active."),
    # 6. PROVINCE.md:17 - the restated capability's file set and the contract token
    ("PROVINCE.md",
     "`tools/append-only-audit.py` with `tools/round46-append-audit-check.py` (append-only "
     "audit of the five append-only self-description files: every commit deleting >= 20 "
     "lines from one of them, how many of those lines the file holds again at the audited "
     "revision and the commit that restored them; round 46)",
     "`tools/append-only-audit.py` with `registry/append-only-contract.tsv` and "
     "`tools/round47-append-audit-v2-check.py` (append-only audit of the contract-declared "
     "self-description set: every commit deleting >= 20 lines from one of those files, with "
     "a deleted count equal to git numstat, the largest share of those lines any commit in "
     "the event's window holds again and the commit that restored them; round 46, v2 round "
     "47); `tools/kama-live-replay.py` (re-acquire a live receipt's server archive and model "
     "from the URLs its provenance records, verify both sha256 values, re-run the lifecycle "
     "and compare every check; round 47)"),
]


def read(p):
    with open(p, encoding="utf-8") as f:
        return f.read()


def write(p, s):
    with open(p, "w", encoding="utf-8") as f:
        f.write(s)


def main():
    repo, mode = sys.argv[1], sys.argv[2]
    top = subprocess.run(["git", "-C", repo, "rev-parse", "--show-toplevel"],
                         capture_output=True, text=True).stdout.strip()
    if os.path.realpath(top) != os.path.realpath(repo):
        raise SystemExit(f"refusing: {repo} is not the toplevel of a checkout ({top})")
    if mode not in ("section", "full"):
        raise SystemExit("mode is section|full")
    if mode == "full":
        for path, old, new in EDITS:
            if new == "@@CANON@@":
                new = canon_rows()
            head_only = path.endswith("#head-row")
            p = os.path.join(repo, path.split("#")[0])
            s = read(p)
            n = s.count(old)
            if head_only:
                # the round-46 canonical block keeps this row byte-intact as history:
                # edit the head mirror only, and only above §Historical head sections
                cut = s.index("## Historical head sections")
                if s.index(old) >= cut or n < 1:
                    raise SystemExit(f"{path}: head row not above the historical block")
                i = s.index(old)
                write(p, s[:i] + new + s[i + len(old):])
                continue
            if n != 1:
                raise SystemExit(f"{path}: old text occurs {n} times: {old[:70]!r}")
            write(p, s.replace(old, new))
        # the coverage row's PROVINCE facts follow the edited blob
        prov = open(os.path.join(repo, "PROVINCE.md"), "rb").read()
        digest = hashlib.sha256(prov).hexdigest()
        nlines = prov.count(b"\n") + (0 if prov.endswith(b"\n") else 1)
        sc = read(os.path.join(repo, "SCORECARD.md"))
        m = re.search(r"surface list `PROVINCE\.md` sha256 `([0-9a-f]{64})` \((\d+) lines\)", sc)
        if not m:
            raise SystemExit("coverage row fact not found in SCORECARD.md")
        sc = sc.replace(m.group(0),
                        f"surface list `PROVINCE.md` sha256 `{digest}` ({nlines} lines)")
        write(os.path.join(repo, "SCORECARD.md"), sc)
        print(f"coverage row: PROVINCE.md sha256 {digest[:16]}… ({nlines} lines)")
    sc = read(os.path.join(repo, "SCORECARD.md"))
    section = read(SECTION)
    if "## Round 47 — " in sc:
        raise SystemExit("SCORECARD.md already carries a round-47 section")
    if not sc.endswith("\n"):
        sc += "\n"
    write(os.path.join(repo, "SCORECARD.md"), sc + "\n" + section)
    print(f"{mode}: SCORECARD.md {len(sc.splitlines())} -> {len(read(os.path.join(repo, 'SCORECARD.md')).splitlines())} lines")


if __name__ == "__main__":
    main()
