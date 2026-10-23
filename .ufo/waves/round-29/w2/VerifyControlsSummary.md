# w2 / VerifyControlsSummary — round-29 C1 pre-data controls: SUMMARY vs raw receipts

Seat: kama-r29-w2-VerifyControlsSummary-3 · 2026-10-23 · Scope: recompute `.ufo/waves/round-29/controls/SUMMARY.md` from every `<seat>/counter.out` + `receipt.json`; confirm no verdict receipt shows a changed counter.

## Verdict

**SUMMARY.md's table is fully supported: 14/14 seats, every cell (valid / false / unresolved / met) agrees exactly with the raw receipts. Only RefPaste has `met True`. All 20 verdict-bearing receipts record `counter_sha256 fe11d599d064…` (= sha256 of the live lane copy of `count-c1.py`, re-verified below); no verdict receipt shows a changed counter.** Two LOW-severity documentation defects found (both in CtlObjectStore / SUMMARY wording), no data defect.

## Recomputed table (from raw receipts, compared cell-by-cell to SUMMARY.md)

| Seat | Receipt file(s) | append_only | rows | valid | false | unresolved | met | tip[0:12] | SUMMARY row agrees |
|---|---|---|---|---|---|---|---|---|---|
| CtlDoNothing | receipt.json + counter.out | True | 0 | 0 | 0 | 11 | False | 827d136546b8 | YES |
| CtlDeletion | receipt.json + counter.out | False | 0 | 0 | 0 | 69 | False | 1c2a351f8519 | YES |
| CtlEditInPlace | receipt.json + counter.out | False | 0 | 0 | 0 | 69 | False | a528237e8f17 | YES |
| CtlJunk | receipt.json + counter.out | True | 11 | 0 | 11 | 22 | False | 394e898d132c | YES |
| CtlAllFalse | receipt.json + counter.out | True | 69 | 11 | 58 | 58 | False | 3fe6136627df | YES |
| CtlLabelKeyed | receipt.json + counter.out | True | 69 | 0 | 69 | 80 | False | 9c3dd9133e2c | YES |
| CtlTypeGuess | receipt.json + counter.out | True | 35 | 11 | 24 | 24 | False | 3802e4faac93 | YES |
| CtlSourceBounds | receipt.json + counter.out | True | 16 | 9 | 7 | 9 | False | af96283389de | YES |
| CtlNoReader | receipt.json + counter.out | True | 11 | 0 | 11 | 22 | False | 123ec63eb8f6 | YES |
| CtlBaseTree | receipt.json + counter.out | True | 10 | 6 | 4 | 9 | False | 93efe2d45da5 | YES |
| CtlWorkingTree | receipt.json + receipt-head.json + counter.out + counter-head.out | True | 0 | 0 | 0 | 11 | False | 827d136546b8 (both runs) | YES |
| CtlObjectStore | receipt.json + receipt-baseline.json + receipt-subst{A,B,C}-*.json + all 5 counter*.out | True | 0 | 0 | 0 | 11 | False | 827d136546b8 (all 5 runs) | YES ("all three shapes") |
| CtlDuplicate shape 1 | receipt.json + counter.out | True | 22 | 0 | 11 | 22 | False | 8c0d61ea3fba | YES |
| CtlDuplicate shape 2 | receipt-2.json + counter-2.out | True | 12 | 11 | 1 | 1 | False | a50152fd9ebd | YES |
| RefPaste | receipt.json + counter.out | True | 11 | 11 | 0 | 0 | **True** | a59f90ec1d70 | YES |

Every quoted "Counter line" string in SUMMARY.md matches the corresponding raw `counter.out` byte-for-byte in its quoted fields, including CtlDeletion/CtlEditInPlace's `append_only False, unresolved 69` and CtlDoNothing's `tip = freeze commit` (tip `827d136546b8` = freeze commit `827d136546b85059…`). Arithmetic identity from `count-c1.py` `main()` — `unresolved = (mismatched_at_base − valid_corrections) + false_corrections` (or `69 + false_rows` when `append_only False`) — holds for all 23 receipts. Class census corroborates two rows independently: `by_class` P10 H2 N2 C27 T3 Q25 = 69; the 11 base mismatches are 4 P + 7 Q (RefPaste receipt `mismatches`), which is exactly why CtlTypeGuess's 35 P/Q rows score valid 11 / false 24 / unresolved 24.

## Counter-immutability check

- `sha256sum /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-29/count-c1.py` → `fe11d599d064f5749c829394fc813f43921de2f9903e41c7217e3daa4b647383` (matches the frozen value; the lane copy is unchanged today).
- All 20 verdict-bearing `receipt*.json` (CtlAllFalse, CtlBaseTree, CtlDeletion, CtlDoNothing, CtlDuplicate ×2, CtlEditInPlace, CtlJunk, CtlLabelKeyed, CtlNoReader, CtlObjectStore ×5, CtlSourceBounds, CtlTypeGuess, CtlWorkingTree ×2, RefPaste) record `counter_sha256: fe11d599d064…` and `counter: "kama round-29 count-c1 v1"`. No verdict receipt shows a changed counter.
- Exception, disclosed and intentional: `CtlObjectStore/receipt-DIAGNOSTIC-subst{A,B,C}-honoured.json` record `counter_sha256 5ad2c74d0b84640b1cbd9f2d805f386e3360a7284858d6f16e2741ca8d50ffb6` = sha256 of the sandbox copy `/fast/scratch/hyaku/kama-r29/ctl/CtlObjectStore/diag-counter.py` (hash verified locally) — the counter with `--no-replace-objects` removed, run deliberately to prove the substitution channels were live (all three read `valid 11 / unresolved 0 / met True` on the same payload). These are canaries, not control verdicts; CtlObjectStore's verdict rests on the five `fe11d599…` receipts. See Finding 1.

## Independent re-run (strongest check)

Re-ran the frozen lane counter against the seats' own sandbox clones:

- RefPaste: `--repo /fast/scratch/hyaku/kama-r29/ctl/RefPaste/repo --tip a59f90ec1d7077a482ada768be8cb7d976b96a71` → `statements 69 mismatched_at_base 11 append_only True valid_corrections 11 false_corrections 0 unresolved 0 met True tip a59f90ec1d70`, exit 0. Receipt: `w2/out/VerifyControlsSummary/recompute-refpaste.json`.
- CtlDoNothing: `--repo /fast/scratch/hyaku/kama-r29/ctl/CtlDoNothing/repo --tip 827d136546b85059a984b34970f5b493d9a71290` → `… valid_corrections 0 false_corrections 0 unresolved 11 met False …`, exit 0. Receipt: `w2/out/VerifyControlsSummary/recompute-ctldonothing.json`.

Both reproduce the seats' receipts exactly. The only `met True` control is genuinely produced by the unmodified frozen counter; the freeze-tip baseline genuinely fails.

## Findings (by severity)

1. **LOW — SUMMARY.md counter-immutability sentence is overbroad.** SUMMARY.md states "no control receipt shows the counter changed (all used sha256 `fe11d599…`)". Three receipts in the controls tree do record a different counter hash: `CtlObjectStore/receipt-DIAGNOSTIC-subst{A,B,C}-honoured.json` at `5ad2c74d0b84…` (the disclosed diagnostic copy, `met True` by design). Every *verdict* receipt uses `fe11d599…`, and the table is unaffected; but as written the sentence is falsifiable by a reader who greps all receipts. Recommend the L1 tighten to "no control **verdict** receipt…" or add a parenthetical noting the three disclosed diagnostic receipts.
2. **LOW — CtlObjectStore/REPORT.md lists a nonexistent artifact.** Its Files section names `receipt-DIAGNOSTIC-clean.json`; no such file exists in the seat directory or anywhere under `/fast/scratch/hyaku/kama-r29/ctl/CtlObjectStore/` (checked by find; only `diag-counter.py` matches). The clean-diagnostic result (modified counter, no substitution → `unresolved 11 met False`) is quoted in prose only, with no delivered receipt. The control's verdict does not depend on it, but the report cites an artifact that was not delivered.

No MEDIUM or HIGH findings. No SUMMARY row is unsupported by its receipts.

## Residual risk and verification gaps

- SUMMARY header claims not in my recomputation scope, left to other seats: dispatch timestamp "10:58Z", "no refusal or model switch", "lane checked untracked-clean after the call" (the lane worktree now carries the inherited attempt-1 edits, which is expected per the assignment and not evidence of control-time mutation), and the fresh-clone receipt at the pushed tip (C1-inherited, separately verified). `call.json` does corroborate the seat census: 14 tasks, 7 executor + 7 mutation-tester.
- The DIAGNOSTIC-clean run (finding 2) is unverifiable from delivered receipts alone.

## Evidence index (absolute paths)

- Base dir: `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-29/controls/` — `SUMMARY.md`, `call.json`, 14 seat dirs, `items/`.
- Receipts read: `<seat>/counter.out` for all 14 seats (16 files incl. CtlWorkingTree ×2, CtlDuplicate ×2, CtlObjectStore ×5); `receipt*.json` for all 23 receipts (jq table over every file).
- Counter: `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-29/count-c1.py` (sha256 `fe11d599…7383`, verified 2026-10-23).
- Diagnostic counter: `/fast/scratch/hyaku/kama-r29/ctl/CtlObjectStore/diag-counter.py` (sha256 `5ad2c74d0b84640b1cbd9f2d805f386e3360a7284858d6f16e2741ca8d50ffb6`).
- My re-run receipts: `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-29/w2/out/VerifyControlsSummary/recompute-refpaste.json`, `recompute-ctldonothing.json`.
- REPORT: also at `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-29/w2/out/VerifyControlsSummary/report.md`.

Tool installs: none (jq, git, python3 already present; no pacman/uv/npm transaction performed). Bounds: no writes outside `w2/out/VerifyControlsSummary/` and the two mandated report paths; read-only access to sandbox clones; no fleet/lane mutation.
