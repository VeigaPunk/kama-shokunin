# MeasurementPlan (KamaR15.MeasurementPlan-3) — advisory, no checks run

Scope: advisory count before/after duplicate-corpus rejection, same harness; commit and causal only-delta guard measurement. No edits outside this report. No verification commands were run; every statement below is from file reads or is marked `[INFERENCE]`.

## Observed facts (read-only)

- `.ufo/waves/round-14/measure.py` `corpus_problems()` (lines 350-362): collects `name.strip()` only for dict cases whose `name` is a non-empty string, computes `unique = len(set(declared))`, and emits a problem only when `unique < MINIMUM_UNIQUE_CASES` (16). It never compares `len(declared)` with `unique`, so duplicate names are not rejected as long as at least 16 distinct names exist. This is the R1 gap.
- `run()` (lines 365-423): when `corpus` is non-empty, every case gets an `unmeasured_record` and no child is started (the `elif tool_present:` branch that calls `measure_case` is skipped). The rejection-before-children ordering already exists; only the predicate is missing.
- Cases without a usable string name are silently dropped from `declared` while still counted in `len(cases)`. This is a second fail-open path that the same predicate should close.
- `.ufo/waves/round-15/frozen/measure-before.py` is the pre-edit snapshot. Its visible structure matches round-14 `measure.py`. Manifest records `source_commit 6e348e28943849aceb08d6954dee92be48ce9ba8` and `sha256 fda61e001ca8c2533c99a1759bb4b82f3260a72fafccf72f863f3f4e3684b60d` for `.ufo/waves/round-14/measure.py`. Neither hash was recomputed here.
- `tests/ollama-corpus-guard/` does not exist yet (glob returned no matches). Fixtures must be authored to the shared schema in spec: `{name, names[], envelope: 'array'|'object', expected_rejected}`.

## Recommended repair (executable fail-closed, minimal delta)

Only `corpus_problems()` should change (plus nothing else in `run()`):

1. Build `canonical = [name.strip() for each case]`. If any case has a non-string or empty/whitespace name, add a problem naming the index.
2. If `len(canonical) != len(set(canonical))`, add a duplicate problem listing duplicated names.
3. Keep the existing `unique < MINIMUM_UNIQUE_CASES` check unchanged.
4. Keep `run()` unchanged: `if corpus:` already short-circuits before any child.

Valid unique corpora (>=16 distinct, all strings) pass through unchanged, so `retain valid unique corpus measurement` holds.

## Count plan (before vs after, same harness)

Fixture set per spec: K invalid duplicate controls (each >=16 distinct stripped names plus at least one duplicate) and V valid controls (>=16 all-distinct names). Cloned from first known passing case, with the same cases document otherwise.

Let C = number of cases per corpus (cloned from cases.json; exact C not counted here).

| Metric | Before (measure-before.py) | After (repaired) |
|---|---|---|
| Invalid duplicate corpora accepted to child stage | K | 0 |
| Child processes spawned for invalid corpora | K x C (per-case child, pending confirmation in `measure_case`, lines 211-347, not read) | 0 |
| Valid unique corpora measured | V | V |
| Child processes for valid corpora | V x C | V x C (unchanged) |

Expected "before" outcome for invalid controls is acceptance (`[INFERENCE]` from the code shape above, not executed). The "after" outcome is rejection with `unmeasured_record` entries and `verdict_exit` 1.

Measurement procedure for L1 (run once, after edits; not run by this agent):
- Run frozen `measure-before.py` and repaired `measure.py` against the same K+V fixtures.
- Count the `records` whose `detail` starts with `corpus:` and count children via the harness's per-case path.
- Confirm K invalid fixtures return `corpus:` detail in the repaired run and not in the before run.

## Commit and causal only-delta guard

- Before/after pair: `frozen/measure-before.py` (snapshot) vs `.ufo/waves/round-14/measure.py` (edited).
- Only-delta check: the diff must be confined to `corpus_problems()` and its docstring/comments. Any change in `run()`, `measure_case()`, `child_environment()`, LIMITS, or constants is out of scope and should fail the guard.
- Commit reference: `6e348e28943849aceb08d6954dee92be48ce9ba8` (from manifest, not re-resolved here).
- Old receipt under round-14 must remain byte-identical; do not overwrite it.

## Limitations

- No tool was run; no counts are observed. All counts above are structural predictions.
- `measure_case()` was not read in full, so the exact child-process count per case is unverified.
- `frozen/measure-before.py` was only read in its visible ranges; its full equality with the round-14 source was not checked. The sha256 in the manifest was not recomputed.
- Fixtures under `tests/ollama-corpus-guard/` do not yet exist and must be authored per the shared schema.
- No tools were installed or updated; no pacman, uv, or npm actions were taken.

## Tool record

- Installs/updates: none.
- Checks/tests/builds/linters/smoke runs: none (per assignment).

## Report

Report: .ufo/waves/round-15/build/advice/MeasurementPlan.md
