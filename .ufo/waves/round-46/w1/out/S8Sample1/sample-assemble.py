#!/usr/bin/env python3
"""Assemble the S8Sample1 KQ65 hand-labeled claim-outcome sample.

This script does NOT read or classify outcomes. Every (round, claim, side,
path, rev, line, outcome, phrasing_class) tuple below was assigned by hand
from the source text. The script only (a) pulls the verbatim line text from
the byte-identical dumps of `git show <rev>:<path>` and (b) asserts that the
expected anchor substring is present, so a mis-numbered line fails loudly.
"""
import csv
import os
import sys

OUT = sys.argv[1]

FLEET = "9b676be886e1e2a428fa81321a05a16363ca68ac"
LANE = "4a2a4d55d09dfacf83dc62d1b3fddae5f6d2a050"

# (round, claim, side, path, rev, line, outcome, class, must-contain)
ROWS = [
    # ---------------- round 10 (declared C1 freshness, C3 capability/coverage)
    (10, "C1", "self", ".ufo/reports/round-10/kama.md", FLEET, 50, "met", "outcome-word", "freshness: improved, 7"),
    (10, "C3", "self", ".ufo/reports/round-10/kama.md", FLEET, 51, "met", "outcome-word", "coverage: improved, 8"),
    (10, "C1", "self", ".ufo/reports/round-10/kama.md", FLEET, 44, "met", "table-row", "| C1 freshness |"),
    (10, "C3", "self", ".ufo/reports/round-10/kama.md", FLEET, 45, "met", "table-row", "| C3 capability |"),
    (10, "C3", "self", ".ufo/reports/round-10/kama.md", FLEET, 46, "met", "table-row", "| C3 coverage |"),
    (10, "C1+C3", "self", ".ufo/reports/round-10/kama.md", FLEET, 117, "met", "multi-claim-line", "freshness 7 → 8 and coverage 8 → 9"),
    (10, "C1", "self", ".ufo/reports/round-10/kama.md", FLEET, 120, "met", "measurement-only", "rows=50 resolved=48 terminal=2 unresolved=0"),
    (10, "C3", "self", ".ufo/reports/round-10/kama.md", FLEET, 124, "met", "measurement-only", "9 → 12 entries, and 0 → 3"),
    (10, "C1+C3", "self", ".ufo/reports/round-10/kama.md", FLEET, 53, "met", "other", "No axis is harmed"),
    (10, "C1+C3", "outside", "corpus/lessons/round-10-verifier-spotcheck.md", LANE, 17, "met", "multi-claim-line", "freshness improved"),
    # ---------------- round 11 (declared C1 calibration, C2 coverage)
    (11, "C1+C2", "self", ".ufo/reports/round-11/kama.md", FLEET, 10, "met", "multi-claim-line", "C1 improved; C2 improved"),
    (11, "C1", "self", ".ufo/reports/round-11/kama.md", FLEET, 120, "met", "table-row", "| C1 calibration |"),
    (11, "C2", "self", ".ufo/reports/round-11/kama.md", FLEET, 121, "met", "table-row", "| C2 coverage |"),
    (11, "C1+C2", "self", ".ufo/reports/round-11/kama.md", FLEET, 135, "met", "multi-claim-line", "calibration improved; coverage improved"),
    (11, "C1+C2", "outside", "corpus/lessons/round-11-verifier-spotcheck.md", LANE, 9, "met", "multi-claim-line", "C1 calibration and C2 coverage verify"),
    (11, "C1", "outside", "corpus/lessons/round-11-verifier-spotcheck.md", LANE, 80, "met", "table-row", "| C1 provenance |"),
    (11, "C2", "outside", "corpus/lessons/round-11-verifier-spotcheck.md", LANE, 81, "met", "table-row", "| C2 crosswalk metadata |"),
    (11, "C1", "outside", "corpus/lessons/round-11-verifier-spotcheck.md", LANE, 124, "met", "table-row", "| calibration | improved |"),
    (11, "C2", "outside", "corpus/lessons/round-11-verifier-spotcheck.md", LANE, 125, "met", "table-row", "| coverage | improved |"),
    (11, "C1+C2", "outside", "corpus/lessons/round-11-verifier-spotcheck.md", LANE, 132, "met", "multi-claim-line", "calibration 7→7 and coverage 9→9"),
    # ---------------- round 12 (declared C1 calibration)
    (12, "C1", "self", ".ufo/reports/round-12/kama.md", FLEET, 5, "met", "measurement-only", "Calibration stays **7 → 7, delta 0**"),
    (12, "C1", "self", ".ufo/reports/round-12/kama.md", FLEET, 41, "met", "table-row", "| Source correspondence, fixed one-path denominator |"),
    (12, "C1", "self", ".ufo/reports/round-12/kama.md", FLEET, 53, "met", "table-row", "| calibration | **improved**"),
    (12, "C1", "self", ".ufo/reports/round-12/kama.md", FLEET, 60, "met", "other", "no axis harm observed within this bounded scope"),
    (12, "C1", "outside", "corpus/lessons/round-12-verifier-spotcheck.md", LANE, 5, "met", "outcome-word", "C1 calibration verifies"),
    (12, "C1", "outside", "corpus/lessons/round-12-verifier-spotcheck.md", LANE, 71, "met", "measurement-only", "before 1; after 0"),
    (12, "C1", "outside", "corpus/lessons/round-12-verifier-spotcheck.md", LANE, 114, "met", "table-row", "| calibration | improved |"),
    # ---------------- round 13 (declared C1 calibration)
    (13, "C1", "self", ".ufo/reports/round-13/kama.md", FLEET, 8, "met", "measurement-only", "2 missing precise"),
    (13, "C1", "self", ".ufo/reports/round-13/kama.md", FLEET, 100, "met", "table-row", "| Selected frozen before |"),
    (13, "C1", "self", ".ufo/reports/round-13/kama.md", FLEET, 101, "met", "table-row", "| Selected frozen after |"),
    (13, "C1", "self", ".ufo/reports/round-13/kama.md", FLEET, 102, "met", "table-row", "| Live committed file"),
    (13, "C1", "self", ".ufo/reports/round-13/kama.md", FLEET, 125, "met", "outcome-word", "C1 verdict: improved"),
    (13, "C1", "self", ".ufo/reports/round-13/kama.md", FLEET, 141, "met", "other", "No axis harm was observed"),
    (13, "C1", "outside", "corpus/lessons/round-13-verifier-spotcheck.md", LANE, 10, "met", "outcome-word", "C1 calibration verifies as"),
    (13, "C1", "outside", "corpus/lessons/round-13-verifier-spotcheck.md", LANE, 110, "met", "table-row", "| start `941bb32` |"),
    (13, "C1", "outside", "corpus/lessons/round-13-verifier-spotcheck.md", LANE, 111, "met", "table-row", "| delivered `370c066` |"),
    (13, "C1", "outside", "corpus/lessons/round-13-verifier-spotcheck.md", LANE, 146, "met", "table-row", "| frozen after |"),
    (13, "C1", "outside", "corpus/lessons/round-13-verifier-spotcheck.md", LANE, 177, "met", "outcome-word", "C1 therefore verifies as improved"),
    (13, "C1", "outside", "corpus/lessons/round-13-verifier-spotcheck.md", LANE, 230, "met", "table-row", "| calibration | improved |"),
    # ---------------- round 14 (declared C1 calibration capability)
    (14, "C1", "self", ".ufo/reports/round-14/kama.md", FLEET, 5, "met", "measurement-only", "51/51 separately authored fixed adversarial cases"),
    (14, "C1", "self", ".ufo/reports/round-14/kama.md", FLEET, 38, "met", "table-row", "| Before capability |"),
    (14, "C1", "self", ".ufo/reports/round-14/kama.md", FLEET, 39, "met", "table-row", "| After capability |"),
    (14, "C1", "self", ".ufo/reports/round-14/kama.md", FLEET, 48, "met", "outcome-word", "calibration **improved**, score7→7"),
    (14, "C1", "outside", "corpus/lessons/round-14-verifier-spotcheck.md", LANE, 7, "met", "outcome-word", "verifies as `improved`, numeric score 7 → 7"),
    (14, "C1", "outside", "corpus/lessons/round-14-verifier-spotcheck.md", LANE, 68, "met", "measurement-only", "Observed **51 cases / 51 unique names**"),
    (14, "C1", "outside", "corpus/lessons/round-14-verifier-spotcheck.md", LANE, 76, "met", "table-row", "| final fixed corpus |"),
    (14, "C1", "outside", "corpus/lessons/round-14-verifier-spotcheck.md", LANE, 127, "met", "table-row", "| calibration | improved |"),
    (14, "C1", "outside", "corpus/lessons/round-14-verifier-spotcheck.md", LANE, 142, "partial", "qualified-met-not-admitted", "duplicate-rejection generality is not admitted"),
    # ---------------- round 15 (declared C1 calibration)
    (15, "C1", "self", ".ufo/reports/round-15/kama.md", FLEET, 5, "met", "measurement-only", "Numeric score **7 → 7, delta0**"),
    (15, "C1", "self", ".ufo/reports/round-15/kama.md", FLEET, 47, "met", "table-row", "| Original before, `run-before.json` |"),
    (15, "C1", "self", ".ufo/reports/round-15/kama.md", FLEET, 49, "met", "table-row", "| Final after,"),
    (15, "C1", "self", ".ufo/reports/round-15/kama.md", FLEET, 65, "met", "outcome-word", "C1 calibration **improved**, numeric7→7"),
    (15, "C1", "outside", "corpus/lessons/round-15-verifier-spotcheck.md", LANE, 7, "met", "outcome-word", "C1 calibration verifies as **improved**"),
    (15, "C1", "outside", "corpus/lessons/round-15-verifier-spotcheck.md", LANE, 104, "met", "table-row", "| final after |"),
    (15, "C1", "outside", "corpus/lessons/round-15-verifier-spotcheck.md", LANE, 150, "met", "table-row", "| calibration | improved |"),
    # ---------------- round 16 (declared C1 calibration, C2 operability)
    (16, "C1", "self", ".ufo/reports/round-16/kama.md", FLEET, 88, "met", "measurement-only", "**C1 (probe):**"),
    (16, "C1", "self", ".ufo/reports/round-16/kama.md", FLEET, 93, "met", "measurement-only", "**C1 (docs):**"),
    (16, "C1", "self", ".ufo/reports/round-16/kama.md", FLEET, 96, "met", "measurement-only", "**C1 no-harm:**"),
    (16, "C1", "self", ".ufo/reports/round-16/kama.md", FLEET, 98, "met", "measurement-only", "Score: calibration **7 → 7**"),
    (16, "C2", "self", ".ufo/reports/round-16/kama.md", FLEET, 99, "met", "measurement-only", "**C2:** before: no lane tool could start a runtime"),
    (16, "C2", "self", ".ufo/reports/round-16/kama.md", FLEET, 107, "met", "outcome-word", "Score: operability **8 → 8**"),
    (16, "C1+C2", "outside", "corpus/lessons/round-16-verifier-spotcheck.md", LANE, 7, "met", "multi-claim-line", "C1 calibration verifies as **improved**"),
    (16, "C1", "outside", "corpus/lessons/round-16-verifier-spotcheck.md", LANE, 84, "met", "measurement-only", "before is **55 pass / 17 fail"),
    (16, "C1", "outside", "corpus/lessons/round-16-verifier-spotcheck.md", LANE, 87, "met", "measurement-only", "Doc ledger:"),
    (16, "C1", "outside", "corpus/lessons/round-16-verifier-spotcheck.md", LANE, 96, "met", "outcome-word", "**Verdict: calibration improved.**"),
    (16, "C2", "outside", "corpus/lessons/round-16-verifier-spotcheck.md", LANE, 100, "met", "measurement-only", "`receipt.json`: 10 checks, all passed"),
    (16, "C2", "outside", "corpus/lessons/round-16-verifier-spotcheck.md", LANE, 112, "met", "outcome-word", "**Verdict: operability improved**"),
    (16, "C1", "outside", "corpus/lessons/round-16-verifier-spotcheck.md", LANE, 165, "met", "table-row", "| calibration | improved |"),
    (16, "C2", "outside", "corpus/lessons/round-16-verifier-spotcheck.md", LANE, 166, "met", "table-row", "| operability | improved |"),
    # ---------------- round 17 (declared C1 calibration, C2 operability)
    (17, "C1", "self", ".ufo/reports/round-17/kama.md", FLEET, 63, "met", "measurement-only", "- **C1** —"),
    (17, "C2", "self", ".ufo/reports/round-17/kama.md", FLEET, 69, "met", "measurement-only", "- **C2** —"),
    (17, "C1+C2", "self", ".ufo/reports/round-17/kama.md", FLEET, 75, "met", "multi-claim-line", "- No-harm:"),
    (17, "C1+C2", "outside", "corpus/lessons/round-17-verifier-spotcheck.md", LANE, 8, "met", "multi-claim-line", "Both declared claims verify"),
    (17, "C1", "outside", "corpus/lessons/round-17-verifier-spotcheck.md", LANE, 11, "met", "outcome-word", "C1 calibration (7 → 7): improved, bounded"),
    (17, "C2", "outside", "corpus/lessons/round-17-verifier-spotcheck.md", LANE, 16, "met", "outcome-word", "C2 operability (8 → 8, sourced): improved"),
    (17, "C1", "outside", "corpus/lessons/round-17-verifier-spotcheck.md", LANE, 105, "met", "outcome-word", "Verdict: **improved**."),
    (17, "C2", "outside", "corpus/lessons/round-17-verifier-spotcheck.md", LANE, 143, "met", "qualified-met-not-admitted", "admitted on the four control-flipped checks"),
    # ---------------- round 18 (declared C1 operability, C2 calibration)
    (18, "C1", "self", ".ufo/reports/round-18/kama.md", FLEET, 7, "met", "measurement-only", "C1 — operability, 8 → 8"),
    (18, "C2", "self", ".ufo/reports/round-18/kama.md", FLEET, 12, "met", "measurement-only", "C2 — calibration, 7 → 7"),
    (18, "C1", "self", ".ufo/reports/round-18/kama.md", FLEET, 95, "met", "table-row", "| C1 |"),
    (18, "C2", "self", ".ufo/reports/round-18/kama.md", FLEET, 96, "met", "table-row", "| C2 |"),
    (18, "C1+C2", "self", ".ufo/reports/round-18/kama.md", FLEET, 98, "met", "multi-claim-line", "No axis is harmed"),
    (18, "C1", "outside", "corpus/lessons/round-18-verifier-spotcheck.md", LANE, 44, "met", "table-row", "| C1 operability 8→8 |"),
    (18, "C2", "outside", "corpus/lessons/round-18-verifier-spotcheck.md", LANE, 45, "met", "table-row", "| C2 calibration 7→7 |"),
    (18, "C1", "outside", "corpus/lessons/round-18-verifier-spotcheck.md", LANE, 90, "met", "table-row", "| operability | improved |"),
    (18, "C2", "outside", "corpus/lessons/round-18-verifier-spotcheck.md", LANE, 91, "met", "table-row", "| calibration | improved |"),
    # ---------------- round 19 (declared C1 calibration, C2 operability)
    (19, "C1", "self", ".ufo/reports/round-19/kama.md", FLEET, 7, "met", "measurement-only", "C1 — calibration, 7 → 7"),
    (19, "C1", "self", ".ufo/reports/round-19/kama.md", FLEET, 11, "not-met", "outcome-word", "The declared 7 → 8"),
    (19, "C2", "self", ".ufo/reports/round-19/kama.md", FLEET, 16, "met", "measurement-only", "C2 — operability, 8 → 8"),
    (19, "C1", "self", ".ufo/reports/round-19/kama.md", FLEET, 84, "met", "table-row", "| C1 |"),
    (19, "C2", "self", ".ufo/reports/round-19/kama.md", FLEET, 85, "met", "table-row", "| C2 |"),
    (19, "C1+C2", "self", ".ufo/reports/round-19/kama.md", FLEET, 89, "met", "multi-claim-line", "No axis is harmed"),
    (19, "C1", "outside", "corpus/lessons/round-19-verifier-spotcheck.md", LANE, 62, "not-met", "outcome-word", "declared 7 → 8, then refuted and held"),
    (19, "C1", "outside", "corpus/lessons/round-19-verifier-spotcheck.md", LANE, 74, "met", "measurement-only", "0/4 → 4/4 verified"),
    (19, "C2", "outside", "corpus/lessons/round-19-verifier-spotcheck.md", LANE, 83, "met", "measurement-only", "**C2 operability 8 → 8.**"),
    (19, "C2", "outside", "corpus/lessons/round-19-verifier-spotcheck.md", LANE, 94, "met", "table-row", "with the pin: `rejected=3/3`"),
    (19, "C1", "outside", "corpus/lessons/round-19-verifier-spotcheck.md", LANE, 136, "met", "table-row", "| calibration | improved |"),
    (19, "C2", "outside", "corpus/lessons/round-19-verifier-spotcheck.md", LANE, 137, "met", "table-row", "| operability | improved |"),
    (19, "C1+C2", "outside", "corpus/lessons/round-19-verifier-spotcheck.md", LANE, 176, "met", "multi-claim-line", "Both declared claims verify"),
    # ---------------- round 20 (declared C1 calibration, C2 operability)
    (20, "C1+C2", "self", ".ufo/reports/round-20/kama.md", FLEET, 5, "met", "multi-claim-line", "Both claims are supported at those bounded scopes"),
    (20, "C1", "self", ".ufo/reports/round-20/kama.md", FLEET, 25, "met", "table-row", "| C1 — finite named error regressions"),
    (20, "C2", "self", ".ufo/reports/round-20/kama.md", FLEET, 26, "met", "table-row", "| C2 — offline GGUF declared identity"),
    (20, "C1", "outside", "MANIFEST.json", FLEET, 10093, "met", "manifest-field", '"calibration": "improved"'),
    (20, "C2", "outside", "MANIFEST.json", FLEET, 10094, "met", "manifest-field", '"operability": "improved"'),
    (20, "C1+C2", "outside", "MANIFEST.json", FLEET, 10107, "met", "manifest-field", '"rechecks":'),
    (20, "C1+C2", "outside", "MANIFEST.json", FLEET, 10112, "met", "manifest-field", "Admitted: C1 calibration improved 7->7"),
    # ---------------- round 21 (declared C1 calibration, C2 operability)
    (21, "C1+C2", "self", ".ufo/reports/round-21/kama.md", FLEET, 5, "met", "multi-claim-line", "Both are author-supported at bounded scopes"),
    (21, "C1", "self", ".ufo/reports/round-21/kama.md", FLEET, 31, "met", "table-row", "| C1 report-landing detector"),
    (21, "C2", "self", ".ufo/reports/round-21/kama.md", FLEET, 32, "met", "table-row", "| C2 soname-aware install identity"),
    (21, "C1", "self", ".ufo/reports/round-21/kama.md", FLEET, 25, "met", "measurement-only", "summary reports=12 defects=9 corrected=9"),
    (21, "C2", "self", ".ufo/reports/round-21/kama.md", FLEET, 34, "met", "measurement-only", "C2's 0→N detection holds by construction"),
    (21, "C1", "outside", "MANIFEST.json", FLEET, 10563, "met", "manifest-field", '"calibration": "improved"'),
    (21, "C2", "outside", "MANIFEST.json", FLEET, 10564, "met", "manifest-field", '"operability": "improved"'),
    (21, "C1+C2", "outside", "MANIFEST.json", FLEET, 10579, "met", "manifest-field", '"rechecks":'),
    (21, "C1+C2", "outside", "MANIFEST.json", FLEET, 10587, "met", "manifest-field", '"notes":'),
    # ---------------- round 22 (declared C1 calibration)
    (22, "C1", "outside", "MANIFEST.json", FLEET, 11358, "met", "manifest-field", '"verdict": "improved"'),
    (22, "C1", "outside", "MANIFEST.json", FLEET, 11359, "met", "manifest-field", '"scalar_before": 7'),
    (22, "C1", "outside", "MANIFEST.json", FLEET, 11387, "met", "manifest-field", '"rechecks":'),
    (22, "C1", "outside", "MANIFEST.json", FLEET, 11372, "met", "manifest-field", '"scope": "Narrow verified calibration improvement'),
    # ---------------- round 23 (no claims object in the kama closure entry)
    (23, "C1", "outside", "MANIFEST.json", FLEET, 12038, "met", "manifest-field", '"calibration": "improved"'),
    (23, "operability", "outside", "MANIFEST.json", FLEET, 12039, "not-met", "manifest-field", '"operability": "harmed"'),
    (23, "C1", "outside", "MANIFEST.json", FLEET, 12061, "met", "manifest-field", '"rechecks":'),
    (23, "operability", "outside", "MANIFEST.json", FLEET, 12062, "not-met", "manifest-field", '"harm_ruling":'),
    (23, "C1", "outside", "MANIFEST.json", FLEET, 12065, "met", "manifest-field", '"notes":'),
    (23, "operability", "outside", "MANIFEST.json", FLEET, 12065, "not-met", "manifest-field", '"notes":'),
]

import subprocess

FLEET_REPO = "/home/vgpnk/Projects/shokunin"
LANE_REPO = "/home/vgpnk/Projects/shokunin/kama-shokunin"
FILES = {}


def lines_at(rev, path):
    """Verbatim lines of ``git show rev:path``, read from the cited repository."""
    key = (rev, path)
    if key not in FILES:
        repo = FLEET_REPO if (path == "MANIFEST.json" or path.startswith(".ufo/")) else LANE_REPO
        out = subprocess.run(["git", "-C", repo, "show", rev + ":" + path],
                             capture_output=True, check=True)
        FILES[key] = out.stdout.decode("utf-8").split("\n")
    return FILES[key]


for r in ROWS:
    text = lines_at(r[4], r[3])[r[5] - 1]
    if r[8] not in text:
        sys.exit("MISMATCH round %s line %s: expected %r not in %r" % (r[0], r[5], r[8], text[:200]))

with open(OUT, "w", encoding="utf-8", newline="") as fh:
    w = csv.writer(fh, delimiter="\t", lineterminator="\n", quoting=csv.QUOTE_MINIMAL)
    w.writerow(["round", "claim", "side", "path", "rev", "line", "outcome",
                "phrasing_class", "text"])
    for r in ROWS:
        text = lines_at(r[4], r[3])[r[5] - 1].strip()
        w.writerow([r[0], r[1], r[2], r[3], r[4], r[5], r[6], r[7], text])
print("rows", len(ROWS))
