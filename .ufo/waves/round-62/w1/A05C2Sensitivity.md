# A05C2Sensitivity — C2 sensitivity predicate

## Counterexample and finding

The sensitivity leg can be false for a non-empty decisive pattern, and is not logically vacuous. The captured `master:tools/round62-c2-counter.py` implements (lines 269–271):

```python
mut = out.replace(tpl['pattern'], MUT)
sensitive = not (tpl['pattern'] in mut and rc == 0 and not dead)
```

Let `P` be `tpl['pattern']`, `O` be `out`, `M` be `MUT`, `R` mean `rc == 0`, and `D` mean `dead`. Boolean algebra gives:

` sensitive = not ((P in O.replace(P, M)) and R and not D)`

so it is false exactly when `(P in O.replace(P, M)) ∧ R ∧ ¬D`; it is true when `P` no longer occurs in the mutated text, the run fails, or the target is dead. For example, `P='a', O='a', M='__kama_mut__', R=True, D=False` yields mutated text `__kama_mut__`, which still contains `'a'` (in `kama`), hence `sensitive=False`. Thus replacing the matched occurrence does not guarantee removal of the pattern: the replacement itself can contain the pattern. A second demonstrated case, `P='a', O='__kama_mut__'`, also remains false and shows repeated replacement may create/retain pattern text.

Conversely, `P='ab', O='aab'` mutates to `a__kama_mut__`, contains no `'ab'`, and makes sensitivity true. Therefore the test is not always false either. The implementation measures whether the literal pattern is absent after global replacement, not whether the emitted verdict flips under a semantically faithful mutation. This can be misleading whenever the chosen `MUT` contains the decisive pattern (or creates it at a boundary), even though the specific observed `P='a'` case is an actual false result.

## Smallest safe correction

Use a replacement token guaranteed not to contain the decisive pattern, and assert the verdict changes when recomputing the mutated predicate; alternatively choose a token dynamically guaranteed not to contain `P` and test `P not in mutated_output` directly. Keep `rc` and target liveness fixed for the counterfactual. This makes sensitivity correspond to flipping the pattern-dependent verdict rather than incidental substring occurrence in a hard-coded marker.

Impacted axis: calibration (C2 sensitivity evidence; potential false characterization of whether a bound check depends on its decisive output pattern).

Evidence receipt: `.ufo/waves/round-62/w1/out/A05C2Sensitivity/sensitivity-probe.txt`.
