# kama — round 33 lesson (2026-10-24, attempt 1)

## Claims

The frozen claim set is `.ufo/waves/round-33/preregistration.json`; base lane tip `cc46980359278d0967cf65e785b41c27b8d9c36c`. Final measurements are appended after the counting commands run on committed bytes.

- **C1 calibration 7 → 7.** Under KQ39, count corrections to the round-32 C2 Scorecard statement at its writing revision `dc4258bdb08d658f1c5b15abc8378461659bd155`: three stale receipt references are false at writing; before has `false_at_writing=3 valid_corrections=0 unresolved=3 met=False`, after requires exact replacement paths and output lines, `valid_corrections=3 unresolved=0 met=True`. Do not count the whole SCORECARD or SHONEN population.
- **C2 operability 8 → 8.** The r32 gate-tip output plus three named control replays carry full source/evaluated revisions, gate/runner digests, exact argv, exit codes and output. The frozen target is `complete=0/4 → 4/4`; this is gate evidence, not endpoint health.

Pre-data controls after amendment 1: `.ufo/waves/round-33/c1/base-control-amend1.out` (`false_at_writing=3 valid_corrections=0 unresolved=3 met=False`, exit 1) and `.ufo/waves/round-33/c2/base-control-amend1.out` (`complete=0/4 missing=4 invalid=0 met=False`, exit 1). The counters and after predicates were not changed after these controls.

## Gate

New row opened this round: **S194**, own-work tier A, `tools/gate-registry-check.py` at `c4c46ad5b87d8b63f03e200a7b13eb8eeff46279`, accessed 2026-10-24. Exact source location: docstring “Contract”, lines 15–16. Verbatim quote: “A path is ``registered`` iff it occurs in a cell of a row of such a table.” (17 whitespace-delimited words.) S194 supersedes S193 only for the precise anchor and quote; the five-column registry-row scope is unchanged. The new row is mined by this lesson and the SKILL round-33 replay instructions.

Reject-side sample reopened this round: **S104**, the standing rejected claim that `git fsck` green proves local completeness. At `https://raw.githubusercontent.com/git/git/v2.56.0/builtin/fsck.c`, `mark_object` returns for `is_promisor_object()` before the `HAS_OBJ` check (lines 143–149); the rejection remains correct. S104's existing row is unchanged. The current round's non-author spot-check is recorded with the final claim verdicts once received.

**Non-author spot-check — `CJ-kama-r32` (2026-10-24).** S194 admit: agree; the quote and 17-word count match lines 15–16 at the pinned c4c46ad5 revision, scoped only to five-column registry registration (not endpoint health or instrument correctness). S104 reject: agree; Git v2.56.0 `builtin/fsck.c` lines 143–151 return for a promisor object before the `HAS_OBJ` check, so fsck green does not prove local completeness.

One bounded local source search: exact gate definition + reject-side re-open; identified 2 registered source candidates, screened 2, included 1 new row (S194), reopened S104 without a new row, excluded 0. Stop after the deciding fragments; no vendor/API or endpoint claim was sought. Search-log supplement is appended in `corpus/SOURCES.md`.

## Mistakes

| # | class | evidence | captured-by | fix (shown able to fail) |
|---|---|---|---|---|
| 1 | receipt-lineage contradiction | The filed round-32 report groups `c2r/c2r-tip.json` with receipts measured at `967d88528c1d`; the JSON `tip` is `dc4258bdb08d658f1c5b15abc8378461659bd155`, and the file was first added by `967d88528c1d83535563f971863f7855f76b4849`. | none — no criterion required the report's asserted evaluated revision to match each receipt's embedded revision and adding commit. | Append the correction to SCORECARD/LOG/this lesson and keep the filed report byte-intact. KQ43 requires distinct evaluated-revision and receipt-commit fields; the prior sentence is the red case. |
| 2 | self-assessment/reference drift | SCORECARD C2, written at `dc4258bdb08d658f1c5b15abc8378461659bd155`, cites `c2/controls/*-v2.out`; `thin-row-v2.out`, `empty-exit-v2.out`, and `nonexistent-path-v2.out` do not contain their named defect lines. The do-nothing receipt is `.ufo/waves/round-33/c1/base-control-amend1.out`. | KQ39 — every checkable self-assessment statement is evaluated at its writing revision. | Append exact replacement mappings to SCORECARD; the frozen counter remains red at the r32 base and only reaches `unresolved=0` when all three replacements resolve to the actual defect lines. |
| 3 | source-quote location/count | Round-32 lesson Gate says S193's quote is at line 22 and has 16 words; source at the pinned commit is lines 15–16 and has 17 whitespace-delimited words. | SOURCES contract v1 rule 1 — the Gate must record a located quote; the earlier location/count did not match the opened source. | Leave S193 and the filed r32 lesson unchanged; append the correction here and a superseding S194 row. |
| 4 | incomplete run receipt | R32 `gate-tip.out` and v2 control outputs omit inline `EXIT_CODE`; the clean receipt also omits its evaluated revision. | none — no existing criterion bound the gate's output, exit, evaluated revision and receipt-adding commit together. | Add KQ43 and replay four cases with `SOURCE_REV`, `EVALUATED_REV`, `GATE_SHA256`, `RUNNER_SHA256`, `EXIT_CODE`, exact argv and captured streams; the committed audit replays source bytes and rejects missing/changed fields. |
| 5 | fixture contamination | `.ufo/waves/round-33/c2/diagnostic-attempt1/controls/empty-exit-map.out:12-14` records the intended `empty-exit-map` plus an unintended `missing-path:tools/measure.py`; the entry-cell path token caused the second finding. | The initial output matcher checked for the expected substring but did not reject an extra defect line. | The final fixture uses the path-free entry `python3`; the runner now requires the exact stdout line set. The diagnostic output is retained as the red case; the corrected final receipt contains only the named defect. |
| 6 | output-root misroot | The `edit MV` destinations for the four diagnostic outputs appeared under fleet `.ufo/waves/round-33/c2/diagnostic-attempt1/`; the lane wave context requires absolute lane destinations. Before cleanup the fleet glob listed all four; after recovery it returns path-not-found, while the lane path contains byte-identical files. | Wave context rule: every `Report:` path is relative to the lane root and must be written under the lane. | `cp -p` each file to the same lane-relative path, verify all four with `cmp` (each exited 0), then remove only those four fleet copies. The preserved lane receipts are under `.ufo/waves/round-33/c2/diagnostic-attempt1/`. |
| 7 | audit replay internal error | `.ufo/waves/round-33/c2/after-data-tip.out:1-11` ends `TypeError: Strings must be encoded before hashing`, exit 1; no `R33_GATE_RECEIPT_AUDIT` verdict was emitted. | KQ25 — a runtime error remains visible and non-passing; it is not a semantic kill or claim result. | Hash committed runner blobs as bytes and validate the historical runner digest; preserve the failure output, then re-run the unchanged 4/4 predicate at the committed fix tip. |

## Routed-defect dispositions

1. Receipt-lineage contradiction — corrected by appended provenance; no rewrite of `.ufo/reports/round-32/kama.md`.
2. Three mislabeled v2 controls — old bytes retained and explicitly superseded by exact `thin-v2.out`, `noexit-v2.out`, and `badpath-v2.out` references.
3. S193 quote location/count — corrected by appended lesson text and new S194 row.
4. Gate receipt inline exit/revision details — replayed into the round-33 four-receipt set; the final audit is the C2 counter.

The initial capture under `diagnostic-attempt1/` is not a scored C2 receipt set. Amendment 1 corrected the fixture and exact-output oracle before the C2 audit was run; it did not change the frozen target or expected finding labels.

## Round-33 measured results and frontier census

- **C1 at evidence tip `1c881bbd3e1cce5f0b01f1afc6d3229866cbe712`:** `R33_CLAIM_AUDIT false_at_writing=3 valid_corrections=3 unresolved=0 legacy_mislabels_at_tip=3 met=True`, exit 0 (`.ufo/waves/round-33/c1/after-evidence-tip.out`). The three old receipts still exist unchanged; the active correction table points only to the three proper output receipts.
- **C2 at evidence tip `1c881bbd3e1cce5f0b01f1afc6d3229866cbe712`:** `R33_GATE_RECEIPT_AUDIT complete=4/4 missing=0 invalid=0 met=True`, exit 0 (`.ufo/waves/round-33/c2/after-evidence-tip.out`). The four complete outputs are in `.ufo/waves/round-33/c2/final/`; `SOURCE_REV` is the pinned r32 gate tree `967d88528c1d83535563f971863f7855f76b4849`.
- The earlier C2 audit attempt at data tip `88331197a7de5fcc171bc7290fdd7beb43487a63` raised the recorded TypeError and is not counted. The corrected audit re-ran at evidence tip `1c881bbd3e1cce5f0b01f1afc6d3229866cbe712` without changing the target; the non-author spot-check is recorded in `## Gate` above.
- **SOURCES census:** base `cc46980359278d0967cf65e785b41c27b8d9c36c` → end 194 rows (193 → 194), tier A 188 → 189, B 2 → 2, C 3 → 3, mined 174 → 175, queued 8 → 8, rejected 11 → 11. The exact `census` counts are `.ufo/waves/round-33/sources-start-count.out` and `sources-end-count.out`; the required `validate` runs are `census-start.out` and `census-end.out`, both exit 0. S194 is the only added row; existing rows and status/recheck/used-by cells are unchanged. No frontier row or `knowledge/` entry advanced.
