# UnicodeDuplicate — advice

## Files written
- `tests/ollama-corpus-guard/UnicodeDuplicate.json` (new; sole owned file)

## Matrix contents (5 literal scenarios, ids prefixed `UnicodeDuplicate_`)
Base corpus: 16 distinct stripped names — `n00`..`n14` plus non-ASCII `名前` (three kanji code points; distinct from every ASCII name under the runner's `str.strip()` canonicalization).

| id | entries | unique stripped | envelope | expected_rejected |
|---|---|---|---|---|
| `UnicodeDuplicate_non_ascii_name_appended_array_envelope` | 17 | 16 | array | true |
| `UnicodeDuplicate_non_ascii_name_appended_object_envelope` | 17 | 16 | object | true |
| `UnicodeDuplicate_non_ascii_name_adjacent_array_envelope` | 17 | 16 | array | true |
| `UnicodeDuplicate_valid_unique_non_ascii_array_envelope` | 16 | 16 | array | false |
| `UnicodeDuplicate_valid_unique_non_ascii_object_envelope` | 16 | 16 | object | false |

Every invalid scenario has exactly 16 distinct stripped names, so the old minimum-only guard (`unique < 16`, measure.py:356-361) cannot catch them — they exercise the actual duplicate-name policy, not malformed-schema or under-count scope. Valid counterparts are the same corpus with the duplicate entry removed.

## Rationale
- `名前` duplicated both appended (position displacement: last entry collides with mid-corpus entry) and adjacent (consecutive copy), covering duplicate detection independent of position.
- Follows the sibling convention observed in `AppendDuplicate.json` / `WhitespaceCollision.json`: array+object envelopes for the primary rejection, valid controls for both envelopes.

## Deliberately not covered (boundary notes for planners)
- Unicode normalization collisions (NFC `café` vs NFD `café`): the guard canonicalizes by `strip()` only; if a repaired guard adds `unicodedata` normalization this becomes a separate decision. No fixture asserts either outcome.
- Unicode whitespace collisions (e.g. `名前` / NBSP): `str.strip()` removes U+3000 and U+00A0 is NOT stripped by Python's `strip()` (only Unicode-whitespace category members are; U+00A0 is not stripped). Other lanes own whitespace-collision scope; left out to avoid overlap with WhitespaceCollision/TabCollision.
- Empty/whitespace-only names: `corpus_problems` ignores non-string or whitespace-empty names rather than counting them; that is a separate guard weakness outside this file's duplicate-policy scope.

## Limitations
- Static fixture only; not executed. Harness (`check.py`, owned by GuardRepair lane) clones the first passing case of `tests/ollama-evidence/cases.json` per name — assumed available at runtime.
- Whether `expected_rejected:true` currently fails against the buggy guard is the wave's known R1 defect; these fixtures prove the fix.

## Installs
None.
