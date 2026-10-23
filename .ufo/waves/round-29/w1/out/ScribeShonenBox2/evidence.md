# Evidence — SHONEN.md box 2 / line 8

## Verified correction

The source line is still marked `[~]` and labels its prose an “Author assertion”; the correction only repairs the round-17 controls summary. The proposed line retains the `[~]` box, author attribution, the lane-owned-control scope, and the explicit “no non-author mark” qualification. It adds no `[x]` mark.

- Current `SHONEN.md:8` says “8 bad fake-server shapes rejected, frozen pair accepted 6.” The full line is retained in the proposed draft.
- `tests/llamacpp-live/controls.py:17-18` identifies K1–K8 as the round-17 controls with unchanged shapes. Definitions at `:525-578` show K1–K5 and K7–K8 as server behaviors; K6 is registered `kind='inprocess'`, uses the good K0 shape, and injects a `RuntimeError` into teardown (`:558-564`). Thus there are seven bad server shapes plus a harness-fault control, not eight bad server shapes.
- `.ufo/waves/round-17/runs/controls-frozen.json:2` records `accepted_bad: 6`. Five accepted controls with receipts are K1, K2, K4, K5 and K8 (the per-control outcomes are recorded in the `controls` array). K6 is `accepted: true`, `escaped: true`, `receipt_written: false`, `tool_exit: 4`, and `gate_exit: null` at `:118-135`; it is the receiptless escape, not an accepted bad receipt. K3 is marked `inconclusive: true` at `:58-73`.
- `.ufo/waves/round-17/falsify/advice/ShonenProvince.md:39-47` independently names the population distinction, records that the current result rejected K1–K8, describes the frozen six and K3 as inconclusive, and recommends the revised wording. `.ufo/waves/round-28/residual/advice/ResSelfAssessment.md:51-60` routes this as a pre-existing, unrepaired imprecision and states the same breakdown.

## Provenance and limits

Evidence is from static reads of the lane files named above; no controls suite, gate, test, build, lint, or server was executed for this scribe item. No install was made. The frozen artifact is the round-17 run at `.ufo/waves/round-17/runs/controls-frozen.json`; the assignment's “tests/llamacpp-live/controls-frozen.json” location was not present in the `tests/llamacpp-live/` directory listing. The round-17 run artifact is the located frozen evidence source.

The proposed SHONEN line and LOG entry are drafts for L1 integration, not edits to `SHONEN.md` or `LOG.md`. No product, tracked lane, judge, or sibling files were changed.
