# A08C2CacheScope — scorer cache scope (Round 62)

Axis: calibration. Finding: `_EXEC_CACHE` is keyed only by `(tip, cap)` and caches `run_bound`'s execution tuple, not the registry row's verdict/observation. Therefore every same-capability row at the same tip, including altered registry/control rows, reuses one execution result.

## Evidence

At `tools/round62-c2-counter.py:132`, `_EXEC_CACHE = {}`. `score_registry` (`:277-289`) constructs `key = (tip, cap)` (`:282`), runs only on cache miss, then returns the cached `(verdict, observed, sensitive, dead)` (`:283-287`). The cache identity excludes binding/run/pattern/verdict/observed and registry content. `controls` calls `score_registry` again on mutated registry text through `rescore` (`:292-303`); its verdict mutation is built at `:315-317`.

Reproducible in-process demonstration (scratch; imported the shipped module, replaced `run_bound` with a counted deterministic executor returning `(True, 'green-pattern', True, False)`, and used one manifest capability with two otherwise identical bound rows):

```json
{"same_cap_different_verdict":{"first_mismatches":0,"second_mismatches":1,"execution_calls_total":1,"cache_keys":[["same-tip","sources-registry"]],"cached_result":[true,"green-pattern",true,false]},"controls_rescore_after_genuine":{"genuine_mismatches":0,"mutated_mismatches":1,"execution_calls_total":1,"cache_seeded":true}}
```

The false row does **not** inherit the first row's final mismatch/verdict assessment: `score()` compares the cached execution verdict against each row's own `row['verdict']` (`:228-239`), so differing verdicts are caught. The important limitation is that the execution itself is shared, so the second row's check is not independently executed. A direct invocation of shipped `controls()` on the one-row synthetic registry returned verdict-control `mismatches: 1`, `met: false`, while `run_bound` was called once. Thus, for this counter's present verdict mutation, the cached genuine green execution still detects the changed row verdict; it does not cause this control to escape. The control is nevertheless not an independent re-execution under the mutated registry.

## Assessment

This disproves the strongest reading that a contradictory verdict is simply replaced by a cached verdict: mismatch accounting is per row. It proves same-capability rows share execution and controls reuse the genuine execution. It does **not** demonstrate the mutated verdict control passing; observed result is rejection. This leaves calibration risk if the intended semantics require each claim row/control to independently execute its bound check, especially where row-specific run/pattern semantics can vary; current row binding validation limits allowed templates, but the key itself does not encode them.

Impacted axis: calibration (execution independence / provenance of per-row coverage). No claim verdict offered.

Smallest safe correction: scope execution memoization to the complete execution identity (at least tip, cap, binding, fully substituted command, and decisive pattern), or clear/rebuild the execution cache before each control rescore so control execution is independent. Prefer the complete key for correctness; do not cache a final row verdict. Add a regression test asserting distinct executions for distinct row execution identities and that the verdict control remains rejected.

No tools installed or updated.

Demonstration ran with the assigned scratch root `/fast/scratch/hyaku/kama-r62/w/A08C2CacheScope`; temporary fixture repository was initialized there and passed `git rev-parse --show-toplevel`. Scratch was removed after preserving this report.
