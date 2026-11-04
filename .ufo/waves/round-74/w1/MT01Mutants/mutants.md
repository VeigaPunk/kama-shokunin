# MT01Mutants — round-74 v2 module mutation matrix

Seat MT01Mutants, kama round 74 w1. Scope: mutation-test the three v2 modules.
Strategy per seat spec: modules landed WHILE this seat ran — C1 and C3 executor
modules landed mid-seat and were snapshotted (sha256 in `live-module-sha256.txt`)
and mutated as scratch copies; C2 was still absent at final check, so C2 mutants
ran against a clearly labeled PROTOTYPE built from the frozen predicate
(`prototypes/prototype-c2.py` in the deleted scratch). Live bytes were re-verified
unchanged at the end (same sha256 as the mid-seat snapshot; no executor module
changed under this seat).

## Detector (bounded, same for pristine/mutant/restored)

For each module: run against the committed fixtures rebuilt into this seat's
scratch with the committed builder (`controls/build-survivors.py`), asserting
the kill-arm exit code AND the required finding fragment; plus run the module's
`--selftest` where the module provides one.

## Baselines (pristine runs, receipts: harness-live-results.json)

| Module | Arm | rc | key output |
|---|---|---|---|
| C1 live | c1_invisible | 1 | `canon_round=71 canon_rows=3 demonstrated=4 total=7 invisible=4` |
| C1 live | c1_clean | 0 | `canon_round=74 canon_rows=7 demonstrated=0 total=7 invisible=0` |
| C1 selftest | — | 0 | `SELFDESC_CANON_V2_SELFTEST pass=11 fail=0` |
| C2 prototype | c2_wrapped | 1 | `RECEIPT_CLAIM_V2_FINDING wrapped-claim` |
| C2 prototype | c2_offset | 1 | `RECEIPT_CLAIM_V2_FINDING offset-claim` |
| C2 prototype | c2_mixed_honest | 0 | `bound_revisions=1` |
| C2 prototype | c2_clean_realizable | 0 | `bound_revisions=1` |
| C3 live | c3_edited | 1 | `PROVINCE_HOST_DRIFT_V2_FINDING edited-block …` |
| C3 live | c3_clean | 0 | `edited=0` |
| C3 selftest | — | 0 | `PROVINCE_HOST_DRIFT_V2_SELFTEST pass=10 fail=0` |

## Mutation matrix

### C1 — `tools/round74-selfdesc-canon.py` (live executor bytes)

| # | mutant | class | verdict | changed arms |
|---|---|---|---|---|
| 1 | c1_live_invisible_forced0 | comparison cut (invisible=[]) | KILLED | c1_invisible, c1_clean |
| 2 | c1_live_demonstrated_to_bold | set poison (demonstrated=canon) | KILLED | c1_invisible, c1_clean |
| 3 | c1_live_neq_flip | != → & (invisible∩canon) | KILLED | c1_invisible, c1_clean |
| 4 | c1_live_union_intersection | union→intersection (total) | KILLED | c1_invisible, c1_clean |
| 5 | c1_live_finding_exit0 | exit-code flip (always 0) | KILLED | c1_invisible, c1_clean |
| 6 | c1_live_demo_case_sensitive | case-sensitivity restored (re.I dropped) | KILLED | c1_invisible, c1_clean |
| 7 | c1_live_first_table | scope cut (first table, not newest) | KILLED | c1_invisible, c1_clean |
| 8 | c1_live_ge_to_gt | comparison flip (>= vs >) | KILLED | c1_invisible, c1_clean |
| 9 | c1_live_selftest_arm_never_fails | selftest oracle tamper (problems=None) | KILLED | c1_invisible, c1_clean (module crashes → arm output changes; also detectable by selftest pass-count mismatch) |
| 10 | c1_live_demo_kind_never | scope cut (demo tables classified as canon) | KILLED | c1_invisible, c1_clean |

C1 tally: 10 mutants, 10 KILLED, 0 survived, 0 N/A.

### C2 — `tools/round74-receipt-claim-binding.py` (PROTOTYPE; module absent at final check)

| # | mutant | class | verdict | changed arms |
|---|---|---|---|---|
| 1 | c2_p2l_paragraph_to_line | scope cut (paragraph → line) | KILLED | c2_wrapped, c2_offset |
| 2 | c2_p2l_case_hex | case-sensitivity restored (tip bind) | **SURVIVED** | — |
| 3 | c2_p2l_rev_case | case-sensitivity restored (rev bind) | KILLED | c2_mixed_honest |
| 4 | c2_p2l_exit0 | exit-code flip (clean ignores claims) | KILLED | c2_wrapped, c2_offset |
| 5 | c2_p2l_kind_swap_a | label swap (wrapped→offset) | KILLED | c2_wrapped |
| 6 | c2_p2l_kind_swap_b | label swap (offset→wrapped) | KILLED | c2_offset |
| 7 | c2_p2l_header_flip | comparison flip (== binds instead of !=) | KILLED | c2_wrapped, c2_offset |
| 8 | c2_p2l_claim_always | scope cut (claim check forced true) | KILLED | c2_mixed_honest, c2_clean_realizable |
| 9 | c2_p2l_assert_true | oracle tamper (clean=True) | KILLED | c2_wrapped, c2_offset |

C2 tally: 9 mutants, 8 KILLED, 1 SURVIVED, 0 N/A.

### C3 — `tools/round74-province-host-drift.py` (live executor bytes)

| # | mutant | class | verdict | changed arms |
|---|---|---|---|---|
| 1 | c3_live_edited_ignored | comparison cut (elif False) | KILLED | c3_edited, c3_clean |
| 2 | c3_live_token_regex_broken | `recorded at` regex broken (40→39 hex) | KILLED | c3_edited, c3_clean |
| 3 | c3_live_compare_self | compare block to itself | KILLED | c3_edited, c3_clean |
| 4 | c3_live_finding_exit0 | exit-code flip (always 0) | KILLED | c3_edited, c3_clean |
| 5 | c3_live_neq_flip | != flipped to == | KILLED | c3_edited, c3_clean |
| 6 | c3_live_blocks_newest_only | scope cut (newest block only) | KILLED | c3_edited, c3_clean |

C3 tally: 6 mutants, 6 KILLED, 0 survived, 0 N/A.

## Totals

- Mutants applied: 25 distinct behavior-bearing mutations across the three
  modules (10 C1 + 9 C2 + 6 C3); seat floor was 6/module and 30 total where
  modules are available — C1 and C3 (the landed modules) carry 16 mutants
  against live executor bytes; C2 carries 9 against the labeled prototype
  because the executor module had not landed at final check.
- KILLED: 24. SURVIVED: 1 (`c2_p2l_case_hex`). INCONCLUSIVE: 0
  (no baseline detector failure on any arm).
- N/A: 0 in the final matrix (two early C1 anchors were replaced with
  code-accurate anchors after a source peek; the matrix above reports the
  final, applicable runs).

## Survivor analysis — the one live defect

**`c2_p2l_case_hex` (case-sensitive tip binding) SURVIVED both the committed
fixtures and (by construction) any committable fixture.** Restoring
case-sensitivity to the tip-claim comparison (`rev != tip_sha` instead of
`rev.lower() != tip_lower`) leaves all four fixture arms green:

- c2_wrapped / c2_offset: receipt header rev=A ≠ tip either way → finding
  still fires, same exit 1.
- c2_mixed_honest / c2_clean_realizable: clean arms bind via the explicit-
  revision branch, which the mutant does not touch.

**Why no fixture can kill it (r70 rule):** the defect is load-bearing only on
a paragraph that carries a *tip claim* whose cited receipt's header equals the
tip — and a receipt whose header names the commit that contains it is a git
hash fixpoint, unbuildable on committed bytes (the exact impossibility the
round-73 closure recorded for the old committed-header-equals-tip rule). The
committed builder cannot carry this defect; see
`fixtures/case-tip-arm-meta.json` in the deleted scratch for the attempted
arm and its verdict.

**The selftest arm the C2 module SHOULD have** (and the executor should
verify it ships): an arm over a `blob_reader` seam — the r73 module's own
selftest pattern (`tools/round73-receipt-claim-binding.py:_claim_pass`
accepts `blob_reader=` precisely so the fixpoint can be injected without
committing it). The arm injects a receipt blob whose header names the tip in
UPPER-CASE hex; the pristine module binds it (`rev.lower() == tip_lower`,
exit 0); the case-sensitive mutant flags it (exit 1). Without this seam arm,
a case-sensitive regression in the tip-claim branch ships green.

## Restoration evidence

Every mutant was applied to a scratch copy under
`/fast/scratch/hyaku/kama-r74/MT01Mutants/mutants/`; live tools were never
edited. Post-run sha256 of both live executor modules equals the mid-seat
snapshot (`live-module-sha256.txt` in this directory; both files
`2f4e473f…` and `118ae079…` unchanged). Scratch dir deleted after receipts
were copied here, per seat spec. No git/jj mutation ran anywhere; fixtures
were built by the committed builder into this seat's scratch only.
