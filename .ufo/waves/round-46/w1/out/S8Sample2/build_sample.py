#!/usr/bin/env python3
"""Assemble the KQ65 hand-read claim-outcome sample (round-46 item S8Sample2).

This is NOT a claim-outcome reader. It contains no classifier: every row below
was hand-picked by seat S8Sample2 from the two named sources per round, and the
script only (a) reads the exact physical line from the dumped source bytes,
(b) asserts the line number still carries the hand-read text, and (c) writes the
TSV. Labels are literal table data.

Sources (dumped read-only by the seat):
  fleet reports : git -C /home/vgpnk/Projects/shokunin show HEAD:.ufo/reports/round-N/kama.md
                  rev 9b676be886e1e2a428fa81321a05a16363ca68ac (fleet HEAD at sample time)
  closures      : git -C .../kama-shokunin show 4a2a4d55...:corpus/lessons/round-N-verifier-spotcheck.md
                  rev 4a2a4d55d09dfacf83dc62d1b3fddae5f6d2a050
  rounds 22-23  : git -C /home/vgpnk/Projects/shokunin show HEAD:MANIFEST.json (closure entry)
"""
import hashlib
import os
import sys

SRC = "/fast/scratch/hyaku/kama-r46/S8Sample2"
FLEET_REV = "9b676be886e1e2a428fa81321a05a16363ca68ac"
LANE_REV = "4a2a4d55d09dfacf83dc62d1b3fddae5f6d2a050"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)))

FLEET = "fleet:.ufo/reports/round-%d/kama.md"
LANE = "lane:corpus/lessons/round-%d-verifier-spotcheck.md"
MANIFEST = "fleet:MANIFEST.json"

# (round, claim, side, path, rev, line, outcome, phrasing, local_file, expect_prefix)
ROWS = [
    # ---- round 22 -------------------------------------------------------
    (22, "C1", "self", FLEET % 22, FLEET_REV, 5, "met", "outcome-word", "src/fleet-r22.md", "**Declared C1"),
    (22, "C1", "self", FLEET % 22, FLEET_REV, 69, "met", "measurement-only", "src/fleet-r22.md", "| Helper error/identity separation"),
    (22, "C1", "self", FLEET % 22, FLEET_REV, 70, "met", "measurement-only", "src/fleet-r22.md", "| Source URL versus owned citation"),
    (22, "(entry)", "outside", MANIFEST, FLEET_REV, 11345, "met", "manifest-field", "MANIFEST.json", '"admitted": true,'),
    (22, "(entry)", "outside", MANIFEST, FLEET_REV, 11346, "met", "manifest-field", "MANIFEST.json", '"verdict": "admitted",'),
    (22, "C1", "outside", MANIFEST, FLEET_REV, 11358, "met", "manifest-field", "MANIFEST.json", '"verdict": "improved",'),
    (22, "C1", "outside", MANIFEST, FLEET_REV, 11372, "met", "manifest-field", "MANIFEST.json", '"scope": "Narrow verified'),
    # ---- round 23 -------------------------------------------------------
    (23, "C1", "self", FLEET % 23, FLEET_REV, 62, "met", "measurement-only", "src/fleet-r23.md", "| Fault rows met"),
    (23, "C1", "self", FLEET % 23, FLEET_REV, 63, "met", "measurement-only", "src/fleet-r23.md", "| Tracebacks / executed programs"),
    (23, "C1", "self", FLEET % 23, FLEET_REV, 64, "met", "measurement-only", "src/fleet-r23.md", "| Contract rows"),
    (23, "C1", "self", FLEET % 23, FLEET_REV, 65, "met", "measurement-only", "src/fleet-r23.md", "| Controls"),
    (23, "C1", "self", FLEET % 23, FLEET_REV, 66, "met", "measurement-only", "src/fleet-r23.md", "| Isolation mutants"),
    (23, "C1", "self", FLEET % 23, FLEET_REV, 67, "met", "measurement-only", "src/fleet-r23.md", "| Selftest (no harm)"),
    (23, "C1", "self", FLEET % 23, FLEET_REV, 68, "met", "measurement-only", "src/fleet-r23.md", "| Historical ledger (no harm)"),
    (23, "C1", "self", FLEET % 23, FLEET_REV, 69, "met", "measurement-only", "src/fleet-r23.md", "| Over-refusal probe"),
    (23, "C1", "self", FLEET % 23, FLEET_REV, 74, "met", "outcome-word", "src/fleet-r23.md", "Verdict (author): C1"),
    (23, "C1", "self", FLEET % 23, FLEET_REV, 75, "met", "qualified-met-not-admitted", "src/fleet-r23.md", "7 → 7. Not admitted by me"),
    (23, "C1", "self", FLEET % 23, FLEET_REV, 76, "partial", "qualified-met-not-admitted", "src/fleet-r23.md", "under the no-trade rule"),
    (23, "C1", "self", FLEET % 23, FLEET_REV, 116, "partial", "other", "src/fleet-r23.md", "- Frontier: D4 partially advanced"),
    (23, "(entry)", "outside", MANIFEST, FLEET_REV, 12035, "not-met", "manifest-field", "MANIFEST.json", '"admitted": false,'),
    (23, "(entry)", "outside", MANIFEST, FLEET_REV, 12036, "not-met", "manifest-field", "MANIFEST.json", '"verdict": "rejected-harmed",'),
    (23, "C1", "outside", MANIFEST, FLEET_REV, 12038, "met", "manifest-field", "MANIFEST.json", '"calibration": "improved",'),
    (23, "C1", "outside", MANIFEST, FLEET_REV, 12065, "met", "manifest-field", "MANIFEST.json", '"notes": "REJECTED-HARMED despite verified bounded C1'),
    # ---- round 24 -------------------------------------------------------
    (24, "C1", "self", FLEET % 24, FLEET_REV, 5, "unprovable", "outcome-word", "src/fleet-r24.md", "**Declared C1: calibration7 → 7**"),
    (24, "C1", "self", FLEET % 24, FLEET_REV, 63, "unprovable", "other", "src/fleet-r24.md", "### C1 calibration7 → 7"),
    (24, "C1", "self", FLEET % 24, FLEET_REV, 65, "partial", "measurement-only", "src/fleet-r24.md", "The original registered measurement plan"),
    (24, "C1", "self", FLEET % 24, FLEET_REV, 79, "met", "table-row", "src/fleet-r24.md", "| Primary amended view"),
    (24, "C1", "self", FLEET % 24, FLEET_REV, 80, "not-met", "table-row", "src/fleet-r24.md", "| Original primary view"),
    (24, "C1", "self", FLEET % 24, FLEET_REV, 81, "partial", "table-row", "src/fleet-r24.md", "| Required-unavailable primary states"),
    (24, "C1", "self", FLEET % 24, FLEET_REV, 82, "met", "table-row", "src/fleet-r24.md", "| Generic regression consumers"),
    (24, "C1", "self", FLEET % 24, FLEET_REV, 83, "partial", "table-row", "src/fleet-r24.md", "| Mutation observations"),
    (24, "C1", "self", FLEET % 24, FLEET_REV, 84, "partial", "table-row", "src/fleet-r24.md", "| Provenance/custody"),
    (24, "C1", "self", FLEET % 24, FLEET_REV, 92, "partial", "table-row", "src/fleet-r24.md", "|Complete local promisor-marked"),
    (24, "C1", "self", FLEET % 24, FLEET_REV, 93, "met", "table-row", "src/fleet-r24.md", "|Genuine omitted pre-cutoff commit"),
    (24, "C1", "self", FLEET % 24, FLEET_REV, 94, "met", "table-row", "src/fleet-r24.md", "|Unavailable required commit/tree/blob/report"),
    (24, "C1", "self", FLEET % 24, FLEET_REV, 95, "not-met", "table-row", "src/fleet-r24.md", "|Missing citation in any promisor-backed repo"),
    (24, "C1", "self", FLEET % 24, FLEET_REV, 96, "unprovable", "table-row", "src/fleet-r24.md", "|No lazy fetching"),
    (24, "C1", "self", FLEET % 24, FLEET_REV, 97, "partial", "table-row", "src/fleet-r24.md", "|Metadata alone is not incompleteness"),
    (24, "C1", "self", FLEET % 24, FLEET_REV, 98, "partial", "table-row", "src/fleet-r24.md", "|R23 filed history unchanged"),
    (24, "C1", "self", FLEET % 24, FLEET_REV, 100, "unprovable", "outcome-word", "src/fleet-r24.md", "Author overall: **not achieved/unprovable in full"),
    (24, "(entry)", "outside", LANE % 24, LANE_REV, 13, "not-met", "outcome-word", "src/spot-r24.md", "Status **ok**, admitted **false**"),
    (24, "C1", "outside", LANE % 24, LANE_REV, 14, "unprovable", "outcome-word", "src/spot-r24.md", "report, not a marker. The full original C1"),
    (24, "C1", "outside", LANE % 24, LANE_REV, 15, "unprovable", "outcome-word", "src/spot-r24.md", "not achieved**, with its withdrawn"),
    (24, "C1", "outside", LANE % 24, LANE_REV, 53, "partial", "other", "src/spot-r24.md", "## Per-claim verification — original C1"),
    (24, "C1", "outside", LANE % 24, LANE_REV, 58, "partial", "measurement-only", "src/spot-r24.md", "Observed: **47 unique primary cases"),
    (24, "C1", "outside", LANE % 24, LANE_REV, 139, "unprovable", "table-row", "src/spot-r24.md", "| calibration / full C1 | unprovable"),
    # ---- round 25 -------------------------------------------------------
    (25, "C1", "self", FLEET % 25, FLEET_REV, 15, "partial", "qualified-met-not-admitted", "src/fleet-r25.md", "- **C1 — declared calibration"),
    (25, "C1", "self", FLEET % 25, FLEET_REV, 92, "met", "measurement-only", "src/fleet-r25.md", "  'M17-ref-shadow']` at efe58e96"),
    (25, "C2", "self", FLEET % 25, FLEET_REV, 96, "met", "measurement-only", "src/fleet-r25.md", "  `registered 14 observed 14 bound True"),
    (25, "C1", "self", FLEET % 25, FLEET_REV, 129, "not-met", "other", "src/fleet-r25.md", "  not fit; C1 earns no calibration credit."),
    (25, "C1", "self", FLEET % 25, FLEET_REV, 131, "partial", "outcome-word", "src/fleet-r25.md", "Claim verdicts (author): C1 measured value verified"),
    (25, "C2", "self", FLEET % 25, FLEET_REV, 135, "met", "outcome-word", "src/fleet-r25.md", "waiver). C2 verified as measured"),
    (25, "(entry)", "outside", LANE % 25, LANE_REV, 17, "not-met", "outcome-word", "src/spot-r25.md", "Status **ok**, admitted **false**"),
    (25, "C1", "outside", LANE % 25, LANE_REV, 20, "partial", "outcome-word", "src/spot-r25.md", "- The C1 measured value verifies"),
    (25, "C1", "outside", LANE % 25, LANE_REV, 24, "not-met", "outcome-word", "src/spot-r25.md", "  is therefore `unchanged`."),
    (25, "C2", "outside", LANE % 25, LANE_REV, 28, "met", "outcome-word", "src/spot-r25.md", "- C2 verifies as measured"),
    (25, "C1", "outside", LANE % 25, LANE_REV, 96, "met", "measurement-only", "src/spot-r25.md", "The supporting full run was verified"),
    (25, "C1", "outside", LANE % 25, LANE_REV, 133, "not-met", "table-row", "src/spot-r25.md", "| calibration | unchanged"),
    (25, "C2", "outside", LANE % 25, LANE_REV, 134, "met", "table-row", "src/spot-r25.md", "| coverage | improved"),
    # ---- round 26 -------------------------------------------------------
    (26, "C1", "self", FLEET % 26, FLEET_REV, 123, "met", "table-row", "src/fleet-r26.md", "| C1 depth"),
    (26, "C1", "self", FLEET % 26, FLEET_REV, 124, "unprovable", "table-row", "src/fleet-r26.md", "| shortcut control on the same counter"),
    (26, "C1", "self", FLEET % 26, FLEET_REV, 127, "unprovable", "qualified-met-not-admitted", "src/fleet-r26.md", "**C1 verdict (author)"),
    (26, "C1", "self", FLEET % 26, FLEET_REV, 128, "unprovable", "qualified-met-not-admitted", "src/fleet-r26.md", "established.** A shortcut"),
    (26, "C1", "self", FLEET % 26, FLEET_REV, 194, "unprovable", "other", "src/fleet-r26.md", "  was corrected by the falsify wave; but the claim's counter does not"),
    (26, "C1", "self", FLEET % 26, FLEET_REV, 240, "unprovable", "other", "src/fleet-r26.md", "- C1 admission is the closure's"),
    (26, "(entry)", "outside", LANE % 26, LANE_REV, 20, "not-met", "outcome-word", "src/spot-r26.md", "Status **ok**, admitted **false**"),
    (26, "C1", "outside", LANE % 26, LANE_REV, 23, "met", "measurement-only", "src/spot-r26.md", "- C1 (depth) reached its frozen target"),
    (26, "C1", "outside", LANE % 26, LANE_REV, 30, "unprovable", "outcome-word", "src/spot-r26.md", "  frozen before data, so C1 is not established"),
    (26, "C1", "outside", LANE % 26, LANE_REV, 118, "unprovable", "outcome-word", "src/spot-r26.md", "Ruling: **C1 not established**"),
    (26, "C1", "outside", LANE % 26, LANE_REV, 178, "unprovable", "table-row", "src/spot-r26.md", "| depth | unprovable"),
    (26, "C1", "outside", LANE % 26, LANE_REV, 214, "unprovable", "other", "src/spot-r26.md", "  supersession gain. Because C1 is a measured claim"),
    # ---- round 27 -------------------------------------------------------
    (27, "C1", "self", FLEET % 27, FLEET_REV, 18, "not-met", "outcome-word", "src/fleet-r27.md", "  It was withdrawn before data"),
    (27, "C1", "self", FLEET % 27, FLEET_REV, 81, "not-met", "measurement-only", "src/fleet-r27.md", "  - base `a720399e`"),
    (27, "C1", "self", FLEET % 27, FLEET_REV, 82, "not-met", "measurement-only", "src/fleet-r27.md", "  - tip content commit `4d2e74f4`"),
    (27, "C1", "self", FLEET % 27, FLEET_REV, 84, "not-met", "outcome-word", "src/fleet-r27.md", "  - Target missed: C1 is a **miss**"),
    (27, "X1", "self", FLEET % 27, FLEET_REV, 85, "unprovable", "outcome-word", "src/fleet-r27.md", "- **X1**: exploratory"),
    (27, "X1", "self", FLEET % 27, FLEET_REV, 121, "unprovable", "other", "src/fleet-r27.md", "- **discernment: unchanged.** X1 is the round's discernment move"),
    (27, "(entry)", "outside", LANE % 27, LANE_REV, 21, "not-met", "outcome-word", "src/spot-r27.md", "- Admitted: **false**"),
    (27, "C1", "outside", LANE % 27, LANE_REV, 22, "not-met", "outcome-word", "src/spot-r27.md", "  is a miss under its frozen kill rule"),
    (27, "X1", "outside", LANE % 27, LANE_REV, 25, "unprovable-but-better", "outcome-word", "src/spot-r27.md", "  **`unprovable-but-better`**."),
    (27, "C1", "outside", LANE % 27, LANE_REV, 59, "not-met", "other", "src/spot-r27.md", "### C1 — depth, `counted >= 15`"),
    (27, "C1", "outside", LANE % 27, LANE_REV, 74, "not-met", "measurement-only", "src/spot-r27.md", "  counted 0 target 15 met False"),
    (27, "X1", "outside", LANE % 27, LANE_REV, 91, "unprovable-but-better", "other", "src/spot-r27.md", "### X1 — calibration, exploratory"),
    (27, "X1", "outside", LANE % 27, LANE_REV, 155, "unprovable", "other", "src/spot-r27.md", "It stays unprovable rather than measured"),
    (27, "C1", "outside", LANE % 27, LANE_REV, 175, "not-met", "table-row", "src/spot-r27.md", "| depth | unchanged"),
    (27, "X1", "outside", LANE % 27, LANE_REV, 176, "unprovable-but-better", "table-row", "src/spot-r27.md", "| calibration | unprovable-but-better"),
    # ---- round 28 -------------------------------------------------------
    (28, "C1", "self", FLEET % 28, FLEET_REV, 57, "unprovable", "measurement-only", "src/fleet-r28.md", "  - A type-only conversion policy counts"),
    (28, "C1", "self", FLEET % 28, FLEET_REV, 126, "not-met", "measurement-only", "src/fleet-r28.md", "    target 18 met False not-counted []`."),
    (28, "C1", "self", FLEET % 28, FLEET_REV, 128, "met", "measurement-only", "src/fleet-r28.md", "    `registered 34 counted 26 target 18 met True`."),
    (28, "C1", "self", FLEET % 28, FLEET_REV, 133, "met", "measurement-only", "src/fleet-r28.md", "    trees gives `registered 34 counted 34 target 18 met True`"),
    (28, "C1", "self", FLEET % 28, FLEET_REV, 156, "partial", "other", "src/fleet-r28.md", "- **ExecShortcutPostData"),
    (28, "C1", "self", FLEET % 28, FLEET_REV, 209, "unprovable", "qualified-met-not-admitted", "src/fleet-r28.md", "- **quality: unchanged (author reading).**"),
    (28, "C1", "self", FLEET % 28, FLEET_REV, 278, "met", "qualified-met-not-admitted", "src/fleet-r28.md", "- **C1 disposition**"),
    (28, "(entry)", "outside", LANE % 28, LANE_REV, 15, "not-met", "outcome-word", "src/spot-r28.md", "- admitted `false`"),
    (28, "C1", "outside", LANE % 28, LANE_REV, 16, "unprovable", "outcome-word", "src/spot-r28.md", "- C1 (depth) does **not** verify"),
    (28, "C1", "outside", LANE % 28, LANE_REV, 65, "unprovable", "other", "src/spot-r28.md", "### C1 — depth, `counted >= 18`"),
    (28, "C1", "outside", LANE % 28, LANE_REV, 76, "met", "table-row", "src/spot-r28.md", "| Committed receipts"),
    (28, "C1", "outside", LANE % 28, LANE_REV, 162, "unprovable", "table-row", "src/spot-r28.md", "| depth | unprovable"),
    # ---- round 29 -------------------------------------------------------
    (29, "C1", "self", FLEET % 29, FLEET_REV, 38, "met", "measurement-only", "src/fleet-r29.md", "  unresolved 0 met True tip 513eba3ba51a"),
    (29, "C1", "self", FLEET % 29, FLEET_REV, 47, "met", "measurement-only", "src/fleet-r29.md", "  r29 receipt unchanged 69/11"),
    (29, "C1", "self", FLEET % 29, FLEET_REV, 98, "not-met", "measurement-only", "src/fleet-r29.md", "  `statements 69 mismatched_at_base 11 append_only True valid_corrections 0"),
    (29, "C1", "self", FLEET % 29, FLEET_REV, 102, "met", "measurement-only", "src/fleet-r29.md", "  append_only True valid_corrections 11 false_corrections 0 unresolved 0 met True"),
    (29, "C1", "self", FLEET % 29, FLEET_REV, 107, "met", "measurement-only", "src/fleet-r29.md", "- Round-end re-verification"),
    (29, "C1", "self", FLEET % 29, FLEET_REV, 114, "partial", "other", "src/fleet-r29.md", "- Bounded reading (CriticAxisFit/ClaimShape, accepted)"),
    (29, "C1", "self", FLEET % 29, FLEET_REV, 139, "met", "other", "src/fleet-r29.md", "- **quality: improved** — 11 false self-assessment statements"),
    (29, "C1", "outside", LANE % 29, LANE_REV, 28, "not-met", "measurement-only", "src/spot-r29.md", "- base 2aa46e24:"),
    (29, "C1", "outside", LANE % 29, LANE_REV, 29, "met", "measurement-only", "src/spot-r29.md", "- data 513eba3b:"),
    (29, "C1", "outside", LANE % 29, LANE_REV, 30, "met", "measurement-only", "src/spot-r29.md", "- tip 7f595a3bf:"),
    (29, "C1", "outside", LANE % 29, LANE_REV, 34, "met", "outcome-word", "src/spot-r29.md", "Gate-standard treatment:"),
    (29, "C1", "outside", LANE % 29, LANE_REV, 46, "met", "other", "src/spot-r29.md", "- **calibration: improved** — C1 re-measured met True"),
    # ---- round 30 -------------------------------------------------------
    (30, "C1", "self", FLEET % 30, FLEET_REV, 17, "not-met", "measurement-only", "src/fleet-r30.md", "  unresolved 13 met False` (`c1/before/c1-base.out`)"),
    (30, "C1", "self", FLEET % 30, FLEET_REV, 18, "not-met", "measurement-only", "src/fleet-r30.md", "  `valid_corrections 11 unresolved 2 met False`"),
    (30, "C1", "self", FLEET % 30, FLEET_REV, 33, "met", "measurement-only", "src/fleet-r30.md", "  valid_corrections 13 false_corrections 0 unresolved 0 met True"),
    (30, "C1", "self", FLEET % 30, FLEET_REV, 75, "met", "measurement-only", "src/fleet-r30.md", "  valid_corrections 13 false_corrections 0 unresolved 0 met True` (`final/c1-tip.out`)"),
    (30, "C1", "self", FLEET % 30, FLEET_REV, 76, "met", "qualified-met-not-admitted", "src/fleet-r30.md", "Score: calibration 7 → 7"),
    (30, "C2", "self", FLEET % 30, FLEET_REV, 85, "met", "measurement-only", "src/fleet-r30.md", "(`c2/receipt-b-corpusguard-refused.json`). Operability 8 → 8"),
    (30, "C1", "outside", LANE % 30, LANE_REV, 26, "met", "outcome-word", "src/spot-r30.md", "**C1 (calibration, measured) — verified, re-measured.**"),
    (30, "C1", "outside", LANE % 30, LANE_REV, 30, "not-met", "table-row", "src/spot-r30.md", "| `2aa46e24` (base) |"),
    (30, "C1", "outside", LANE % 30, LANE_REV, 32, "met", "table-row", "src/spot-r30.md", "| `026eede9` (measured) |"),
    (30, "C2", "outside", LANE % 30, LANE_REV, 37, "met", "outcome-word", "src/spot-r30.md", "**C2 (operability, capability `instrument-agreement`)"),
    (30, "C1", "outside", LANE % 30, LANE_REV, 45, "met", "table-row", "src/spot-r30.md", "| calibration | improved |"),
    (30, "C2", "outside", LANE % 30, LANE_REV, 46, "met", "table-row", "src/spot-r30.md", "| operability | improved |"),
    # ---- round 31 -------------------------------------------------------
    (31, "C1", "self", FLEET % 31, FLEET_REV, 81, "unprovable", "qualified-met-not-admitted", "src/fleet-r31.md", "  Verdict: **met on the frozen counter; NOT admitted**"),
    (31, "C2", "self", FLEET % 31, FLEET_REV, 87, "not-met", "outcome-word", "src/fleet-r31.md", "  3 append_only True met False`. Verdict: **not met — counter defect**"),
    (31, "C3", "self", FLEET % 31, FLEET_REV, 91, "unprovable", "qualified-met-not-admitted", "src/fleet-r31.md", "  `registered 9 unregistered 0`, exit 0. Verdict: **met on the frozen predicate; NOT admitted**"),
    (31, "(multi)", "self", FLEET % 31, FLEET_REV, 177, "unprovable", "multi-claim-line", "src/fleet-r31.md", "- C1/C2/C3 verify on their frozen counters"),
    (31, "(multi)", "self", FLEET % 31, FLEET_REV, 124, "not-met", "multi-claim-line", "src/fleet-r31.md", "  admission (no-op registry 12/12; non-injective key; occurrence-only gate), and all three claims"),
    (31, "C1", "outside", LANE % 31, LANE_REV, 25, "mixed", "other", "src/spot-r31.md", "- Falsification evidence: `w2/out/CriticNoop/report.md`"),
    (31, "C2", "outside", LANE % 31, LANE_REV, 31, "not-met", "other", "src/spot-r31.md", "- Frozen predicate (\"rows >= 28"),
    (31, "C3", "outside", LANE % 31, LANE_REV, 36, "unprovable", "other", "src/spot-r31.md", "- Falsification evidence: `w2/out/ExecC3Control/report.md`"),
    (31, "C1", "outside", LANE % 31, LANE_REV, 44, "unprovable", "table-row", "src/spot-r31.md", "| depth | unchanged |"),
    (31, "C2", "outside", LANE % 31, LANE_REV, 45, "not-met", "table-row", "src/spot-r31.md", "| calibration | unchanged |"),
    (31, "C3", "outside", LANE % 31, LANE_REV, 46, "unprovable", "table-row", "src/spot-r31.md", "| operability | unchanged |"),
    (31, "(multi)", "outside", LANE % 31, LANE_REV, 78, "not-met", "outcome-word", "src/spot-r31.md", "Rejected as admission"),
    # ---- round 32 -------------------------------------------------------
    (32, "C1", "self", FLEET % 32, FLEET_REV, 74, "not-met", "measurement-only", "src/fleet-r32.md", "  `rows 30 base_mismatched 13 exempt 1 valid_corrections 10"),
    (32, "C1", "self", FLEET % 32, FLEET_REV, 77, "met", "measurement-only", "src/fleet-r32.md", "  `rows 30 base_mismatched 13 exempt 1 valid_corrections 13"),
    (32, "C2", "self", FLEET % 32, FLEET_REV, 89, "met", "measurement-only", "src/fleet-r32.md", "  `967d88528c1d`: `registered 10 unregistered 0 defective 0`"),
    (32, "(multi)", "self", FLEET % 32, FLEET_REV, 162, "met", "multi-claim-line", "src/fleet-r32.md", "  fixture, and both claims are reported as instrument repairs"),
    (32, "(multi)", "self", FLEET % 32, FLEET_REV, 202, "met", "other", "src/fleet-r32.md", "- **Honesty notes:** the claims are instrument repairs"),
    (32, "C1", "outside", LANE % 32, LANE_REV, 32, "met", "outcome-word", "src/spot-r32.md", "Verdict: verified (re-measured)."),
    (32, "C2", "outside", LANE % 32, LANE_REV, 46, "met", "outcome-word", "src/spot-r32.md", "Verdict: verified on substance"),
    # ---- round 33 -------------------------------------------------------
    (33, "C1", "self", FLEET % 33, FLEET_REV, 83, "not-met", "measurement-only", "src/fleet-r33.md", "- Before, at base `cc46980359278d0967cf65e785b41c27b8d9c36c`: `false_at_writing=3 valid_corrections=0"),
    (33, "C1", "self", FLEET % 33, FLEET_REV, 84, "met", "measurement-only", "src/fleet-r33.md", "- After, measured at `1c881bbd3e1cce5f0b01f1afc6d3229866cbe712`: `false_at_writing=3 valid_corrections=3"),
    (33, "C2", "self", FLEET % 33, FLEET_REV, 89, "not-met", "measurement-only", "src/fleet-r33.md", "- Before, at base `cc46980359278d0967cf65e785b41c27b8d9c36c`: `complete=0/4"),
    (33, "C2", "self", FLEET % 33, FLEET_REV, 90, "met", "measurement-only", "src/fleet-r33.md", "- After, measured at `1c881bbd3e1cce5f0b01f1afc6d3229866cbe712`: `complete=4/4"),
    (33, "(multi)", "self", FLEET % 33, FLEET_REV, 92, "met", "other", "src/fleet-r33.md", "No capability row was added."),
    (33, "C1", "outside", LANE % 33, LANE_REV, 33, "met", "outcome-word", "src/spot-r33.md", "Verdict: **verified (re-measured + evidence-verified)**."),
    (33, "C2", "outside", LANE % 33, LANE_REV, 45, "met", "outcome-word", "src/spot-r33.md", "Verdict: **verified (evidence-verified; receipt completeness re-measured)**."),
]

HEADER = ["round", "claim", "side", "path", "rev", "line", "outcome", "phrasing", "text"]


def main():
    cache = {}
    rows = []
    problems = []
    for (rnd, claim, side, path, rev, line, outcome, phrasing, local, prefix) in ROWS:
        full = os.path.join(SRC, local)
        if full not in cache:
            with open(full, "r", encoding="utf-8") as fh:
                cache[full] = fh.read().split("\n")
        lines = cache[full]
        if line < 1 or line > len(lines):
            problems.append("line %d out of range in %s" % (line, local))
            continue
        text = lines[line - 1]
        if not text.lstrip().startswith(prefix.lstrip()):
            problems.append("line %d of %s does not start with %r: %r" % (line, local, prefix, text[:80]))
            continue
        if "\t" in text:
            text = text.replace("\t", "\\t")
        rows.append([str(rnd), claim, side, path, rev, str(line), outcome, phrasing, text])

    with open(os.path.join(OUT, "sample.tsv"), "w", encoding="utf-8", newline="\n") as fh:
        fh.write("\t".join(HEADER) + "\n")
        for row in rows:
            fh.write("\t".join(row) + "\n")

    with open(os.path.join(OUT, "sample-lines.out"), "w", encoding="utf-8", newline="\n") as fh:
        fh.write("rows=%d\n" % len(rows))
        fh.write("sample_sha256=%s\n" % hashlib.sha256(
            open(os.path.join(OUT, "sample.tsv"), "rb").read()).hexdigest())
        fh.write("source_fleet_rev=%s\nsource_lane_rev=%s\n" % (FLEET_REV, LANE_REV))
        fh.write("column_count=%d\n\n" % len(HEADER))
        for row in rows:
            fh.write("%s\t%s\t%s:%s\t%s\t%s\t%s\n" % (
                row[0], row[1], row[2], row[4][:12], row[5], row[6], row[8][:220]))

    if problems:
        print("PROBLEMS:")
        for p in problems:
            print(" -", p)
        return 1
    print("OK rows=%d columns=%d" % (len(rows), len(HEADER)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
