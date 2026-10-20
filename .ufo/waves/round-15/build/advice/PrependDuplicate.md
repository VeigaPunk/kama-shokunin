# PrependDuplicate — round-15 corpus-guard fixture

## Files changed
- `tests/ollama-corpus-guard/PrependDuplicate.json` — new; literal shared-schema
  matrix (directory `tests/ollama-corpus-guard/` did not previously exist).

## Matrix
| test id | envelope | names | distinct (stripped) | expected_rejected |
|---|---|---|---|---|
| PrependDuplicate-array | array | `"n15"` prepended to n00–n15 | 16 | true |
| PrependDuplicate-object | object | same 17 names | 16 | true |
| PrependDuplicate-padded-strip-collision | array | `"  n15  "` prepended to n00–n15 | 16 | true |
| PrependDuplicate-valid-unique-array | array | n00–n15 | 16 | false |
| PrependDuplicate-valid-unique-object | object | n00–n15 | 16 | false |

## Rationale
- `corpus_problems` in `.ufo/waves/round-14/measure.py` canonicalizes with
  `str.strip()` and only enforces `unique < 16`; the prepend scenarios each
  carry exactly 16 distinct stripped names, so the count-only guard cannot
  catch them — they exercise the real duplicate policy.
- `padded-strip-collision` exercises canonicalization: the padded literal
  collides with trailing `n15` only after strip. Still a duplicate policy
  scenario, not malformed-schema scope.
- Valid counterparts (duplicate removed) retain the unique-corpus measurement
  path for both envelopes.

## Limitations
- Static fixture only; no generator, no execution, no verification run per
  lane bounds.
- Name style `n00`–`n15` chosen to match sibling-seat convention in the
  dispatch text.
- No tools installed; none needed.
