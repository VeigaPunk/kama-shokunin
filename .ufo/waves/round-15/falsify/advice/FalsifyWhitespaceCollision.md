# FalsifyWhitespaceCollision — round-15 falsification

Scope: `tests/ollama-corpus-guard/WhitespaceCollision.json`, the runner predicate in
`.ufo/waves/round-14/measure.py` (`corpus_problems`, `run`, `case_name`), and the
matrix/grade predicate in `tests/ollama-corpus-guard/check.py` (`load_matrix`,
`measure_test`, `grade`). Read-only. No checks, tests, or runners executed.

## Verdict

No fail finding for this fixture. The committed fixture and both predicates agree.

## Evidence by claim

1. **Negatives: >=16 stripped distinct, duplicate present.**
   - `WhitespaceCollision-array` and `-object`: 17 entries each (`n01`..`n16` plus `" n04 "`).
   - Stripped distinct = 16 (`" n04 ".strip() == "n04"` collides with `n04`).
   - `check.py load_matrix` (lines 192-206): distinct 16 >= `MINIMUM_UNIQUE_CASES` 16; `expected and distinct == len(stripped)` is false, so the negative is accepted as a rejected control.
   - Runner `corpus_problems` (measure.py 350-364): `declared` = 17 stripped names, `unique` = 16, `len(declared) != unique` appends "duplicate case names"; `unique` 16 is not below minimum, so only the duplicate reason is raised. Message text matches `DUPLICATE_REASON`.

2. **Valid controls: distinct.**
   - `WhitespaceCollision-valid-array` / `-object`: 16 distinct names, exactly at the minimum boundary.
   - `load_matrix`: distinct 16 == len 16, `not expected and distinct != len` is false; accepted as valid control.
   - Runner: `declared` 16 == `unique` 16, no corpus problem; `run` takes the `elif tool_present` branch and measures 16 cases.

3. **Rejection occurs before any child process.**
   - `run` (measure.py 374-393): `corpus_problems` is computed before the `tempfile.TemporaryDirectory` loop; on corpus problems every case becomes `unmeasured_record(..., None)` and `measure_case` (the only `subprocess.run` site) is never reached.
   - Grade side (check.py 528-575) enforces marker count 0 and audit `subprocess.Popen`/process events 0 for rejected controls; the record fields (`observed_exit` null, `failed == total == 17`, `total == 17`, `passed == 0`, exit 1, `verdict_exit` 1) are all produced by the runner's corpus branch.

4. **Envelope correspondence.**
   - `array`: `measure_test` writes a bare list; runner `load_cases` accepts a list (measure.py 120-121).
   - `object`: `measure_test` writes `{"cases": [...]}`; runner accepts `document["cases"]` (measure.py 122-123).
   - `load_matrix` restricts `envelope` to `array|object` and `expected_rejected` to a real bool, so no envelope/boolean mismatch can reach grading.

5. **Expected boolean correspondence.**
   - Rejected: `grade` requires exit 1, `error` containing "duplicate case names", zero children, zero spawns.
   - Valid: `grade` requires exit 0, `passed == total`, marker count == total, Popen count == total. These rely on the real classifier passing 16 clones of the template; not executed here.
   - Stripping is consistent end to end: `check.py` counts on `item.strip()`; runner counts on `name.strip()`; `measure_case` writes the unstripped `" n04 "` as the record name, which does not affect the decision.

## Residual observations (not fail findings; outside the stated guard scope)

These are bounded observations, not proposed features.

- **R-a. Unnamed/non-string cases bypass `declared`.** `corpus_problems` drops any case whose `name` is not a non-empty string after strip. `case_name` then falls back to `case-NN` by index. A corpus can therefore carry a literal name `case-05` at one index and an unnamed case at index 5 with no duplicate reported. The record name collides, but no measured value depends on record names. The check.py matrix cannot exercise this: `load_matrix` requires non-empty string names, so no matrix entry generates it. Scoped out by the "guard ONLY adds" rule.
- **R-b. Duplicated constants.** `MINIMUM_UNIQUE_CASES` (16) and `PER_CASE_CHILD_TIMEOUT` (30) are hard-coded in both `check.py` and `measure.py` rather than imported. The values agree today; drift is not caught by any gate.
- **R-c. Strip semantics are Python `str.strip()`.** Code points such as U+200B (zero-width space, not `isspace`) are not stripped, so `"n04\u200b"` counts as distinct. This is the Unicode-duplicate lane's domain; this fixture does not exercise it.

## Tooling

No installs or updates performed. No pacman transactions (host-wide pause in effect).
