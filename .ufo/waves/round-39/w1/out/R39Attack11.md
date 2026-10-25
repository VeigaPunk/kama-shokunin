# R39-11 — Census outputs and exit

## Axes
Calibration; coverage.

## Findings

- Census row count is corroborated independently from the working `corpus/SOURCES.md` and the frozen base: 203 at base `6a4afdfe48b0b54239d127761d21a5cf21b5b0ea`, 204 at the tip; S472 is absent at base and present once at tip. The recorded census transition is therefore +1 row, consistent with the cited claim evidence.
- The recorded post-change census tier totals (A=195, B=6, C=3) and statuses (mined=185, queued=8, rejected=11) match counts independently tallied from the tip registry. The captured `census-end.out` has 94 lines: 93 W04 cross-scope duplicate-URL warnings plus one `ok` summary. The corresponding `validate.out` has the same 93 warnings and final `ok`; the final path differs because one output used the copied validation tree. W04 warnings are not themselves a clean-registry failure per `sources-census.sh` header, which states warnings do not affect exit status.
- `census-start.out` records the initial root-level census command exiting 2 because `kama` was unavailable in the scratch-root fleet config. This is an environment/selection failure, not evidence of an invalid registry. Later file-scoped census is explicitly recorded with exit 0 in `claim-after.out`; the source script documents 2 for usage/environment/missing registry and 1 for E/overdue findings.
- Both no-op controls are negative as required: `c1-noop.out` gives admit=0, reject=0, 203 rows, `met=False`, exit=1; `c2-noop.out` gives all three coverage components 0, `met=False`, exit=1. Positive claim evidence records C1’s admit/reject/new source and C2’s README pointer, amendment, and S472, and reports both predicates met. Frozen preregistration explicitly fixes those predicates before data.

## Assessment

No counterexample to C1 calibration or C2 coverage found in the inspected census/exit artifacts. The strongest caution is provenance: the initial fleet census is not a successful census result, and its exit 2 must not be read as a data defect. The successful post-change evidence is file-scoped and its counts agree with the working registry. No predicate change recommended.

Evidence: `.ufo/waves/round-39/assimilation/{census-start.out,census-end.out,validate.out,claim-after.out,claim-after-initial.out,c1-noop.out,c2-noop.out,preregistration-frozen.json}`; `scripts/sources-census.sh` lines 16–18, 31–33; working `corpus/SOURCES.md` and base commit registry.