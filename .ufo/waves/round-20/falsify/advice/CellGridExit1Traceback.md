VERDICT: confirm - the pinned grid-exit1-traceback row matches frozen=rejected/current=error; both arms ran, and classification is not based on exit status alone.

Findings (severity): none; no discrepancy found.

Evidence:
- `.ufo/waves/round-20/build/out/CensusHarness/error-injection-cells.json:2` pins `id=grid-exit1-traceback`, `mode=crash`, expected frozen class `rejected`, expected current class `error`.
- Exact row `.ufo/waves/round-20/runs/0957ce61/error-pair.stdout:13-21` reports frozen=`rejected`, current=`error`, both expected classes as pinned, `frozen_witness_match=true`, `frozen_ran=true`, and `current_ran=true`.
- `.ufo/waves/round-20/build/out/CensusHarness/error-verdict-census.py:164-179` shows `classify_grid` does not use its `rc` variable: it derives verdict from structured stdout (`baseline`/row `status`), or classifies a missing structured result as `error` only when traceback text appears in stderr; otherwise it returns `could-not-evaluate`. `.ufo/waves/round-20/build/out/CensusHarness/error-verdict-census.py:313-336` records the two arm results and run flags separately.
- Paired-run wrapper exit evidence is `.ufo/waves/round-20/runs/0957ce61/error-pair.exit:1` (`exit=0`); this is not used to infer either cell verdict.

Residual risk: the paired row records classifications and run flags, not per-arm raw output; the classifier excerpt establishes the non-exit-only logic. The matrix was not rerun, as requested.

Verification gaps: `xd://lsp` is unavailable in this environment (`No such tool`, only `ast_edit` and `debug` mounted), so no LSP-backed checks were possible. No other verification was run.