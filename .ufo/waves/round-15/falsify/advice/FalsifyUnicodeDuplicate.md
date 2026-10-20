# FalsifyUnicodeDuplicate: round-15 attack on UnicodeDuplicate.json and the final runner predicate

Scope: `tests/ollama-corpus-guard/UnicodeDuplicate.json`, `tests/ollama-corpus-guard/check.py` (matrix loader and grader), `.ufo/waves/round-14/measure.py` (runner corpus predicate). Read-only. No checks, tests, or child processes were run. No tooling was installed or updated.

## Verdict on the assigned fixture

No defect found in `UnicodeDuplicate.json` against the matrix contract. Evidence:

| Test | Entries | Distinct stripped | Duplicate present | expected_rejected | envelope |
|---|---|---|---|---|---|
| non_ascii_name_appended_array | 17 | 16 | yes (名前 ×2, non-adjacent) | true | array |
| non_ascii_name_appended_object | 17 | 16 | yes | true | object |
| non_ascii_name_adjacent_array | 17 | 16 | yes (名前 ×2, adjacent) | true | array |
| valid_unique_non_ascii_array | 16 | 16 | no | false | array |
| valid_unique_non_ascii_object | 16 | 16 | no | false | object |

- Minimum: every fixture has at least 16 distinct stripped names (check.py:192-200). Rejected fixtures are exactly 16 distinct; valid controls are exactly 16. The boundary is met with zero slack, which is correct for the >=16 rule.
- Correspondence: check.py:201-211 enforces both directions. `expected_rejected: true` requires `distinct < len`; `false` requires `distinct == len`. All five fixtures satisfy this.
- Codepoint exactness (grep, not execution): all eight 名前 lines match `^\s+"名前",?$` exactly, and no other non-ASCII byte exists in the file. Both duplicates are identical codepoint sequences, so the duplicate is real under both Python `str` equality and the matrix's `strip()`.
- Envelope: check.py:354-357 wraps `object` as `{"cases": [...]}` and emits `array` bare. measure.py:118-123 accepts both. Mapping is consistent.
- Rejected-path expectations (check.py:528-575) match the runner's corpus branch: runner returns before the `elif tool_present` block (measure.py:377-385), so no `tempfile` directory, no `subprocess.run`, and every record has `observed_exit` None (measure.py:159-176). Marker count and Popen count are structurally 0 on this path.

## Findings (bounded, none exercised by the committed fixture)

### F1 (medium): runner and matrix disagree on what counts as a name in the duplicate predicate

- Runner: measure.py:352-356 builds `declared` only from dict entries whose `name` is a `str` and whose `name.strip()` is non-empty. The duplicate test is `len(declared) != unique`, and the minimum test uses `unique`. Empty, whitespace-only, and non-string names are invisible to both checks.
- Matrix: check.py:192-193 counts every item's `strip()`ed value, including `""`, toward both `distinct` and the duplicate test. The matrix's `names` only requires `isinstance(item, str)`, so `""` and `"   "` are accepted as items.

Concrete divergence (reasoned from source, not executed):
- Input A: 15 distinct non-empty names plus `""` and `"  "`. Matrix: `distinct` 16, `len` 17, so it is a duplicate-rejected control. Runner: `declared` 15, `unique` 15, no duplicate reported, and the minimum message fires instead (`"15 unique case names; at least 16 required"`). The grader's `DUPLICATE_REASON` check (check.py:537-540) fails. This is fail-closed for the harness, but the matrix cannot express this case as a passing test.
- Input B: 16 distinct non-empty names plus `""` and `""`. Matrix: duplicate, must reject. Runner: `unique` 16, `len(declared)` 16, corpus accepted, and the two blank cases are measured under fallback names `case-NN` (measure.py:131-136). This is a runner-side false accept under the matrix's own definition of duplicate.

Not in the committed matrix, so the suite is green by absence. Either the runner should count every stripped string name (including `""`) the way the matrix does, or the matrix and runner docstring should state that blank names are exempt. The runner docstring (measure.py:13-14, LIMITS line 77) says "duplicated corpora fail before any child is spawned" without defining blank names.

### F2 (low): non-string names are silently exempt from the runner's duplicate predicate

Same mechanism as F1 for `name` values like `5`, `null`, or `[]`. The matrix cannot generate these because `load_matrix` requires strings, so this is reachable only through the runner's direct `--cases` input, not through `check.py`. Duplicate non-string names are accepted and measured under `case-NN` names. Scope-limited evidence; include in whatever fix addresses F1.

### F3 (low): constants and the reason string are duplicated across two files

`MINIMUM_UNIQUE_CASES = 16` appears in both measure.py:66 and check.py:70. `DUPLICATE_REASON = "duplicate case names"` is a literal in measure.py:359 and is matched by substring in check.py:69 and :537. A drift in either file produces a harness failure rather than a silent pass (fail-closed), but the coupling is undocumented. Maintainability only.

### F4 (coverage note, not a defect): UnicodeDuplicate.json does not exercise strip-equivalence on non-ASCII

All duplicates in this fixture are identical codepoint sequences. Nothing in this file proves that a Unicode whitespace variant (for example `"名前\u3000"`) is treated as a duplicate of `"名前"` by `str.strip()`, nor that canonically equivalent but codepoint-different forms (NFC vs NFD) are distinct under both sides. Both runner and matrix use codepoint `str` semantics, so they agree; the fixture simply does not pin that behavior. Report as a verification gap, not a bug.

## Residual risk and verification gaps

- Not verified by execution, per instruction: the template clone passing for the valid controls, actual Popen/marker counts, and runtime audit-hook behavior. Reading suggests `grade` for the rejected path is structurally satisfied, but only a run can confirm it.
- The audit prefix list (check.py:79-85) observes only runner-process `subprocess.Popen`, `os.system`, `os.posix_spawn`, `os.fork`, and `os.exec` events. That is documented in LIMITS (check.py:91-93) and is sufficient for the rejected-path "zero child" claim because the corpus branch makes no such call.
- No outside non-author admission authority was exercised.

Tooling: none installed, updated, or recorded. pacman was not invoked (operator pause in effect).
