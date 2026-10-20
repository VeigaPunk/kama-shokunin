# MiddleDuplicate — scoped findings

## Files changed
- `tests/ollama-corpus-guard/MiddleDuplicate.json` (new) — shared-schema literal matrix, 4 cases, ids prefixed `MiddleDuplicate`.

## Matrix contents
| id | names | envelope | expected_rejected |
|---|---|---|---|
| MiddleDuplicate-inserted-mid-array | n00..n11, **n07** (2nd copy at index 12), n12..n15 — 17 entries, 16 distinct stripped | array | true |
| MiddleDuplicate-inserted-mid-object | same 17-entry list | object | true |
| MiddleDuplicate-duplicate-removed-array | n00..n15 — 16 entries, all distinct | array | false |
| MiddleDuplicate-duplicate-removed-object | same 16-entry list | object | false |

## Behavior covered
- Invalid scenarios carry exactly 16 distinct stripped names across 17 corpus entries, so the pre-repair minimum-unique-count-only guard (`unique >= 16`) in `.ufo/waves/round-14/measure.py::corpus_problems` cannot reject them; only a real duplicate check catches the reinserted `n07`.
- Duplicate position is mid-corpus (index 12) and non-adjacent to the original `n07` at index 7, exercising positional (not just adjacent) duplicate detection.
- Both `array` and `object` envelopes are exercised for the rejected scenario and for the valid counterpart (duplicate removed).
- Values are literal JSON string arrays; no generator, no execution. All cases exercise duplicate policy — none are malformed-schema.

## Retained evidence
- Guard under test: `kama-shokunin/.ufo/waves/round-14/measure.py:350-362` (`corpus_problems`, `MINIMUM_UNIQUE_CASES = 16`, strip canonicalization at line 354).
- Fixture schema source: shared contract in round-15 spec (`envelope: 'array' | 'object'`, `expected_rejected`, harness clones first known passing case from `tests/ollama-evidence/cases.json`).

## Tooling installs
- None; no installs needed or performed.

## Risks / limitations
- No verification commands run per assignment (no JSON lint, no harness execution); L1 owns post-integration checks.
- Expected behavior depends on sibling `check.py` harness implementing the shared schema exactly (`envelope` wraps names under a `cases` key for `object`).
- `MiddleDuplicate.json` targets the `n07`-in-middle scenario only; adjacent-copy coverage is owned by `AdjacentDuplicate`, whitespace/tab collision variants by their own seats.
