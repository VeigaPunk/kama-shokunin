# R03PredicateCode — Round 58 findings

Axes: operability, calibration.

## Result

No wording/code/label mismatch found between the frozen C1 predicate and `tools/round58-c1-counter.py`'s `PREDICATE`/scoring. Freeze lines 5 and 36 of the counter both say `C1-r58 accept genuine+3/3 benign, reject 11/11 no-op, errors=0`. Freeze sentence lines 6–9 names the genuine round-56 battery, 3 behavior-preserving rewrites, 11 enumerated no-op variants, the roster-literal-intact scope and zero evaluation errors; the counter has 3 `BENIGN`, 11 `NOOPS`, and computes acceptance/rejection/error totals in lines 131–138. The no-op labels and order also correspond to the frozen list: calls-removed, if-false, unused-function, early-return, env-guard, no-op run body, no-op mutant assert, main-not-invoked, empty-loop, rebound run, try-else.

Receipt availability caveat: expected measured C1 receipt `.ufo/waves/round-58/measured/c1-build.out` is absent from the current tree listing; only `measured/c2-build.out` is present. I found no C1 measured receipt text to compare. Existing K01 report states its attempted C1 scratch run exited 1 without output/receipt, so it is not evidence of a C1 scored outcome. This is a receipt gap, not evidence of predicate divergence. No claim is made about actual frozen-tip measured values.

Finding attacks: frozen C1 predicate sentence; `tools/round58-c1-counter.py` PREDICATE and scoring/variant labels; expected measured receipt. No tools installed.
