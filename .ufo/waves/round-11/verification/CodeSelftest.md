# CodeSelftest — `measure.py` selftest review

**Scope:** static review of `kama-shokunin/.ufo/waves/round-11/measure.py`; no checks, selftests, or runtime commands were executed, and no implementation or corpus files were changed.

## Findings

### Medium — the prefix-mutation fixture reverses baseline and target bytes

At `measure.py:459-467`, the case labels `original` as the baseline and `mutated` as a one-byte change, but writes `original` into the measured tree (`:463`) and records the hash of `mutated` as the baseline (`:465`). Thus the expected `prefix-mutation` is produced by a baseline that never represented the fixture file's original contents. This is a hash-mismatch control, but not a faithful “baseline preserved, then target prefix altered” regression case.

**Smallest repair:** record `sha256(original)` and `len(original)` in the fixture baseline, write `mutated + supplement` to the measured file, and keep the expected exit `1` / finding name `prefix-mutation`.

### Medium — no truncated-prefix or missing-provenance-file cases

The only prefix case is same-length (`:459-467`); it does not exercise the shorter-than-baseline branch in the length/hash predicate at `:269-276`. The provenance loop's absent-file behavior (`:259-264`, finding `missing-file`) is also not covered by the selftest cases (`:432-537`); the absent-entry case at `:524-527` covers only crosswalk mode.

**Smallest repair:** add an independently pinned baseline whose measured file is shorter than its recorded byte extent, expecting exit `1` and `prefix-mutation`, and a provenance case with the baseline-listed file absent, expecting exit `1` and `missing-file`.

### Medium — selftest exercises helpers, not CLI behavior

`run_case` directly calls `check_provenance` / `check_crosswalk` and inspects returned Python values (`:408-423`). It does not drive `main` or the executable CLI. The `main` argument dispatch, default/explicit root and baseline handling, JSON serialization, and CLI exit propagation (`:551-580`) therefore have no coverage from `--selftest` itself.

**Smallest repair:** retain the direct helper tests, and add a small CLI-level fixture test that invokes the entry point for each mode and asserts the process exit code plus parsed JSON finding names. No such run was performed for this review.

## What is already correct

- The helper-level assertions do compare the returned exit code and the exact expected finding-name set (`:417-419`); error cases also compare the error name. The cases pin stable finding names such as `missing-field`, `prefix-mutation`, and `snapshot_tampered` alongside expected exit values (`:444-505`, `:524-537`).
- The exact-set comparison detects unexpected or renamed finding names, and the expected empty set in clean cases detects added findings. It does collapse duplicate occurrences of the same name and does not assert finding paths/counts, so it is an ID-set contract rather than a full finding-record contract.
- Fixture creation uses a `TemporaryDirectory` (`:388-405`), consistent with the documented isolation claim (`:26-27`).

## Execution / tools record

No execution or detector output is claimed; no mutant was applied, so there are no before/after hashes or killed/survived verdict. No tools were installed or updated; actual install record: none.
