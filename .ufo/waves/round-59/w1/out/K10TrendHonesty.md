# K10TrendHonesty — trend-claim falsification

Axes: **operability** (C1) and **calibration** (C2; assigned low axis, 7). Advisory falsification only; a wave vote is not outside closure.

## Verdicts

| Trend | Verdict | Evidence and limit |
|---|---|---|
| Expansion | **Unchanged / not claimed.** | C1 is a checker-hardening claim, not a new capability or demonstrated knowledge expansion. C2 changes scorecard evidence derivation, not knowledge/capability surface. Round-58 lesson describes a battery-execution knowledge entry as a candidate expansion whose admission depended on closure; it does not authorize attributing current-round expansion. No independent closure evidence supplied here. |
| Quality | **Improved narrowly, subject to frozen counter result.** | C1's frozen output reports genuine 1/1, benign 3/3 and no-op rejection 16/16, errors 0, `met=True` at `aca8d0067ea25627c5015c2193c843965148bc8e`; it explicitly includes per-leg ignored/wrong expected, mutant-result ignored, duplicate label and decoy-counter variants. This addresses round-58's `unlisted-noop-survivors` and `counter-controls-blind-to-mutants` lesson for these enumerated cases only. This is not a global quality or arbitrary-mutant guarantee; harness confinement is in-process and the lesson acknowledges it is not a sandbox. |
| Discernment | **Unchanged; no progress claim.** | Frozen context states external S517/S518 spot-check is not recorded. The round-58 lesson's proposed set is admit S517, admit S518 after checking S512, and no new carried reject; the latest committed closure is r57 `rejected-honest-stop`, and no r58 closure row exists. Local advisory consensus cannot substitute for non-author outside closure. |

## Counterexample / calibration falsifier

Attacked clause: frozen C2 calibration claim requires a runnable checker to derive current lane evidence count and fleet closure verdict from named refs, with each independent field mismatch rejected; success binds exact lane tip and fleet revision. The supplied post-measurement output says `rows=44 mismatches=0 met=True`, `maxN=57 manifest=rejected-honest-stop` at fleet `3f3dd97345ef1aedfdaec818c9e58675d4f41e3f` (`controls/c2-after-current-head.out`). But this apparent successful recalculation has no corresponding external r58 closure: latest closure is r57 rejected-honest-stop. Therefore it establishes internal agreement with present committed evidence, not outside calibration/discernment, and must not be presented as an S517/S518 verdict or closure progress. The measured C2 ref in the assignment used fleet revision `58cffd1f42723048bcfe48eb0bc2f346caa9b77f`; do not conflate that with the later current-HEAD recheck.

Evidence commands and outputs actually available in committed control artifacts (not rerun by this critic):
- `python3 tools/round59-c1-counter.py --repo <lane> --tip aca8d0067ea25627c5015c2193c843965148bc8e --work <scratch>` — recorded candidate-final output: `genuine=1/1 benign=3/3 noop_rejected=16/16 errors=0 met=True`; all 16 named N01–N16 reject exit 1; genuine/benign exit 0. Exit of this top-level recorded invocation is not stated in the `.out` file, so not independently asserted here.
- `python3 tools/round59-c2-counter.py --repo <lane> --tip 2c7443abb8d6edb8a5b0f91dfee9f81b824f6d35 --fleet-ref HEAD` — recorded `controls/c2-after-current-head.out`: `rows=44 mismatches=0 met=True`; individual counters all zero. The artifact reports fleet ref `3f3dd97345ef1aedfdaec818c9e58675d4f41e3f`; invocation exit is not stated there.
- Round-58 lesson, Mistakes: `counter-controls-blind-to-mutants`, `unlisted-noop-survivors`, and `post-freeze-tool-change` document why finite controls and exact frozen predicates matter. Its Gate explicitly says dispatched seat findings are advisory.

## Smallest safe correction

Keep all scores and discernment unchanged; report C1 only as a bounded checker-quality improvement against the frozen finite set, and C2 only as an internal current-evidence consistency result. Do not claim expansion or outside closure. For any calibration/discernment progress, require the separately recorded non-author S517/S518 spot-check and matching fleet closure record; do not infer either from the wave vote or counter green.

No install/update performed. No source edits, fixture commands, counters or campaign tools were run by this critic.