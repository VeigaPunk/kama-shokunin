# Round-15 FixtureReview (read-only)

Scope: review of the duplicate-corpus guard fixture contract under
`/home/vgpnk/Projects/shokunin/kama-shokunin`. No tests, builds, linters, or runner invocations were executed. Facts below come from reading the spec, the frozen runner, `tests/ollama-evidence/cases.json`, and JSON field queries against that file.

No tool installs or updates were made.

## Pending (not failures)

These were absent or unmodified at review time. They are reported separately and were not treated as final failures.

- `tests/ollama-corpus-guard/` does not exist yet. No `*.json` fixtures and no `check.py` were found.
- Fixtures still pending from the spec (12): AppendDuplicate, PrependDuplicate, MiddleDuplicate, DistantDuplicate, AdjacentDuplicate, MultipleDuplicates, TriplicateName, WhitespaceCollision, TabCollision, ObjectEnvelope, UnicodeDuplicate, ValidBoundaries.
- `.ufo/waves/round-14/measure.py` `corpus_problems` (lines 350-362) still has only the minimum-cardinality check. The duplicate guard (GuardRepair) is not yet applied.

## Verified facts

- `tests/ollama-evidence/cases.json` is a top-level JSON array of 51 fixtures. All 51 `name` values are distinct, and none has leading or trailing whitespace. Historical 51/51 therefore passes both the minimum check and any new duplicate check.
- First fixture is `loaded_same_digest`: `expect` `llama3:8b`, `expected_exit` 0, `expected_finding` `loaded_same_digest`. This is the clone source named in the spec, and it is a passing case.
- `tools/kama-ollama-evidence.py` is present.
- Frozen `round-15/frozen/measure-before.py` `run()` (lines 365-383): `load_cases` → `corpus_problems` → if problems, emit `unmeasured_record` for every case and skip the tempdir and `measure_case` loop. Child processes are spawned only at `measure_case` (line 383). A duplicate guard placed in `corpus_problems` therefore rejects before any child, as the spec requires. The repair must keep this ordering.
- `unmeasured_record` sets `passed: False`, `observed_finding: None`, and `reasons: [detail]`. `run()` sets `result["error"] = "corpus: " + "; ".join(...)`. The check predicate `error includes "duplicate case names"` is satisfied only if the guard message contains that exact phrase.
- `load_cases` accepts an object envelope only when it has a `cases` key holding a list (line 122). Any other object shape is rejected.
- `corpus_problems` excludes non-dict cases, non-string names, and names that are empty after strip from `declared` (lines 352-355).

## Per-fixture cardinality, from spec text

Entry counts and distinct stripped counts are derived from the spec wording. Fixture files are not yet present to confirm them.

| Fixture | Invalid (expected_rejected true) | Entries / distinct stripped | Valid counterpart |
|---|---|---|---|
| AppendDuplicate | n00..n15 + n00 | 17 / 16 | n00..n15 (16 / 16) |
| PrependDuplicate | n15 + n00..n15 | 17 / 16 | n00..n15 (16 / 16) |
| MiddleDuplicate | 16 distinct with n07 inserted mid-list | 17 / 16 | 16 / 16 |
| DistantDuplicate | n00..n31 + n00 at end | 33 / 32 | 32 / 32 |
| AdjacentDuplicate | 16 distinct with n05 copied adjacently | 17 / 16 | 16 / 16 |
| MultipleDuplicates | 16 distinct + n01, n03, n01 | 19 / 16 | 16 / 16 |
| TriplicateName | 16 distinct + n08 twice | 18 / 16 (or 3 occurrences of n08 in total; see F6) | 16 / 16 |
| WhitespaceCollision | 16 distinct + " n04 " | 17 / 16 | 16 / 16 |
| TabCollision | 16 distinct + "\tn09\t" | 17 / 16 | 16 / 16 |
| ObjectEnvelope | 16 distinct + n14, object envelope | 17 / 16 | 16 / 16, object envelope |
| UnicodeDuplicate | 16 distinct incl. non-ASCII + identical copy | 17 / 16 | 16 / 16 |
| ValidBoundaries | none invalid (boilerplate line; see F7) | 16 / 16 array; 32 / 32 array; 16 / 16 object; 16 + "N00" = 17 / 17 | all accepted |

Every invalid control has at least 16 distinct stripped names, so the old minimum guard passes and only the duplicate guard can reject it. This satisfies the spec requirement.

## Findings

Ordered by severity.

**F1 (medium). Fixture cardinality is not enforced, so a control can pass for the wrong reason.** Nothing in the spec requires `check.py` to validate that an invalid control has at least 16 distinct stripped names and at least one real duplicate, or that a valid control has at least 16 distinct stripped names with no duplicate. A weak fixture with fewer than 16 distinct names would still be rejected, but by the minimum guard, and the `duplicate case names` substring would still match, so the test would not isolate the new guard. Recommend `check.py` assert the cardinality invariant per fixture before running the runner. Fail the fixture if it is violated.

**F2 (medium). Blank and non-string names fall outside the duplicate count.** `corpus_problems` drops names that are empty after strip (line 354). Two blank names therefore never count as duplicates, and they also do not count toward the minimum. No pending fixture uses blank names. This is a residual gap in the guard policy, not a fixture defect. The repair's stable reason should cover it, or the limitation should be recorded.

**F3 (medium). Unicode duplicates are codepoint-exact, not canonical.** The guard compares Python `str` values after `strip()`. It does not apply NFC or NFD normalization. `UnicodeDuplicate` must use identical code points in both occurrences. A composed/decomposed pair would be accepted by the guard and must not be labeled as an invalid control. Optionally add a valid counterpart documenting that NFC and NFD are distinct under this policy.

**F4 (low). `strip()` uses Python Unicode whitespace.** `str.strip()` also removes U+00A0, U+3000, and similar characters. `WhitespaceCollision` and `TabCollision` use ASCII whitespace, which is fine. `check.py` must compute its expected distinct counts with the same Python `strip()` and must not use a JSON-level or regex trim.

**F5 (low). Case-variant names are distinct.** The guard is case-sensitive. `N00` and `n00` count as two names. `ValidBoundaries` correctly expects acceptance for this. No invalid control should use a case variant expecting rejection.

**F6 (low). TriplicateName is ambiguous about total occurrences.** "16 distinct plus n08 twice" can mean two appended copies (3 occurrences) or two total copies (2 occurrences). Both give 16 distinct names and both are rejected, so the verdict is unaffected. The fixture should state the exact literal list so the test is unambiguous.

**F7 (low). ValidBoundaries carries the invalid boilerplate.** The spec's Target line for ValidBoundaries includes "Invalid scenarios expected_rejected true". This conflicts with a fixture whose purpose is accepted controls. Its entries should all be `expected_rejected: false` unless a deliberate invalid entry is added on purpose. Check this when the file lands.

**F8 (low). Object envelope must use the exact key.** `load_cases` only accepts `{"cases": [...]}` (line 122). `check.py` must write exactly that key for `envelope: "object"`. Any other key fails with a schema error, and the valid-object control would be misreported.

**F9 (info). Red-before behaviour is expected.** Against the frozen `measure-before.py`, every invalid control is a clone of a passing case. Each child passes, so the runner exits 0 and marker count equals total. Those controls then mismatch `expected_rejected: true`, which is the intended red-before result. This confirms the controls discriminate.

**F10 (info). Ambiguous wording in the GuardHarness spec.** "Read sorted sibling *.json arrays (exclude no files needed)" is unclear. `check.py` should read every `*.json` in `tests/ollama-corpus-guard/` in sorted order. It should not silently skip files, and it should reject a non-array top level.

**F11 (info). Clone source is read at runtime.** `check.py` clones the first fixture of `tests/ollama-evidence/cases.json`. If that file changes, the clone base changes too. `check.py` should assert that the clone base has `expected_exit` 0 before cloning, or record the clone source hash in its output.

## Residual risk and verification gaps

- Fixture files and `check.py` were not present, so per-fixture names, envelopes, and exact entries are inferred from spec text and not confirmed against bytes.
- The round-14 duplicate guard had not been applied, so the rejection path was reviewed against the frozen runner and the spec contract only.
- No child process was run. The claim that the guard rejects before any child is based on code reading of the frozen runner.

## Checks for the main agent after edits land

- Confirm each of the 12 fixture files has the exact object schema: `name`, `names`, `envelope`, `expected_rejected`.
- Confirm test ids are distinct across all files (`check.py` enforces this).
- Confirm every invalid control has at least 16 distinct stripped names, and that the valid counterpart removes only the duplicate.
- Confirm `ValidBoundaries` has no invalid entries (F7).
- Confirm `UnicodeDuplicate` uses byte-identical code points (F3).

Report: `.ufo/waves/round-15/build/advice/FixtureReview.md`
