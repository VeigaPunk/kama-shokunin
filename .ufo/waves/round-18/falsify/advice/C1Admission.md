VERDICT: confirm — declared before→after arms are honest and independently re-derivable from retained rows; the official exit-2 was a counter field-mismatch bug, correctly disclosed and repaired in 1c325b2; null is never counted as acceptance; coverage cannot be credited by schema failures. Numeric axis stays 8.

Scope: judge C1 (and the c1-adjacent share of C2) declared before→after and no-harm honestly from code/runs. Attack axes: (i) before→after truthfulness of the retained measurement, (ii) null/not-evaluated never laundered into acceptance, (iii) coverage counts not conflating schema failures with targeted controls, (iv) no-harm of the pushed-vs-measured diff.

## 1. The official exit-2 was the counter's own bug, not the instrument's

- `runs/c1-measure.json` records input `measure` sha256 `55b26b3b…e568c17`; pushed `.ufo/waves/round-18/c1/measure.py` is `a9577ed8…a490f`. `git diff c6dc46f..1c325b2` shows the repair: the cross-check compared top-level `misclassified` against rows where `classification == 'misclassified'`, but `controls.py:1243-1249` aggregates that count from `bucket`, and `controls.py:1062-1070` deliberately separates the axes (`rejected-targeted` classification on a control expecting `not-evaluated` → bucket `misclassified`).
- The retained before-arm row k16 is the witness and is internally consistent: `runs/c1-measure.json` `.runs.before.summary.rows.k16` = `{classification: rejected-targeted, bucket: misclassified, expected: not-evaluated}`. Re-summing the retained rows: accepted_bad = {k18,k19,k20,k21,k22} = 5, good_rejected = {k17} = 1, misclassified = {k16} = 1, uncontrolled = [] — exactly the top-level counts the instrument reported (5/1/1/0). The instrument's arithmetic was right; the counter's cross-check used the wrong field.
- Repair semantics verified: `measure.py:574-585` now sums `bucket=='misclassified'` for `bucket_source=='reported'` rows with a `classification-fallback` for older reported rows; invalid buckets still fault (`measure.py:493-498`). `build/advice/C1Measure.md` documents a selftest fixture replaying the exact k16 record (38/38 in owner's clone). The corrected counter, applied to the same retained rows, yields the declared arms with no fault.

## 2. Null is not acceptance — verified at both layers

- Gate/classification layer (`controls.py:1023-1059`, `classify_run`): `accepted` requires `tool_exit==0 AND gate_exit==0`; a null-licensed run is `tool_exit==2, gate_exit==3` → routed to `_coherent_not_evaluated` (`controls.py:994-1020`) which demands outcome `not-evaluated`, the null set exactly `{loading_envelope_graded}` and `not_evaluated_reason == 'no-loading-503-observed'`. A coherent null returns `not-evaluated`; an incoherent one returns `misclassified` — never `accepted`. A never-run/timeout bad control returns `accepted` (honest, buckets `accepted_bad`), not a rejection.
- Aggregation layer (`bucket_of`): `not-evaluated` on a bad control → `misclassified`, not `accepted_bad` and not `ok`. A bad control that "passes" because its null was coherent is impossible: `not-evaluated` is only reachable through the coherent-null path, and `spec.expect` is `not-evaluated` only for k16 which is `good=True`.
- Counter layer (`measure.py`): `'not-evaluated'` is in `CLASSIFICATIONS` but not a count key; it can only reach `misclassified` via bucket. Missing counts (`None`) are reasons in `clean_reasons` (`measure.py:624-636`), so unreported ≠ clean.
- Real-failure-dominates-null (KQ24 second clause): a real failure on a nullable check yields `failed_checks` nonempty → `_coherent_not_evaluated` requires `null` set exactly `{loading_envelope_graded}` and returns False if other nulls exist; a genuine false result fails the check normally (gate exit 1 path) → `rejected-*`. Verified by code path only; runtime gate behavior is peer seats' assignment (GateNullLicense, LiveV3).

## 3. Coverage cannot be credited by schema failure or untargeted rejection

- `controls.py:1262-1267`: a check joins `controlled` only from a non-forgery row with `bucket=='ok' AND classification=='rejected-targeted'` where the target appears in `failed_checks ∪ gate_named_checks`. Forgery rows (`kind=='forgery'`) never credit coverage — schema-floor forgeries cannot launder into `uncontrolled_checks`. Rows rejected-untargeted (k7 witness, before and after) credit nothing and increment `inconclusive`.
- Universe auto-extends: `universe |= receipt_check_ids` (`controls.py:1261`) — a new schema check a receipt carries surfaces as uncontrolled unless some good run demonstrates a targeted rejection; `INPUT_INTEGRITY=('model_unchanged',)` is subtracted and reported separately as `input_integrity_checks`.
- Retained evidence confirms 0 uncontrolled on both arms and `input_integrity_checks=['model_unchanged']` (`runs/c1-measure.json` `.runs.{before,after}.summary`), so the 0→0 is the instrument's own honest output, not the counter hiding rows.

## 4. No-harm of the pushed-vs-measured diff

`git diff c6dc46f..1c325b2 --stat` touches only `.ufo/waves/round-18/c1/measure.py`, `.ufo/waves/round-18/c2/survivors.py`, run artifacts, LOG/SOURCES/knowledge/lesson docs — no production file (tools/, tests/, registry, probe, matrix) differs between the measured revision and the pushed lane. The `identical_pairs` guard (`measure.py:795-801`) exists and the retained run had `identical_pairs:false`, so before and after graded genuinely different tool/gate pairs with frozen pins verified against `e75cf680` git blobs (`frozen_pins.*.verified:true`).

## Residual limits (not kills — declared claims stand)

1. `EXCLUDED_UNCONTROLLED = {'model_unchanged'}` (`measure.py:122`) is a hardcoded duplicate of `controls.py`'s `INPUT_INTEGRITY`, yet `measure.py` ignores the doc's own `input_integrity_checks` field that `controls.py:1274` emits (present in the retained run). If the instrument's integrity set ever changes, the exclusion silently diverges in either direction. Smallest fix: `excluded = sorted(set(raw) & set(doc.get('input_integrity_checks') or EXCLUDED_UNCONTROLLED))`.
2. The row-sum cross-check exists only for `misclassified`; a row/top-level mismatch in `accepted_bad` or `good_rejected` would pass undetected. Smallest fix: same loop for all three bucketed keys (one comparison against `row['bucket']`).
3. `identical_pairs` is warning-only (`measure.py:798-801`): frozen==current still produces a full counts table and can emit `current_clean`, presenting a vacuous before→after. Smallest fix: when `identical_pairs`, stamp it into `reasons` or require `--allow-identical` to avoid vacuous-clean.
4. `clean_reasons` does not require `good_ok`/k0 presence: a controls output omitting k0 entirely with `good_rejected` reported 0 would pass clean. Smallest fix: append a reason when `summary['good_ok'] is not True`.
5. The counter trusts the instrument's declared `expected` per row; a `controls.py` that weakens expectations while reporting self-consistent counts evades detection. The counter-owner's own report already declares this boundary; no action needed.

## C2-adjacent note (family-b composite, for the c2 admission seat)

`survivors.py` `combine_arms` changed (c6dc46f→1c325b2): `killed` now dominates `inconclusive`. Arms are the mutated tool's own targeted selftest vs a main-run decision comparison — genuinely independent detectors, and `selftest_arm` kills only on the *named* assertion with a green baseline (`survivors.py:928-953`), so a kill dominating a faulted sibling arm is the correct semantics, not a weakening. Selftest_pure covers all four orderings (`survivors.py:1735-1749`). Official run's b[0],b[1] (selftest killed + main exit 2) would correctly re-classify as killed on rerun; retained rows keep both arms visible.

## Evidence

- `runs/c1-measure.json` (exit 2, fault `before: misclassified=1 but 0 row(s) classified misclassified` — stale-field wording); per-row re-sum reproduced above.
- `runs/c1-self-mutants.json` exit 0, all three self-mutants killed; `runs/c1-counter-selftest.exit` 0; `runs/c2-survivors.json` counts 15→2 with inconclusive 2 (pre-repair).
- `sha256sum`: pushed measure `a9577ed8…`, controls `106dd98b…` (= recorded `controls` input); measured-revision measure `55b26b3b…` per runs JSON.
- `git diff c6dc46f..1c325b2` reviewed for both counters (quoted hunks above); `git log` shows `1c325b2` = "retain measured arms and repair counter classification seams" — matching the disclosed routing.
- No installs; no runtime executed (bounded to code/retained-evidence analysis; rerun ownership sits with RerunC1Current/RerunC2H executors).

Impacted axes: operability unchanged at 8 — the declared 5→0/1→0/1→0/0→0 arms are truthful, the exit-2 is disclosed could-not-evaluate and its root cause is repaired; residuals 1–4 are counter-hardening items for the next round, not falsifications of the admitted measurement.
