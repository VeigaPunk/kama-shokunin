# ObjectEnvelope — round-15 advice

## Scope
Owned file: `/home/vgpnk/Projects/shokunin/kama-shokunin/tests/ollama-corpus-guard/ObjectEnvelope.json` (created this wave; directory did not exist).

## Files changed
- `tests/ollama-corpus-guard/ObjectEnvelope.json` — literal shared-schema matrix, 3 fixtures, no generator, no execution.

## Contents
All entries use `envelope: "object"`, exercising the object-with-`cases`-array form accepted by `load_cases` (`measure.py:120-123`), so the duplicate guard cannot pass the corpus while missing the second entry under a dict envelope.

| name | names | expected_rejected |
|---|---|---|
| `ObjectEnvelope_duplicate_n14_trailing` | n00..n15 plus trailing `n14` (17 entries, 16 distinct stripped) | true |
| `ObjectEnvelope_duplicate_n14_adjacent` | n00..n15 with `n14` duplicated adjacent (17 entries, 16 distinct stripped) | true |
| `ObjectEnvelope_valid_16_unique` | n00..n15 (16 entries, all distinct) | false |

- Both invalid controls carry ≥16 distinct stripped names, so the legacy `MINIMUM_UNIQUE_CASES = 16` unique-count guard in `corpus_problems` (`measure.py:350-362`) cannot reject them; only a real duplicate check fails them.
- The valid counterpart is the duplicate-removed form of the invalid matrices; it must pass the corpus guard and proceed to measurement.
- Names are literal JSON string arrays; ids are prefixed `ObjectEnvelope`; all configs exercise duplicate policy only (no malformed-schema scope).

## Evidence retained
- `measure.py:120-127` — object envelope (`{"cases": [...]}`) is a first-class input form.
- `measure.py:350-362` — current guard counts unique stripped names only; duplicates with ≥16 unique names evade it (the R1 bug under repair).

## Limitations / risks
- No verification run performed (per assignment: no tests/builds/linters; L1 verifies post-integration).
- Coverage is name-duplication only under the object envelope; whitespace/tab/case-folding collisions are owned by sibling fixtures (WhitespaceCollision, TabCollision, ValidBoundaries).
- Interpreted "16 distinct plus n14" as n00..n15 with `n14` repeated; both trailing and adjacent placements are provided.

## Tooling
No installs or upgrades performed.
