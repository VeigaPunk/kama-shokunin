```RESULTS
$ git -C /home/vgpnk/Projects/shokunin/kama-shokunin log --reverse --format='%H%x09%s' 07794a4d30a54a60ebdff50ac76d12c6df40a0f1..382d11b2107d335705875da1a4d889b074bd6fa6
exit code: 0
verbatim tail:
0e6f8ed6891c09d5208ac1fdcb294ed9a842832e	round-31: freeze — C1 chat-adapter counter + registry pins, C2 claim-row revision counter, preregistration, pilot receipts
3b1e84f8212e136351f078b4d5c1cc170aaf12fa	round-31: chat-adapter surface — SKILL table, registry, 13 pinned source rows, knowledge entry, PROVINCE/QUALITY/README; wave-1 fragments + control receipts
54c6f4fe070c5d4edd994a8894277083be64118c	round-31: remap S180-S191 to the twelve measured source lines and drop the duplicate K31-14 row
b4f3edc0bfc1f797dc3dceedfea9507ad5c7d3ea	round-31: SCORECARD claims record (C1 met-on-counter/not admitted, C2 counter defect), ten claim-row corrections and the three unexpressible rows, planned r32
d45f947e289a8d5eeb1ccac78115cb70ca9cdc75	round-31: LOG entry, round-31 lesson (Gate/Mistakes/Repairs), C2 receipt and the round-30 hold receipt
382d11b2107d335705875da1a4d889b074bd6fa6	round-31: SOURCES repair — S180-S191 relocated into ## Registry (census E12 exit 1 -> exit 0), lesson Mistakes row 4, census start/end receipts, two late seat artifacts

$ git -C /home/vgpnk/Projects/shokunin/kama-shokunin cat-file -e 382d11b2107d335705875da1a4d889b074bd6fa6:.ufo/waves/round-31/c1/c1-382d11b2.json && git -C /home/vgpnk/Projects/shokunin/kama-shokunin cat-file -e 382d11b2107d335705875da1a4d889b074bd6fa6:.ufo/waves/round-31/c2/c2-382d11b2.json && git -C /home/vgpnk/Projects/shokunin/kama-shokunin cat-file -e 382d11b2107d335705875da1a4d889b074bd6fa6:.ufo/waves/round-31/c2/c2-tip.json
exit code: 128
verbatim tail:
fatal: path '.ufo/waves/round-31/c1/c1-382d11b2.json' exists on disk, but not in '382d11b2107d335705875da1a4d889b074bd6fa6'

$ git -C /home/vgpnk/Projects/shokunin/kama-shokunin ls-tree -r --name-only 382d11b2107d335705875da1a4d889b074bd6fa6 -- .ufo/waves/round-31/c1 .ufo/waves/round-31/c2 .ufo/waves/round-31/before
exit code: 0
verbatim tail:
.ufo/waves/round-31/before/c2-base.out
.ufo/waves/round-31/before/pilot-c1.json
.ufo/waves/round-31/c1/c1-3b1e84f8.json
.ufo/waves/round-31/c1/c1-54c6f4fe.json
.ufo/waves/round-31/c1/c1-remap.json
.ufo/waves/round-31/c1/hold-r30.out
.ufo/waves/round-31/c2/c2-b4f3edc0.json

$ git -C /home/vgpnk/Projects/shokunin/kama-shokunin ls-tree -r --name-only 382d11b2107d335705875da1a4d889b074bd6fa6 -- .ufo/waves/round-31/controls .ufo/waves/round-31/w1/out/CriticClaimSize
exit code: 0
verbatim tail:
.ufo/waves/round-31/controls/CtlAllRows/receipt.txt
.ufo/waves/round-31/controls/CtlBaseTree/receipt.txt
.ufo/waves/round-31/controls/CtlDoNothing/c2.json
.ufo/waves/round-31/controls/CtlDoNothing/receipt.txt
.ufo/waves/round-31/controls/CtlEditInPlace/c2.json
.ufo/waves/round-31/controls/CtlEditInPlace/receipt.txt
.ufo/waves/round-31/controls/CtlNoId/c2.out
.ufo/waves/round-31/controls/CtlNoId/receipt.txt
.ufo/waves/round-31/controls/CtlNoLive/c1.json
.ufo/waves/round-31/controls/CtlNoLive/receipt.txt
.ufo/waves/round-31/controls/CtlNoLive/report.txt
.ufo/waves/round-31/controls/CtlSchemaProjection/c1.json
.ufo/waves/round-31/controls/CtlSchemaProjection/receipt.txt
.ufo/waves/round-31/controls/CtlSchemaProjection/report.md
.ufo/waves/round-31/controls/CtlTamper/c1-tampered.json
.ufo/waves/round-31/controls/CtlTamper/c2-frozen.json
.ufo/waves/round-31/controls/CtlTamper/c2-tampered.json
.ufo/waves/round-31/controls/CtlTamper/receipt.txt
.ufo/waves/round-31/controls/CtlTypeGuess/c1.json
.ufo/waves/round-31/controls/CtlTypeGuess/receipt.txt
.ufo/waves/round-31/controls/CtlWrongCell/c1.out
.ufo/waves/round-31/controls/CtlWrongCell/receipt.txt
.ufo/waves/round-31/controls/CtlWrongObserved/c2-freeze-list.json
.ufo/waves/round-31/controls/CtlWrongObserved/c2.json
.ufo/waves/round-31/controls/CtlWrongObserved/receipt.txt
.ufo/waves/round-31/controls/RefRepair/receipt.txt
.ufo/waves/round-31/w1/out/CriticClaimSize/attack.md
.ufo/waves/round-31/w1/out/CriticClaimSize/c1-distinct-baseline.json
.ufo/waves/round-31/w1/out/CriticClaimSize/c1-noop.json
.ufo/waves/round-31/w1/out/CriticClaimSize/c1-type-guess.json
.ufo/waves/round-31/w1/out/CriticClaimSize/c2-base.json
.ufo/waves/round-31/w1/out/CriticClaimSize/c2-dedup-paste.json
.ufo/waves/round-31/w1/out/CriticClaimSize/c2-literal-paste.json
.ufo/waves/round-31/w1/out/CriticClaimSize/commands.json
.ufo/waves/round-31/w1/out/CriticClaimSize/hold-r30.json
.ufo/waves/round-31/w1/out/CriticClaimSize/scratch-fixtures.bundle

$ git -C /home/vgpnk/Projects/shokunin/kama-shokunin diff --quiet 382d11b2107d335705875da1a4d889b074bd6fa6 -- SCORECARD.md .ufo/waves/round-31/before/c2-base.out .ufo/waves/round-31/before/pilot-c1.json .ufo/waves/round-31/c1/c1-54c6f4fe.json .ufo/waves/round-31/c2/c2-b4f3edc0.json .ufo/waves/round-31/controls/RefRepair/receipt.txt .ufo/waves/round-31/w1/out/CriticClaimSize/c1-noop.json
exit code: 0
verbatim tail: <empty>
```
FINDING: C1 met its frozen counter but is not admissible because the committed no-op control also met it; C2 is unmet, and the C2 receipt and SCORECARD disagree on the after row count (30 vs 28).
LIMITS: This is a committed-artifact audit, not a re-run. No counter, test, or server was run; C1's base exit-2 claim has no raw baseline receipt, and the logged counting commands retain placeholders rather than the actual scratch/output paths.

## Before → after measurements

The command spans below reproduce the parameterized counting commands recorded in the committed SCORECARD §Round 31; the committed receipts do not record concrete scratch-clone or output-path substitutions.

### C1 — depth, measured but not admissible

- Counting command: `/usr/bin/python3 .ufo/waves/round-31/count-c1.py --lane . --repo <scratch clone> --tip <full commit> --out <receipt>`
- Before: committed SCORECARD/preregistration say the registry and SKILL table were absent and the counter exited 2 (“no table”); no raw claim-baseline output is recorded. `receipt missing: .ufo/waves/round-31/before/c1-base.out`. The available `before/pilot-c1.json` is explicitly a mechanics pilot, not the claim baseline: `registered 3 counted 3 target 12 met False`.
- After: `registered 18 counted 17 target 12 met True not-counted ['K31-10']`
- Measured commit: `54c6f4fe070c5d4edd994a8894277083be64118c`
- After receipt: `.ufo/waves/round-31/c1/c1-54c6f4fe.json`
- Before pilot (not a substitute for the missing claim-baseline receipt): `.ufo/waves/round-31/before/pilot-c1.json`
- Falsifying control: committed `w1/out/CriticClaimSize/c1-noop.json` says `registered 12 counted 12 target 12 met True`; the lesson and SCORECARD explain it asserts the base request's `n_predict = 1` in twelve duplicate rows. Thus the count is met-on-counter, not admitted as improvement.

### C2 — calibration, not met

- Counting command: `/usr/bin/python3 .ufo/waves/round-31/count-c2.py --repo <scratch clone> --tip <full commit> --out <receipt>`
- Before: `rows 28 base_mismatched 13 exempt 1 valid_corrections 0 false_corrections 0 unresolved 13 append_only True met False tip 07794a4d30a5`
- After (committed receipt): `rows 30 base_mismatched 13 exempt 1 valid_corrections 10 false_corrections 0 unresolved 3 append_only True met False tip b4f3edc0bfc1`
- Measured commit: `b4f3edc0bfc1f797dc3dceedfea9507ad5c7d3ea`
- Before receipt: `.ufo/waves/round-31/before/c2-base.out`
- After receipt: `.ufo/waves/round-31/c2/c2-b4f3edc0.json`
- Source conflict: committed SCORECARD §Round 31 says the after output is `rows 28 base_mismatched 13 exempt 1 valid_corrections 10 false_corrections 0 unresolved 3 append_only True met False` and points to `.ufo/waves/round-31/c2/c2-tip.json`. The committed-path listing contains `c2-b4f3edc0.json` but not `c2-tip.json`; that receipt says 30 rows, as does `corpus/lessons/round-31.md`. The conflicting SCORECARD wording and missing pointer are retained here, not silently reconciled.
- Counter-defect control: committed `controls/RefRepair/receipt.txt` reports `valid 10 false 3 unresolved 3` when all thirteen failing rows are appended. The lesson attributes the three unresolved C1 rows to the `(row, class)` correction key collision.

## Landed changes

Every commit in `07794a4d30a54a60ebdff50ac76d12c6df40a0f1..382d11b2107d335705875da1a4d889b074bd6fa6`, in ancestry order:

| Commit | Subject |
|---|---|
| `0e6f8ed6891c09d5208ac1fdcb294ed9a842832e` | round-31: freeze — C1 chat-adapter counter + registry pins, C2 claim-row revision counter, preregistration, pilot receipts |
| `3b1e84f8212e136351f078b4d5c1cc170aaf12fa` | round-31: chat-adapter surface — SKILL table, registry, 13 pinned source rows, knowledge entry, PROVINCE/QUALITY/README; wave-1 fragments + control receipts |
| `54c6f4fe070c5d4edd994a8894277083be64118c` | round-31: remap S180-S191 to the twelve measured source lines and drop the duplicate K31-14 row |
| `b4f3edc0bfc1f797dc3dceedfea9507ad5c7d3ea` | round-31: SCORECARD claims record (C1 met-on-counter/not admitted, C2 counter defect), ten claim-row corrections and the three unexpressible rows, planned r32 |
| `d45f947e289a8d5eeb1ccac78115cb70ca9cdc75` | round-31: LOG entry, round-31 lesson (Gate/Mistakes/Repairs), C2 receipt and the round-30 hold receipt |
| `382d11b2107d335705875da1a4d889b074bd6fa6` | round-31: SOURCES repair — S180-S191 relocated into ## Registry (census E12 exit 1 -> exit 0), lesson Mistakes row 4, census start/end receipts, two late seat artifacts |

## Scope notes

- Behavior: evidence-only report draft; no product behavior changed.
- Gates: read-only commit/history/tree checks only; no counters, tests, live server, or other gates executed.
- Touched surfaces: only this seat's report/evidence output files and the designated fleet report path; no tracked lane file was edited.
- Out of scope: C3, new counter runs, resolving the conflicting C2 evidence, and any verdict/admission decision.
- Artifacts: `report.md`, `ScribeReportData.md`, and the raw receipts/logs alongside this report.
