# CorpusCounts — plain-parse census of the corpus-guard matrix JSON

Scope: independently count and characterize the committed matrix at
`tests/ollama-corpus-guard/*.json`, and derive stripped-name uniqueness from the
declared `names` arrays. Read-only; no edits outside this report; no checks,
tests, builds, or runners executed.

Method: `json.load` each sorted sibling `*.json`; every `names` entry is processed
with Python `str.strip()` and exact code-point set equality, matching the identity
key observed in `.ufo/waves/round-14/measure.py:350-364`. The harness expands each
matrix row by cloning the first passing `tests/ollama-evidence/cases.json` fixture
and replacing only `case["name"]` with each `names` entry
(`tests/ollama-corpus-guard/check.py:340-341`), so the per-row distinct stripped
count below is exactly the count `corpus_problems` would compute for that staged
corpus. No import of `check.py`/`measure.py`; parsing only.

Snapshot: worktree clean for these paths; candidate commit `70af36c`
("round-15: enforce duplicate corpus admission before replay children").
Definitions used: **negative** = `expected_rejected: true`; **positive** =
`expected_rejected: false`.

## One-line result (observed)

12 files, **50 cases = 27 negative + 23 positive**. Every negative corpus has
**>=16 distinct stripped names** and at least one duplicated stripped identity;
every positive corpus is all-distinct after strip with **>=16** entries. All 50
case identities are distinct across all files. No name is a non-string or empty
string, and none is whitespace-only after strip, so the harness/runner key sets
coincide on these fixtures.

## Per-file inventory

| Fixture | Cases | Negative | Positive | array | object | Distinct stripped range |
|---|---:|---:|---:|---:|---:|---|
| AdjacentDuplicate.json | 4 | 2 | 2 | 2 | 2 | 16 |
| AppendDuplicate.json | 4 | 2 | 2 | 2 | 2 | 16 |
| DistantDuplicate.json | 3 | 2 | 1 | 2 | 1 | 16–32 |
| MiddleDuplicate.json | 4 | 2 | 2 | 2 | 2 | 16 |
| MultipleDuplicates.json | 4 | 2 | 2 | 2 | 2 | 16 |
| ObjectEnvelope.json | 3 | 2 | 1 | 0 | 3 | 16 |
| PrependDuplicate.json | 5 | 3 | 2 | 3 | 2 | 16 |
| TabCollision.json | 2 | 1 | 1 | 2 | 0 | 16–17 |
| TriplicateName.json | 6 | 4 | 2 | 4 | 2 | 16 |
| UnicodeDuplicate.json | 5 | 3 | 2 | 3 | 2 | 16 |
| ValidBoundaries.json | 6 | 2 | 4 | 5 | 1 | 16–32 |
| WhitespaceCollision.json | 4 | 2 | 2 | 2 | 2 | 16 |
| **Total** | **50** | **27** | **23** | **29** | **21** | **16–32** |

Every case identity is prefixed by its fixture identity (`AdjacentDuplicate…`,
`AppendDuplicate…`, `DistantDuplicate…`, etc.); no mismatched prefix was found.

## Per-case identities and derived stripped-name uniqueness

`Declared` = `len(names)`; `Distinct` = `len({n.strip() for n in names})`;
duplicate column groups by stripped key and notes raw forms when the raw strings
differ from the stripped identity.

| Fixture | Case identity | Env | Expect | Declared | Distinct | Duplicate stripped identities |
|---|---|---|---|---:|---:|---|
| AdjacentDuplicate.json | `AdjacentDuplicate-array` | array | negative | 17 | 16 | `n05`×2 |
| AdjacentDuplicate.json | `AdjacentDuplicate-object` | object | negative | 17 | 16 | `n05`×2 |
| AdjacentDuplicate.json | `AdjacentDuplicate-valid-unique-array` | array | positive | 16 | 16 | — |
| AdjacentDuplicate.json | `AdjacentDuplicate-valid-unique-object` | object | positive | 16 | 16 | — |
| AppendDuplicate.json | `AppendDuplicate_first_name_appended_array_envelope` | array | negative | 17 | 16 | `n00`×2 |
| AppendDuplicate.json | `AppendDuplicate_first_name_appended_object_envelope` | object | negative | 17 | 16 | `n00`×2 |
| AppendDuplicate.json | `AppendDuplicate_valid_unique_corpus_array_envelope` | array | positive | 16 | 16 | — |
| AppendDuplicate.json | `AppendDuplicate_valid_unique_corpus_object_envelope` | object | positive | 16 | 16 | — |
| DistantDuplicate.json | `DistantDuplicate.Array32FirstRepeatedAtEnd` | array | negative | 33 | 32 | `n00`×2 |
| DistantDuplicate.json | `DistantDuplicate.Object16FirstRepeatedAtEnd` | object | negative | 17 | 16 | `m00`×2 |
| DistantDuplicate.json | `DistantDuplicate.ValidArray32Unique` | array | positive | 32 | 32 | — |
| MiddleDuplicate.json | `MiddleDuplicate-inserted-mid-array` | array | negative | 17 | 16 | `n07`×2 |
| MiddleDuplicate.json | `MiddleDuplicate-inserted-mid-object` | object | negative | 17 | 16 | `n07`×2 |
| MiddleDuplicate.json | `MiddleDuplicate-duplicate-removed-array` | array | positive | 16 | 16 | — |
| MiddleDuplicate.json | `MiddleDuplicate-duplicate-removed-object` | object | positive | 16 | 16 | — |
| MultipleDuplicates.json | `MultipleDuplicates_tail_n01_n03_n01_array` | array | negative | 19 | 16 | `n01`×3; `n03`×2 |
| MultipleDuplicates.json | `MultipleDuplicates_tail_n01_n03_n01_object` | object | negative | 19 | 16 | `n01`×3; `n03`×2 |
| MultipleDuplicates.json | `MultipleDuplicates_valid_distinct16_array` | array | positive | 16 | 16 | — |
| MultipleDuplicates.json | `MultipleDuplicates_valid_distinct16_object` | object | positive | 16 | 16 | — |
| ObjectEnvelope.json | `ObjectEnvelope_duplicate_n14_trailing` | object | negative | 17 | 16 | `n14`×2 |
| ObjectEnvelope.json | `ObjectEnvelope_duplicate_n14_adjacent` | object | negative | 17 | 16 | `n14`×2 |
| ObjectEnvelope.json | `ObjectEnvelope_valid_16_unique` | object | positive | 16 | 16 | — |
| PrependDuplicate.json | `PrependDuplicate-array` | array | negative | 17 | 16 | `n15`×2 |
| PrependDuplicate.json | `PrependDuplicate-object` | object | negative | 17 | 16 | `n15`×2 |
| PrependDuplicate.json | `PrependDuplicate-padded-strip-collision` | array | negative | 17 | 16 | `n15`×2 (strip-only raw `'  n15  '`) |
| PrependDuplicate.json | `PrependDuplicate-valid-unique-array` | array | positive | 16 | 16 | — |
| PrependDuplicate.json | `PrependDuplicate-valid-unique-object` | object | positive | 16 | 16 | — |
| TabCollision.json | `TabCollision-tab-wrapped-duplicate-array` | array | negative | 17 | 16 | `n09`×2 (strip-only raw `'\tn09\t'`) |
| TabCollision.json | `TabCollision-tab-wrapped-unique-array` | array | positive | 17 | 17 | — |
| TriplicateName.json | `TriplicateName_array_n08_triplicated_separated` | array | negative | 18 | 16 | `n08`×3 |
| TriplicateName.json | `TriplicateName_object_n08_triplicated_separated` | object | negative | 18 | 16 | `n08`×3 |
| TriplicateName.json | `TriplicateName_array_n08_triplicated_adjacent` | array | negative | 18 | 16 | `n08`×3 |
| TriplicateName.json | `TriplicateName_array_n08_triplicated_strip_equivalent` | array | negative | 18 | 16 | `n08`×3 (strip-only raw `' n08'`, `'n08 '`) |
| TriplicateName.json | `TriplicateName_array_16_distinct_no_duplicate` | array | positive | 16 | 16 | — |
| TriplicateName.json | `TriplicateName_object_16_distinct_no_duplicate` | object | positive | 16 | 16 | — |
| UnicodeDuplicate.json | `UnicodeDuplicate_non_ascii_name_appended_array_envelope` | array | negative | 17 | 16 | `名前`×2 |
| UnicodeDuplicate.json | `UnicodeDuplicate_non_ascii_name_appended_object_envelope` | object | negative | 17 | 16 | `名前`×2 |
| UnicodeDuplicate.json | `UnicodeDuplicate_non_ascii_name_adjacent_array_envelope` | array | negative | 17 | 16 | `名前`×2 |
| UnicodeDuplicate.json | `UnicodeDuplicate_valid_unique_non_ascii_array_envelope` | array | positive | 16 | 16 | — |
| UnicodeDuplicate.json | `UnicodeDuplicate_valid_unique_non_ascii_object_envelope` | object | positive | 16 | 16 | — |
| ValidBoundaries.json | `ValidBoundaries_Exactly16UniqueArrayAccepted` | array | positive | 16 | 16 | — |
| ValidBoundaries.json | `ValidBoundaries_ThirtyTwoUniqueArrayAccepted` | array | positive | 32 | 32 | — |
| ValidBoundaries.json | `ValidBoundaries_Object16UniqueAccepted` | object | positive | 16 | 16 | — |
| ValidBoundaries.json | `ValidBoundaries_16DistinctPlusCaseVariantN00Accepted` | array | positive | 17 | 17 | — |
| ValidBoundaries.json | `ValidBoundaries_16DistinctPlusExactDuplicateLastRejected` | array | negative | 17 | 16 | `vd00`×2 |
| ValidBoundaries.json | `ValidBoundaries_16DistinctPlusExactDuplicateFirstRejected` | array | negative | 17 | 16 | `ve00`×2 |
| WhitespaceCollision.json | `WhitespaceCollision-array` | array | negative | 17 | 16 | `n04`×2 (strip-only raw `' n04 '`) |
| WhitespaceCollision.json | `WhitespaceCollision-object` | object | negative | 17 | 16 | `n04`×2 (strip-only raw `' n04 '`) |
| WhitespaceCollision.json | `WhitespaceCollision-valid-array` | array | positive | 16 | 16 | — |
| WhitespaceCollision.json | `WhitespaceCollision-valid-object` | object | positive | 16 | 16 | — |

## Derived count distributions

- Negative declared sizes: 17×20, 18×4, 19×2, 33×1 (483 declared entries).
- Negative distinct sizes: 16×26, 32×1.
- Positive declared = distinct sizes: 16×19, 17×2, 32×2 (402 declared entries).
- Envelope split: negative array 16 / object 11; positive array 13 / object 10.
- Boot floor: the minimum distinct stripped count across all 50 cases is 16; no
  case falls below `MINIMUM_UNIQUE_CASES`. Consequently, for all 27 negatives the
  minimum-count clause is already satisfied (26 of them have exactly 16 distinct
  names), so the set-cardinality comparison between declared and stripped-unique
  names is the only predicate distinguishing every negative corpus from a valid
  one. This is a shape fact about the committed fixtures, not an execution result.

## Duplicate identity classes (negative corpora only)

- Raw-exact duplicate present: 22 of 27.
- Duplicate only after `strip()`: 5 of 27 —
  `PrependDuplicate-padded-strip-collision` (`n15`),
  `TabCollision-tab-wrapped-duplicate-array` (`n09`),
  `TriplicateName_array_n08_triplicated_strip_equivalent` (`n08`),
  `WhitespaceCollision-array` and `WhitespaceCollision-object` (`n04`).
- Multiplicity: 21 negatives have exactly one duplicated identity at ×2; 4 have a
  ×3 identity (`MultipleDuplicates` pair: `n01`×3 and `n03`×2; `TriplicateName`
  separated/object/adjacent/strip-equivalent: `n08`×3). Two rows carry two
  duplicated identities (the `MultipleDuplicates` pair).
- Duplicate identity spellings: `n00`, `n01`, `n03`, `n04`, `n05`, `n07`, `n08`,
  `n09`, `n14`, `n15`, `m00`, `vd00`, `ve00`, `名前`.
- Whitespace-touched raw names occur in 6 cases: negatives `'  n15  '`,
  `'\tn09\t'`, `' n04 '`×2, `' n08'`+`'n08 '`; positive
  `TabCollision-tab-wrapped-unique-array` contains `'\tn16\t'` yet is all-distinct
  after strip (17/17) — a positive control that would defeat an over-broad
  rejection of any whitespace-wrapped name.
- `名前` duplicates are exact code-point repeats in all three Unicode negative
  rows; no NFC/NFD or compatibility variant appears anywhere in the matrix.
- `ValidBoundaries_16DistinctPlusCaseVariantN00Accepted` is 17/17 distinct,
  showing a case-only variant (`N00` vs `n00`) is treated as a distinct identity.

## Cross-corpus identity facts

- Test identities: 50 rows, 50 distinct; no cross-file duplicate id.
- Declared corpus entries over all rows: 885. Union of raw names: 152 distinct;
  union after `strip()`: 146 distinct. The 6 raw forms that collapse onto an
  existing stripped identity are `' n04 '`→`n04`, `'\tn09\t'`→`n09`,
  `'  n15  '`→`n15`, `' n08'`→`n08`, `'n08 '`→`n08`, `'\tn16\t'`→`n16`.
- Adjacent, non-matrix baseline `tests/ollama-evidence/cases.json` (clone source):
  51 cases, 51 distinct stripped names, no blank/non-string names, no duplicates.

## Static concordance with the load-time predicates

Parsed row shape satisfies `check.py:161-210` exactly: non-empty string id,
non-empty string `names`, envelope in `{array, object}`, boolean
`expected_rejected`, distinct stripped names `>= 16`, negatives with a real
duplicate, positives all-distinct, and globally unique test ids. This is a
statement about fixture shape only; whether the repaired runner then rejects or
accepts these corpora, and whether it does so before any child process, was not
executed here.

## Limits and residual unknowns

- No execution: no claim about exit codes, `duplicate case names` emission,
  classifier invocations, runner process events, or pre-child ordering. Those
  require running `check.py` and are outside this lane.
- Fixtures exercise exact-codepoint identity plus `str.strip()` only. Interior
  whitespace, case folding, Unicode normalization, missing/blank/non-string
  names, and duplicate raw JSON keys are not represented in this matrix.
- Counts are a snapshot of the digests below; any later fixture edit invalidates
  them.

## Snapshot digests (sha256)

| Path | sha256 |
|---|---|
| tests/ollama-corpus-guard/AdjacentDuplicate.json | `28c5f0524a2a20f4ae8e720946aa49e9943ac44481461be3a081989298298a2b` |
| tests/ollama-corpus-guard/AppendDuplicate.json | `fb677e8c86d660b515fba489ce73a9cf20bfd81fbe81ffbf1e113e28f3353fc3` |
| tests/ollama-corpus-guard/DistantDuplicate.json | `38d396fc9d4e7ae9352aa8248b32e4567c032e56ba1ca7ae7a3c88402a36d0aa` |
| tests/ollama-corpus-guard/MiddleDuplicate.json | `fad0078436f59cb3b89a0135c3ff12743ae60ea850864ac07fb4436cadbdb8c5` |
| tests/ollama-corpus-guard/MultipleDuplicates.json | `b72ed6b8704dbd683224f9b647b1091d4316c6d863638f8f0adb37e96eee43a5` |
| tests/ollama-corpus-guard/ObjectEnvelope.json | `3d66ec5fa166bc2ba881ba252417a54d5f7bd8b91e13c6bc91b0c72a25e7f4cb` |
| tests/ollama-corpus-guard/PrependDuplicate.json | `3d15e7006e163a82b41508ba41f6e3080e79b2c0f6f6ebb21d2a9d2b527cf866` |
| tests/ollama-corpus-guard/TabCollision.json | `94a261c444d8bdbb109576d8e347d88d67bca713387fa0cc9443b1843118b734` |
| tests/ollama-corpus-guard/TriplicateName.json | `23d33f00ff9ec76d8ce92db37c1e492e994cc3df04e815fb46c5df40f5ee4da0` |
| tests/ollama-corpus-guard/UnicodeDuplicate.json | `1f72b7b4bdef6cb0ef8a8ed39dd205aeb02afc695eefd368267145b0dedab5f2` |
| tests/ollama-corpus-guard/ValidBoundaries.json | `d96d721473ab67c01ab336f908c5727985d57b344019a2c64b5c518482b911b9` |
| tests/ollama-corpus-guard/WhitespaceCollision.json | `fd3836b8daf6b85dde59d24ff586b4ae5c08944f7a410cd4f05f9ef4a41735f6` |
| tests/ollama-evidence/cases.json (baseline, not matrix) | `4a4de0b85009c42804e43c8ae8833bd6f0673edc71ae5ec8baa1e3201e158ae4` |
| tests/ollama-corpus-guard/check.py (harness, read for key semantics) | `914923166517ca162364e8b2ec2e7cb3cf9e295b89962392999267d55f5ca4c8` |
| .ufo/waves/round-14/measure.py (runner, read for guard predicate) | `46c5866d73a4f875353ff59c6929615149a1f4f4acf69b0b07deeb99d5445257` |

## Tooling

No installs or updates were performed.

Report: `.ufo/waves/round-15/falsify/advice/CorpusCounts.md`
