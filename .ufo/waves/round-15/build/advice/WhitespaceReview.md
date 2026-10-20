# WhitespaceReview: strip and identity semantics (round 15, read-only)

Scope: whether strip/whitespace canonicalization is confined to the corpus duplicate guard and leaves classifier identity semantics exact. Read-only. No tests, builds, linters, or smoke runs executed. Read tools only (`read`, `grep`, `jq` fact extraction). No installs; no tool installed or upgraded.

Snapshot state observed:
- `.ufo/waves/round-15/frozen/measure-before.py` (sha256 prefix fda61e001ca8c253): pre-repair. `corpus_problems` (lines 350-362) checks only `unique >= 16`. No duplicate check. This confirms the R1 bug: a corpus with >=16 distinct stripped names plus duplicates passes and children spawn.
- `.ufo/waves/round-14/measure.py` (live, read at tag 6643, sha prefix 46c5866d73a4f875 at first hash): in-flight repair. Lines 356-359 add `if len(declared) != unique: problems.append("duplicate case names")`. The guard runs in `run()` before the `measure_case` loop, so no child is spawned on a corpus failure. The repair is still in flight and may change again.
- `tests/ollama-corpus-guard/*.json`: 12 in-flight fixture files, 50 cases. Pending; not final.

## Findings

### F1 (MEDIUM) Blank and non-string names are fail-open in the repaired guard
- Where: `measure.py` 350-364 (live). `declared` only collects `isinstance(name, str) and name.strip()`. Blank, whitespace-only, missing, and non-string names are dropped from both the duplicate count and the minimum count.
- Effect: a corpus with 16 distinct non-blank names plus any number of blank-named fixtures passes the guard. Blank-named fixtures are then executed under the fallback label `case-NN` (`case_name`, line 131-136). Multiple blank fixtures are never flagged as duplicates.
- Inconsistency: the classifier's selftest treats a blank name as `case_invalid` (`tools/kama-ollama-evidence.py:329-343`, `_valid_case` requires `name != ''`). The measure runner accepts the same fixture.
- Recommendation: in the guard, any case whose name is not a nonblank string is a corpus problem (rejected before any child). This is fail-closed and matches the selftest. No new fixture is required, but a control row is recommended in the in-flight harness (see F6).

### F2 (LOW) Duplicate JSON keys in fixtures are silently last-wins in the runner
- Where: `measure.py` `load_cases` (lines 109-128) uses plain `json.loads`. The classifier's `_pairs` hook rejects duplicate keys (`kama-ollama-evidence.py:124-130`). The runner also does not set `parse_constant`, so NaN and Infinity are accepted in fixtures (the classifier rejects non-finite values).
- Effect: `{"name":"a","name":"b",...}` is guarded and executed as `name="b"`. The `"a"` is invisible. This is not a bypass of duplicate detection, since the guard and the executed case use the same last value, but it is identity ambiguity.
- Recommendation: `object_pairs_hook` rejecting duplicate keys and `parse_constant` rejecting non-finite numbers, as the classifier does. Optional for this round; flag if the guard is claimed to be identity-exact.

### F3 (LOW) Two duplicate semantics in one lane
- The classifier selftest duplicate check (`kama-ollama-evidence.py:359-365`) is exact-string: `len(names) != len(set(names))` over `name != ''` values. The measure guard canonicalizes with strip. Effect: `"x"` and `" x"` pass the classifier selftest and are rejected by the measure guard. Neither is wrong by its own docs, but the lane has two duplicate definitions.
- Recommendation: document the divergence in the round-15 record or align the selftest. Do not change the classifier in this round (out of assignment scope).

### F4 (INFO, verified correct) Classifier identity is exact; strip is confined to the guard
Read at `tools/kama-ollama-evidence.py`:
- `_matching` (190-192): exact `==` on name or model against `--expect`. No strip, no case fold, no `:latest`, no GGUF normalization.
- `_identity_conflict` (195-202): nonempty exact `!=`. Whitespace-only counts as nonempty.
- `_remote_marker` (205-210): `value != ''`. Whitespace-only is a marker (`remote_inventory`), not absent. Matches ReviewDigest F7 and ReviewSchema M3/M4.
- `_digest_present` (213-215): `value != ''`. Whitespace-only is present. Digest equality (line 259) is exact string `!=`.
- `validate_capture` (172-187): non-string name/model/digest/marker (including null) is `invalid_input`. Matches ruling.
- `measure.py` never uses strip for classification. It uses strip only in `case_name` truthiness (returns the raw name for records) and in the guard. Records keep the raw name. Confirmed.

### F5 (LOW) Whitespace identity is under-covered in committed fixtures
- `tests/ollama-evidence/cases.json` (51 cases, unique after strip, verified by jq): the only whitespace-bearing string values in the whole file are `" sha256:111..."` (`identity_conflict_digest_whitespace_not_stripped`), `""` (`loaded_empty_string_remote_markers_are_absent`), and `""` (`unknown_tags_empty_digest`).
- Not locked by any committed case: whitespace-only digest (should be present, not unknown); whitespace-only remote marker (should be `remote_inventory`, per F7); whitespace-only or padded name/model (should be identity conflict or non-match); whitespace-padded `--expect` (must not match).
- Advisory only. Adding cases changes the numeric 7 surface. Do not add in this round without approval; record as a gap for the fixtures owner.

### F6 (INFO, pending) In-flight guard fixtures match the contract on uniqueness
Read-only jq over `tests/ollama-corpus-guard/*.json` (12 files, 50 cases):
- Every `expected_rejected: true` case has `unique(strip) = 16` or more, with at least one duplicate after strip (`TabCollision`, `WhitespaceCollision`, `PrependDuplicate` rows are strip-only duplicates). The old minimum-only guard would pass all of them, so they are valid controls for the new guard.
- Every `expected_rejected: false` case has `unique(strip) == n >= 16`.
- Uncovered, pending or advisory: no blank or whitespace-only name control (F1); no duplicate-JSON-key control (F2); `UnicodeDuplicate` uses byte-identical duplicates only, with no NFC/NFD pair. Python `str.strip()` does not normalize, so a composed/decomposed pair would be distinct; U+200B is not stripped (not `isspace`). These are residual by contract (strip only) and should be an explicit decision in the receipt.
- Harness clone property (each fixture identical except names/envelope) is not verifiable until the harness lands. Pending, not a failure.

## Residual risk
- Blank-name fail-open (F1) is the only finding that could let a non-duplicate corpus shape pass the repaired guard. Treat as blocking for the repair claim if the guard is described as "all names unique".
- Unicode normalization and zero-width characters are residual by contract (strip-only). Record as accepted residual, not as proof.
- The live `measure.py` changed during this review (tag B6F1 to 6643). Final review should re-hash against the final source.

## Verification gaps
- No test or runner executed (per assignment). The contract claims (rejection before any child; valid corpus retained) are not verified here.
- Harness file(s) not yet present in final form; fixture clone-equality unverified.
- Classifier behavior described from source reading, not execution.

## Installs and updates
None. No tool installed or upgraded. `jq` (existing) used read-only.
