# FalsifyDistantDuplicate: scoped findings

Scope: `tests/ollama-corpus-guard/DistantDuplicate.json`, the final duplicate predicate in `.ufo/waves/round-14/measure.py` (`corpus_problems` 350-364, `run` 367-425), and the matrix grader in `tests/ollama-corpus-guard/check.py` that consumes the fixture (`load_matrix` 139-226, `measure_test` 333-414, `grade` 478-624). No checks, tests, or installs were run. Read-only static analysis.

## Verdict

No falsifying defect found for the distant-duplicate case. The fixture meets its stated contract, and the runner predicate rejects a duplicate at any distance before any child is staged or spawned. One low-severity gap exists in the runner predicate for blank names. The fixture does not exercise it and it produces no false pass.

## Fixture contract (DistantDuplicate.json)

| Row | Envelope | Entries | Stripped distinct | Expected | Check |
|---|---|---|---|---|---|
| Array32FirstRepeatedAtEnd (lines 3-40) | array | 33 (n00..n31 + n00) | 32 | rejected | 32 >= 16; 32 != 33 so the duplicate-control check (check.py:201-206) is satisfied |
| Object16FirstRepeatedAtEnd (lines 43-64) | object | 17 (m00..m15 + m00) | 16 | rejected | 16 >= 16 (exactly at minimum); 16 != 17 |
| ValidArray32Unique (lines 67-103) | array | 32 (n00..n31) | 32 | accepted | 32 == 32, passes check.py:207-211 |

- The matrix validator (check.py:192-211) rejects any row where `expected` disagrees with `distinct == len(stripped)`. All three rows agree with it.
- Names are unique across the matrix: the only `DistantDuplicate.*` test ids are the three above (grep). `seen` in `load_matrix` also fails closed on collisions.
- JSON is well-formed: three objects, closing `]` at line 104.

## Predicate against distant duplicates

- `corpus_problems` (measure.py:350-364) uses `set()` over stripped names. Duplicate detection is therefore independent of index distance. Array32 places its duplicate at indices 0 and 32, and Object16 at 0 and 16. Both are caught by `len(declared) != unique` (358-359).
- Duplicate rejection is evaluated before the minimum check and before the staging fork. In `run()` the corpus gate (374-380) precedes the only child path (381-385, `subprocess.run` at 240 inside `measure_case`). A non-empty corpus produces only `unmeasured_record`s with `observed_exit: None`.
- Object16 has exactly 16 unique names, so `unique < 16` is false (360). The rejection in that row is attributable to the duplicate predicate alone. The minimum predicate does not contribute.
- Arithmetic in the grader matches the runner: `total = len(names)` (check.py:335) counts duplicate copies. Runner `failed = len(records) = len(cases)` (runner:395-396) equals total for rejected rows, so `failed != total` (check.py:545) cannot be masked.

## Grader correspondence for rejected rows (check.py:528-575)

- Requires runner exit 1, `verdict_exit` 1, `error` containing `"duplicate case names"`, `passed == 0`, `failed == total`, `total == total`, `tool_present` True, every record with `observed_exit` null, classifier marker count 0, audit process events 0, and audit Popen events 0.
- The audit hook (launcher, check.py:257-286) sees the runner's own `subprocess.Popen` / `os.*` events. A runner that spawned a child before the corpus gate would produce Popen events and a non-zero marker, and the row would fail. This is the discriminator for "before ANY child process".
- The valid row requires Popen events equal to total and markers equal to total (check.py:596-604), so a runner that rejects everything would fail it.

## Mutant discrimination (static reasoning, not executed)

| Mutant runner | Caught by |
|---|---|
| Adjacent-only duplicate comparison | Both rejected rows: duplicate not adjacent, accepted, exit 0 fails 1 |
| Scan first 16 entries only | Array32 (index 32) and Object16 (index 16) missed |
| Only triples count as duplicates | Both rejected rows are pairs |
| Reject every corpus with duplicate reason | ValidArray32 row: passed 0 != 32 |
| Duplicate check placed after first child | Rejected rows: Popen events and markers non-zero |
| Dedupe then measure unique names | Rejected rows: total/failed 32 != 33 |

## Findings

### F1 (Low): blank-name cases are excluded from the duplicate predicate but counted by the matrix validator

- `corpus_problems` (measure.py:353-355) only appends names where `isinstance(name, str) and name.strip()`. Blank or whitespace-only names are dropped from `declared`, so two blank-named cases are never reported as duplicates.
- `load_matrix` (check.py:192-211) does not drop them. `"".strip()` is a distinct value, so a row with two blank items is counted as a duplicate and expected rejected.
- Effect: a matrix row like `names = [16 distinct, "", ""]` would be expected rejected. The runner would measure it, exit 0, and the grader would fail the row. That is a fail-closed harness error, not a false pass.
- Effect on production: a `cases.json` with 16 named cases plus two blank-named cases would be measured, not rejected. This contradicts the docstring phrase "duplicated corpus fails ... before any child is spawned" if blank names are read as duplicates.
- Not covered by DistantDuplicate.json. No fixture in this file triggers it. Scope note only. No change is proposed here.

### F2 (Informational): Object16 does not isolate the minimum boundary

- Object16 sits exactly at 16 unique names, so it does not discriminate an off-by-one in the minimum (`unique < 16` vs `unique <= 16`). The duplicate reason would still appear in `error`, so the row would pass under such a mutant.
- This is expected, because the row is meant to test duplicates. The boundary belongs to other rows (`ValidBoundaries.json`, not read here).

## Residual risk and verification gaps

- No execution. Every line-level claim is static-read and should be confirmed by L1's single post-wave run of `check.py --selftest`.
- `audit` coverage is limited to the prefixes listed at check.py:79-85. Other process-creation APIs are not observed (LIMITS already says so).
- Unicode canonicalization (NFC vs NFD) is not applied by either predicate. Not exercised by this fixture; owned by the Unicode lane.

## Tooling

No tools installed, upgraded, or removed. No pacman, uv, or npm actions.
