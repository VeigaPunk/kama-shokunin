# Round 31 — ScribeReportData

FINDING: C1 meets its frozen counter but is not admissible: the committed no-op control also scores 12/12. C2 remains unmet; committed C2 receipt says 30 rows while the SCORECARD row says 28.

LIMITS: This report uses committed artifacts only. No counters, tests, live server, or other gates were run. The C1 base claim run has no raw receipt, and the SCORECARD's parameterized command does not preserve the actual scratch/output paths. The conflicting C2 evidence is reported, not reconciled.

## Before → after measurements

Commands are the exact parameterized forms recorded in committed `SCORECARD.md` §Round 31; receipt files do not record substitutions for scratch clone or output path.

### C1

- Counting command: `/usr/bin/python3 .ufo/waves/round-31/count-c1.py --lane . --repo <scratch clone> --tip <full commit> --out <receipt>`
- Before: committed SCORECARD/preregistration record that the base has no registry or SKILL table and `count-c1.py` exits 2 (“no table”). Raw claim-baseline receipt missing: `.ufo/waves/round-31/before/c1-base.out`. Existing `.ufo/waves/round-31/before/pilot-c1.json` is a mechanics pilot, `registered 3 counted 3 target 12 met False`, not the claim baseline.
- After: `registered 18 counted 17 target 12 met True not-counted ['K31-10']`
- Measured commit: `54c6f4fe070c5d4edd994a8894277083be64118c`
- Receipt: `.ufo/waves/round-31/c1/c1-54c6f4fe.json`
- Falsifier: committed `.ufo/waves/round-31/w1/out/CriticClaimSize/c1-noop.json` reports `registered 12 counted 12 target 12 met True` using duplicate rows asserting the base request's `n_predict = 1`. C1 is met-on-counter, not an improvement.

### C2

- Counting command: `/usr/bin/python3 .ufo/waves/round-31/count-c2.py --repo <scratch clone> --tip <full commit> --out <receipt>`
- Before: `rows 28 base_mismatched 13 exempt 1 valid_corrections 0 false_corrections 0 unresolved 13 append_only True met False tip 07794a4d30a5` — receipt `.ufo/waves/round-31/before/c2-base.out`.
- After (committed receipt): `rows 30 base_mismatched 13 exempt 1 valid_corrections 10 false_corrections 0 unresolved 3 append_only True met False tip b4f3edc0bfc1` — measured commit `b4f3edc0bfc1f797dc3dceedfea9507ad5c7d3ea`; receipt `.ufo/waves/round-31/c2/c2-b4f3edc0.json`.
- Verbatim conflict: SCORECARD §Round 31 instead says after `rows 28 base_mismatched 13 exempt 1 valid_corrections 10 false_corrections 0 unresolved 3 append_only True met False` and points to `.ufo/waves/round-31/c2/c2-tip.json`. That pointer is absent from the committed tree; `corpus/lessons/round-31.md` agrees with the receipt's 30 rows. `controls/RefRepair/receipt.txt` records `valid 10 false 3 unresolved 3` when all thirteen failing rows are appended.

## Landed changes

| Commit | Subject |
|---|---|
| `0e6f8ed6891c09d5208ac1fdcb294ed9a842832e` | round-31: freeze — C1 chat-adapter counter + registry pins, C2 claim-row revision counter, preregistration, pilot receipts |
| `3b1e84f8212e136351f078b4d5c1cc170aaf12fa` | round-31: chat-adapter surface — SKILL table, registry, 13 pinned source rows, knowledge entry, PROVINCE/QUALITY/README; wave-1 fragments + control receipts |
| `54c6f4fe070c5d4edd994a8894277083be64118c` | round-31: remap S180-S191 to the twelve measured source lines and drop the duplicate K31-14 row |
| `b4f3edc0bfc1f797dc3dceedfea9507ad5c7d3ea` | round-31: SCORECARD claims record (C1 met-on-counter/not admitted, C2 counter defect), ten claim-row corrections and the three unexpressible rows, planned r32 |
| `d45f947e289a8d5eeb1ccac78115cb70ca9cdc75` | round-31: LOG entry, round-31 lesson (Gate/Mistakes/Repairs), C2 receipt and the round-30 hold receipt |
| `382d11b2107d335705875da1a4d889b074bd6fa6` | round-31: SOURCES repair — S180-S191 relocated into ## Registry (census E12 exit 1 -> exit 0), lesson Mistakes row 4, census start/end receipts, two late seat artifacts |

## Scope and artifacts

- Behavior: evidence-only report draft; no product behavior changed.
- Gates: read-only history/tree/diff commands only; no counters, tests, or live checks.
- Touched surfaces: this report and files in `.ufo/waves/round-31/w2/out/ScribeReportData/`; no tracked lane file edited.
- Out of scope: C3, rerunning C1/C2, resolving the SCORECARD/receipt mismatch, and verdict/admission.
- Detailed RESULTS block and raw receipts/logs: `.ufo/waves/round-31/w2/out/ScribeReportData/report.md` and sibling evidence files (`command-results.txt`, `committed-tree-listings.txt`, receipt copies, and scorecard excerpts).
