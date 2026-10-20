# CorpusIdentity: case-name identity advice (round-15, read-only)

Scope: compare the original case names in `tests/ollama-evidence/cases.json` with the runner's displayed case name and the stripped corpus identity used by the guard. No execution; no files edited besides this report.

## Sources read

- `tests/ollama-evidence/cases.json`: top-level array of 51 fixtures. Every `name` is a string. All names are ASCII, lowercase snake_case, with no leading or trailing whitespace. There are 51 unique raw names, 51 unique after `ascii_downcase`, and 51 unique after `-`→`_`. The corpus has no duplicates and no case-only or separator-only collisions.
- `.ufo/waves/round-14/measure.py` (runner, path is the existing historical runner):
  - L60–67: `MINIMUM_UNIQUE_CASES = 16`.
  - L109–128: `load_cases` accepts a top-level array or an object with a `cases` array; it parses with `json.loads`.
  - L131–136: `case_name` returns the raw `name` unchanged when `name.strip()` is truthy; otherwise it returns `case-NN`.
  - L350–362: `corpus_problems` appends `name.strip()` for every str `name` with a non-empty strip, then fails if `len(set(declared)) < 16`.
  - L368–383: the guard runs before the temp directory and the per-case child loop. Ordering already satisfies "before any child process".
- `.ufo/waves/round-15/frozen/measure-before.py`: the same lines (L133–136, L353–358, L66) match the round-14 runner by grep. It is the frozen snapshot and was not edited.

## Which equivalence is actually guarded

1. **Identity key:** `str.strip()` applied to the `name` value, then exact code-point equality through a Python `set`. Nothing else.
2. **Case:** significant. `Foo` and `foo` are distinct. There is no `casefold` or `lower`. Current data has no folded collisions.
3. **Unicode:** no normalization.
   - NFC and NFD spellings of the same text are distinct.
   - Compatibility forms (fullwidth, ligatures) are distinct.
   - Only leading and trailing characters that Python `str.isspace()` treats as whitespace are removed. Interior whitespace is significant.
   - Zero-width characters (U+200B, U+FEFF) are not `isspace()`, so they are not stripped. [INFERENCE from Python `str.isspace` semantics; not executed.]
   - Current data is all ASCII, so none of the Unicode rules are exercised by the existing corpus.
4. **Display versus identity:** the record `name` keeps the raw string (`" x"` is displayed with its space). Identity strips it. So `"x"` and `" x"` are one identity but two displayed strings. A duplicate report must group by the stripped key, not by the displayed text.
5. **Excluded from the count:** non-string names, missing names, and whitespace-only names are not counted. Those fixtures are still measured. Whitespace-only names display as `case-NN`.

## What the guard does NOT do (the R1 bug)

- **It does not reject duplicates.** It enforces only a floor of distinct stripped names. A corpus of 16 distinct names plus 35 repeated fixtures passes, because `unique = 16 >= 16`.
- The module docstring (L13–14) and `LIMITS` (L77) say "a narrower or duplicated corpus fails before any child runs". The code enforces only the "narrower" half. The "duplicated" half is a documentation overclaim.
- **Repair (executor's job, not done here):** compute the stripped key for every counted fixture; reject when any stripped key occurs more than once, before the child loop; report offenders grouped by stripped key with their raw display forms. Keep the `< 16` floor. Keep `strip` plus exact equality, with no case or Unicode folding, so the repair does not add a second identity convention.
- **Duplicate raw JSON keys:** `json.loads` keeps the last value of a repeated `name` key. The guard therefore sees only that last value. The corpus has a case named `invalid_duplicate_raw_json_key`, but the guard does not inspect raw duplicate keys. Limitation, not fixed here.

## Implications for the shared fixture schema

- The guard sees names after the harness expands `names` into cases (clone the first passing case and replace `name`). Duplicate detection must run on the expanded names, because that is what the runner counts.
- **Invalid duplicate controls:** at least 16 distinct stripped names, including one repeated stripped key. Under the current guard they pass; under the repaired guard they must be rejected. This is the test that proves the repair.
- **Valid controls:** at least 16 names, all distinct after strip, with no surrounding whitespace, so the displayed names and the identity keys agree.
- Do not add to the schema any promise the guard does not implement: no case-insensitive equality, no NFC/NFD normalization, no whitespace trimming beyond `strip()`, no basename or prefix matching. If the schema needs to state the rule, state exactly: "names are compared after Python `str.strip()`, by exact code-point equality; case and Unicode form are significant."
- `envelope` `array` versus `object` changes only the `load_cases` branch. The guard is the same after that. An `object` envelope without a `cases` list fails in `load_cases` before the guard, which is correct.
- `expected_rejected` is a harness expectation. It is not a guard input.

## Limitations

- No execution. Python semantics are from documentation knowledge and are marked [INFERENCE] where relevant.
- The jq checks covered `ascii_downcase` and `-`→`_` only. Unicode normalization equivalence was not tested because jq has no normalize function. The corpus is ASCII-only.
- The classifier `tools/kama-ollama-evidence.py` was not read; it is out of scope for identity.
- I did not read the round-15 build or fixture directories, and I did not check whether any other caller counts names. Those remain for the executor and L1.

## Tooling

No installs or updates performed.

Report: `.ufo/waves/round-15/build/advice/CorpusIdentity.md` (this file).
