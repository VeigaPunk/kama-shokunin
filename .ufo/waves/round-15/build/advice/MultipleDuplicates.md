# MultipleDuplicates (KamaR15.MultipleDuplicates-3) — advisory, no checks run

Scope: author `tests/ollama-corpus-guard/MultipleDuplicates.json` per the shared fixture schema. No edits outside the assigned file and this report. No verification commands were run; statements are from file reads or marked `[INFERENCE]`.

## Files changed

- `tests/ollama-corpus-guard/MultipleDuplicates.json` (new) — literal shared-schema fixture matrix, 4 scenarios, no generator or execution.

## Fixture contents

Two invalid duplicate controls (both `expected_rejected: true`), exercising the actual duplicate-name policy:

- `MultipleDuplicates_tail_n01_n03_n01_array` — `envelope: "array"`; names `n00`–`n15` plus literal tail `n01`, `n03`, `n01` (19 entries).
- `MultipleDuplicates_tail_n01_n03_n01_object` — same names under `envelope: "object"` to cover the `{"cases": [...]}` document form.

Each invalid control yields exactly 16 distinct stripped names — at the old `MINIMUM_UNIQUE_CASES = 16` floor, so the pre-repair guard (`unique < 16` only, `.ufo/waves/round-14/measure.py` `corpus_problems`) cannot catch them. The duplicates are multi-valued: `n01` appears 3× and `n03` 2×, distinguishing this lane from single-duplicate lanes.

Two valid counterparts (both `expected_rejected: false`), duplicates removed:

- `MultipleDuplicates_valid_distinct16_array` — `n00`–`n15`, `envelope: "array"`.
- `MultipleDuplicates_valid_distinct16_object` — `n00`–`n15`, `envelope: "object"`.

All `names` values are literal JSON arrays of strings; ids use the `MultipleDuplicates` prefix; no malformed-schema scope (every generated case will carry a string `name`, so only the duplicate predicate is exercised).

## Grounding

- Shared schema (`{name, names[], envelope: 'array'|'object', expected_rejected}`) confirmed in `.ufo/waves/round-15/build/spec.json` context and `build/advice/MeasurementPlan.md`.
- Guard canonicalizes `name.strip()` before counting (measure.py lines 353-356), so literal `nNN` strings need no whitespace handling here; whitespace-collision coverage belongs to sibling fixtures.

## Limitations

- No verification commands run (per assignment); JSON validity and guard behavior unverified by execution.
- Sibling fixture files could not be inspected for style (directory did not exist when this file was authored); naming pattern `n00`–`n15` matches the dispatch spec shared with sibling lanes.
- Old-runner (`measure-before.py`) behavior on these fixtures is an unexecuted structural prediction, not an observed result.

## Tool record

- Installs/updates: none.
- Checks/tests/builds/linters/smoke runs: none (per assignment).

## Report

Report: .ufo/waves/round-15/build/advice/MultipleDuplicates.md
