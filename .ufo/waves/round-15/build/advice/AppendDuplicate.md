# AppendDuplicate — scoped findings

## Files changed
- `tests/ollama-corpus-guard/AppendDuplicate.json` (new; parent directory did not exist before this edit — created as part of the write).

## Matrix contents (shared schema: {name, names, envelope, expected_rejected})
Four literal fixtures, all ids prefixed `AppendDuplicate`, all `names` literal JSON arrays:

1. `AppendDuplicate_first_name_appended_array_envelope` — 17 names: `n00`..`n15` then appended `n00` at tail; envelope `array`; `expected_rejected: true`. 16 distinct stripped names.
2. `AppendDuplicate_first_name_appended_object_envelope` — same 17-name list; envelope `object`; `expected_rejected: true`. 16 distinct stripped names.
3. `AppendDuplicate_valid_unique_corpus_array_envelope` — `n00`..`n15` (16 names, all distinct); envelope `array`; `expected_rejected: false`.
4. `AppendDuplicate_valid_unique_corpus_object_envelope` — same 16 distinct names; envelope `object`; `expected_rejected: false`.

## Why this exercises the real bug
- Round-14 `measure.py` `corpus_problems` only rejects when `unique < MINIMUM_UNIQUE_CASES` (16). A corpus of 17 cases whose stripped names have exactly 16 distinct values passes the old guard even though a case name is duplicated — the append-tail duplicate is the canonical instance (R1).
- Both invalid fixtures here carry exactly 16 distinct stripped names, so the legacy minimum-unique check cannot catch them; only a true duplicate-name corpus guard (rejected before any child process spawn) can produce `expected_rejected: true`.
- No whitespace/unicode/schema-malformed tricks: every name is a clean literal `nXX` token, so the fixture isolates pure duplicate policy, not canonicalization edge cases or malformed-schema rejection. Whitespace/tab/unicode collisions are owned by sibling seats (WhitespaceCollision, TabCollision, UnicodeDuplicate).
- Valid counterparts (duplicate removed) confirm the repaired guard still admits a compliant 16-unique corpus to measurement rather than fail-closing everything.

## Evidence retained
- Guard source reviewed read-only: `.ufo/waves/round-14/measure.py` `corpus_problems` (lines 350-362) and `run` corpus gate (lines 372-378, 419-420); `MINIMUM_UNIQUE_CASES = 16` at line 66; strip canonicalization at line 354.
- Harness contract per spec: clones first known passing case of `tests/ollama-evidence/cases.json` (`loaded_same_digest`), replaces `name` per `names` entry; `envelope` selects top-level array vs `{"cases": [...]}` document.

## Limitations / risks
- No execution, generation, or verification performed per wave rules; JSON was not parse-validated by running it. Structure is literal and hand-checked.
- Fixture assumes harness maps `envelope: "object"` to `{"cases": [...]}` per the frozen loader's accepted forms (measure.py lines 120-127).
- Whether a repaired guard reports the duplicate per-record or as a single corpus `error` is GuardRepair's decision; these fixtures only require rejection before any child process.

Report: .ufo/waves/round-15/build/advice/AppendDuplicate.md
