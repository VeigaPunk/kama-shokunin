# FalsifyAppendDuplicate: round-15 duplicate-corpus guard

Scope: `tests/ollama-corpus-guard/AppendDuplicate.json` against the final matrix predicate in `tests/ollama-corpus-guard/check.py` and the final runner predicate in `.ufo/waves/round-14/measure.py`. Read-only. No checks, tests, or installs were run. No pacman transactions.

## Evidence read

- Fixture `AppendDuplicate.json#9ADB`, four tests (ids unique; grep finds the `AppendDuplicate_` prefix only in this file).
- Matrix predicate: `check.py` `load_matrix` (139-226), `measure_test` (333-414), `grade` (478-624), `main` (714-742).
- Runner predicate: `measure.py` `load_cases` (109-128), `case_name` / `case_problems` / `unmeasured_record` (131-176), `corpus_problems` (350-364), `run` (367-425), `main` (477-489).

## Fixture check: no defect

| test | names | stripped distinct | duplicate present | envelope | expected_rejected | consistent |
|---|---|---|---|---|---|---|
| first_name_appended_array | 17 (n00 repeated at end) | 16 | yes | array | true | yes |
| first_name_appended_object | 17 | 16 | yes | object | true | yes |
| valid_unique_corpus_array | 16 | 16 | no | array | false | yes |
| valid_unique_corpus_object | 16 | 16 | no | object | false | yes |

- The minimum guard (`distinct >= 16`) is met exactly at the boundary for all four tests. The duplicate tests are not masked by the minimum check, and the valid controls are not rejected by it.
- Names contain no padding or whitespace, so strip is a no-op for this file.
- Envelopes are `array` (bare list) and `object` (`{"cases": [...]}`). Both are accepted by `load_cases` (list branch and dict-with-`cases` branch).
- Expected-boolean correspondence holds: `load_matrix` rejects an expected-true test with no duplicate and an expected-false test with a duplicate, and this file has neither.
- The runner exits and grades as the matrix expects for a rejected corpus. `run()` calls `corpus_problems` before any `measure_case` or `TemporaryDirectory`. `load_cases` only reads the file, so no child process is created on this path.
- Error text contains `duplicate case names`, so `grade` reason `DUPLICATE_REASON` matches. `observed_exit` is None on every unmeasured record, and `failed == total == len(names)`.

## Finding 1 (medium, fail-open in the runner predicate for blank-name duplicates)

Location: `measure.py` `corpus_problems` lines 352-356. Declared names are collected only when `name.strip()` is truthy.

```python
for case in cases:
    name = case.get("name") if isinstance(case, dict) else None
    if isinstance(name, str) and name.strip():   # blank names never enter `declared`
        declared.append(name.strip())
unique = len(set(declared))
if len(declared) != unique: problems.append("duplicate case names")
```

The matrix counts blank names as a distinct identity (`check.py` lines 192-193 use `set(stripped)` with no blank filter). The two predicates therefore disagree on this input class.

Concrete cases, reasoned from the source:

- `names = [n00..n15, "", ""]` (18 entries). Matrix: distinct 17, length 18, so it is a valid expected-rejected fixture. Runner: declared 16, unique 16, no duplicate problem, no minimum problem. The runner accepts the corpus and calls `measure_case` for all 18 entries, spawning wrapper children before any rejection. The matrix would grade this as failed (exit 0, not 1, marker count 18), so the harness would fail closed if such a fixture existed.
- `names = [n00..n14, "", ""]` (17 entries). Runner reports only `15 unique case names; at least 16 required` and no `duplicate case names`. The matrix would also fail this test.

Coverage gap: no committed fixture contains a blank or whitespace-only name (grep over `tests/ollama-corpus-guard/*.json`), so the committed matrix passes while the runner would spawn children for a blank-duplicate corpus. This is bounded to blank names; it does not affect `AppendDuplicate.json`.

Contract ambiguity to decide, not fixed here: `case_name` (measure.py 131-136) falls back to `case-NN` for blank names, so the runner treats blank names as unnamed rather than as duplicate identities. The matrix treats them as names. Either choice is consistent. The runner must not silently disagree with the matrix. Options are for L1 to choose: (a) count blank names in `declared`, or (b) reject blank names as invalid fixtures in both predicates.

## Finding 2 (low, out of matrix scope)

`corpus_problems` ignores non-string names entirely (line 353). Two non-string names cannot be detected as duplicates. The matrix forbids non-string names (`check.py` line 176), so no committed test exercises this. Recorded for completeness only.

## Residual risk and verification gaps

- Not run: matrix, runner, or fixture execution. The findings above are from source reading only.
- Finding 1 is not exercised by any committed fixture, so the matrix cannot currently detect it.
- Runtime behavior (child spawn count, exit codes) is inferred from the source paths listed above, not observed.
- L1 should execute the matrix once after the owners finish, and should add or decide a blank-name fixture if Finding 1 is accepted.

## Tooling

None installed or updated.
