# WhitespaceCollision — scoped findings (round-15)

## Files changed
- `tests/ollama-corpus-guard/WhitespaceCollision.json` — new literal shared-schema fixture matrix (this report covers only this file).

## Behavior exercised
Bug under test: `.ufo/waves/round-14/measure.py` `corpus_problems` strips each `case.name` and counts only `len(set(declared))`, then rejects solely when `unique < 16`. It never compares `len(declared)` against `unique`, so a corpus of 17 entries whose stripped names collapse to exactly 16 passes the old guard while being a genuine duplicate corpus.

Fixture entries (all `name` ids prefixed `WhitespaceCollision`, all literal arrays, no generator/execution):

| name | names | envelope | expected_rejected |
|---|---|---|---|
| WhitespaceCollision-array | `n01`–`n16` + `" n04 "` (17 entries) | array | true |
| WhitespaceCollision-object | same 17 names | object | true |
| WhitespaceCollision-valid-array | `n01`–`n16` (16 entries, all distinct) | array | false |
| WhitespaceCollision-valid-object | same 16 distinct names | object | false |

- Invalid rows: 17 entries → 16 distinct stripped names → `>=16` distinct, so the pre-repair minimum-unique check cannot reject them; only a repaired guard that rejects any post-strip duplicate fails them before any child process.
- Valid counterparts: the duplicate removed; strip changes nothing (names already canonical), so measurement must proceed unchanged.
- Leading-and-trailing padded `" n04 "` exercises `str.strip()` canonicalization on both edges; padded-vs-unpadded is a policy-equal duplicate, not a malformed-schema input — every name remains a non-empty string.

## Constraints honored
- No execution, verification commands, generator, or edits to sibling fixtures/receipts; `tests/ollama-corpus-guard/` directory created implicitly by the write.
- No tool installs; none needed.

## Limitations
- Static declarations only; verdict correctness depends on the repaired guard + harness semantics and is asserted solely via `expected_rejected`, never verified here.
- Padded name is pinned exactly `" n04 "` per assignment (single canonicalization variant); other whitespace forms (tabs, internal padding) are covered by siblings (`TabCollision`, etc.), not this file.

Report: .ufo/waves/round-15/build/advice/WhitespaceCollision.md
