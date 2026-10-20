# ValidBoundaries — round-15 advice

## Files changed
- `tests/ollama-corpus-guard/ValidBoundaries.json` (new, 6 entries, literal shared-schema matrix)

## Matrix authored
| name | names | envelope | expected_rejected |
|---|---|---|---|
| ValidBoundaries_Exactly16UniqueArrayAccepted | 16 unique (`vb00`–`vb15`) | array | false |
| ValidBoundaries_ThirtyTwoUniqueArrayAccepted | 32 unique (`vw00`–`vw31`) | array | false |
| ValidBoundaries_Object16UniqueAccepted | 16 unique (`vo00`–`vo15`) | object (`{"cases": [...]}`) | false |
| ValidBoundaries_16DistinctPlusCaseVariantN00Accepted | 17 names, 17 distinct stripped (`n00`–`n15` + `N00`) | array | false |
| ValidBoundaries_16DistinctPlusExactDuplicateLastRejected | 17 names, 16 distinct (`vd00` repeated last) | array | true |
| ValidBoundaries_16DistinctPlusExactDuplicateFirstRejected | 17 names, 16 distinct (`ve00` repeated first) | array | true |

## Coverage rationale
- Valid controls cover the minimum boundary (exactly 16 unique), a supersized corpus (32 unique), the `{"cases": [...]}` object envelope at the boundary, and case-sensitivity (`n00` vs `N00` must stay distinct — the guard strips but does not case-fold).
- Invalid entries are the R1 bug targets: 16 distinct stripped names with one exact duplicate appended (last) and prepended (first). `unique == 16` passes the buggy `unique < MINIMUM_UNIQUE_CASES` check, so only a repaired duplicate guard rejects them before any child process. The 16-unique accepted fixtures serve as the duplicate-removed counterparts.
- No whitespace/tab collisions, unicode, adjacency variants, or malformed-schema cases — owned by sibling files.

## Evidence retained
- Guard canonicalization observed in `.ufo/waves/round-15/frozen/measure-before.py:350-362` (`name.strip()`, case-sensitive `set`, `MINIMUM_UNIQUE_CASES = 16`); envelope handling at lines 120-127; docstring promise "narrower or duplicated corpora fail before any child is spawned" at lines 13-14 and 77.

## Limitations / risks
- Fixture authored statically; no execution or generator used (per assignment; L1 harness runs it).
- Case-variant fixture assumes case-sensitive comparison — correct for `str.strip()` + `set()`; would flag a (wrong) case-insensitive repair.

Report: .ufo/waves/round-15/build/advice/ValidBoundaries.md
