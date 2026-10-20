# GuardReview (KamaR15.GuardReview-3): duplicate detection and minimum order

Scope: read-only review of `corpus_problems()` and `run()` in the round-14 measure harness, plus the in-flight fixtures under `tests/ollama-corpus-guard/`. No tests, builds, linters, or harness runs were executed. Checks used: sha256 and `diff` of the committed blob against the working file and the frozen snapshot, `python3` JSON parsing of fixtures for counts, and file reads. Every claim below is from those reads.

## Evidence base

- Committed source: `git show 6e348e2:.ufo/waves/round-14/measure.py`, sha256 `fda61e001ca8c2533c99a1759bb4b82f3260a72fafccf72f863f3f4e3684b60d`.
- Frozen snapshot: `.ufo/waves/round-15/frozen/measure-before.py`. Identical to the committed blob (cmp and diff both clean). Manifest sha matches.
- Working file: `.ufo/waves/round-14/measure.py`, sha256 `46c5866d73a4f875353ff59c6929615149a1f4f4acf69b0b07deeb99d5445257`. It differs from the committed blob by exactly two inserted lines at 358-359 (`if len(declared) != unique: problems.append("duplicate case names")`). The edit is in flight, so its origin was not verified. Nothing else in the file changed, including `run()`, `measure_case()`, `child_environment()`, LIMITS, and constants.

## Findings (by severity)

### F1. HIGH, fixed in the working file, confirmed in the frozen snapshot: duplicate corpora passed the guard

Frozen `corpus_problems()` (lines 350-362) builds `declared` from `name.strip()` for dict cases with non-empty string names, then emits a problem only when `unique < 16`. A duplicate is never compared against the count. Any corpus with at least 16 distinct stripped names plus duplicates passes, and `run()` (lines 379-383) then spawns one child per case, including the duplicates. That matches the R1 gap.

The working file adds `len(declared) != unique`, which closes this for every case that has a usable name. Repair verified only by reading the diff. It has not been executed, which is correct for this lane.

### F2. MEDIUM, open in the working file: nameless fixtures still bypass the guard

`declared` only receives cases whose `name` is a non-empty string after strip. Cases with a missing key, a non-string name, `""`, or whitespace-only names are dropped silently. `len(declared) != unique` cannot see them, because both sides exclude them. Example: 16 distinct valid names plus any number of fixtures with no name passes `corpus_problems()` and runs. Those fixtures are measured under the fallback `case-NN` label, which is the duplicate-identity hole the guard exists to close.

The planning note `.ufo/waves/round-15/build/advice/MeasurementPlan.md` (step 1) asks for exactly this check. The working file does not implement it.

Suggested shape for the executor (advice only, not applied):

```python
def corpus_problems(cases):
    declared = []
    problems = []
    for index, case in enumerate(cases):
        name = case.get("name") if isinstance(case, dict) else None
        if isinstance(name, str) and name.strip():
            declared.append(name.strip())
        else:
            problems.append(f"fixture {index} has no usable string name")
    unique = len(set(declared))
    if len(declared) != unique:
        problems.append("duplicate case names")
    if unique < MINIMUM_UNIQUE_CASES:
        problems.append(f"{unique} unique case names; at least {MINIMUM_UNIQUE_CASES} required")
    return problems, unique
```

The name-check branch is the only new behavior. Valid corpora (16 or more all-distinct string names) still pass unchanged, so the "retain valid unique measurement" requirement holds. The current `tests/ollama-evidence/cases.json` (51 fixtures, all string names, 51 distinct after strip, exits 10/13/28) is not affected by this addition.

### F3. OK, ordering: duplicates and the minimum are rejected before any child

`run()` (lines 365-423, unchanged in the working file) computes `corpus_problems()` and takes the `if corpus:` branch before `elif tool_present:`. That branch only builds `unmeasured_record` entries, so `measure_case()` and `subprocess.run` are never reached. The absent-tool path and the duplicate path both precede the child stage. A duplicate corpus with a missing tool therefore reports the corpus error, not the tool error. This is consistent and fail-closed. Both problems can be reported together, and the verdict is 1 regardless of which one fires.

### F4. LOW, limitation under the stated contract: canonicalization is strip-only

The guard compares `str.strip()` results only. Inner-whitespace variants, case variants, and NFC/NFD variants are distinct to this guard. The in-flight fixtures are consistent with this: I checked every `expected_rejected: true` fixture in `tests/ollama-corpus-guard/` and each contains at least one exact duplicate after strip (`dupstrip >= 1`). `UnicodeDuplicate.json` and `TabCollision.json` rely on exact strip-equal pairs, not on Unicode normalization. If anyone later adds a fixture that expects rejection for NFC/NFD-equal or case-equal names, the current guard will not reject it. That would be a contract change, not a bug in the repair.

### F5. LOW, residual outside the contract: duplicate JSON keys in cases.json

`load_cases()` uses plain `json.loads`, which keeps the last value for a repeated key. A fixture object with two `"name"` keys would be counted under its last name only. The classifier rejects duplicate keys, but the harness does not. The committed `cases.json` was parsed with Python `json` for the count above; I did not scan the raw bytes for repeated keys. Not in the stated contract; noted only.

### F6. PENDING for GuardHarness: object envelope without a `cases` key

`load_cases()` accepts a top-level array, or an object with a `cases` array. An object envelope without `cases` raises `MeasureError` before `corpus_problems()` runs. The run then returns `total: 0`, `records: []`, and an `error` string with no `corpus:` prefix. A fixture runner that checks for a `corpus:` detail on records, instead of `verdict_exit` 1 plus a nonempty error, would classify that as wrong. Whether the in-flight `ObjectEnvelope.json` fixtures use `{"cases": [...]}` could not be verified from the fixture files alone. Pending the runner, which is not in this lane.

## In-flight fixtures (pending, not failures)

`tests/ollama-corpus-guard/` contains 11 JSON files (AdjacentDuplicate, AppendDuplicate, DistantDuplicate, MiddleDuplicate, MultipleDuplicates, ObjectEnvelope, PrependDuplicate, TabCollision, TriplicateName, UnicodeDuplicate, WhitespaceCollision). Structural read only:

- Every `expected_rejected: true` fixture has at least 16 distinct stripped names and at least one exact duplicate after strip. The old minimum guard cannot catch these; the duplicate check can.
- Every `expected_rejected: false` fixture has all names distinct after strip and at least 16 entries.
- Envelopes are `array` or `object` as the schema requires.

No runner output exists yet; these are pending. Nothing here is a final failure.

## Residual risk and verification gaps

- The working-file repair (F1) and the F2 gap were confirmed by reading only. L1 must run the harness once after edits to confirm the rejection path emits `corpus:` records with zero child spawns.
- The frozen `measure-before.py` should be checked against the manifest sha (done here: matches).
- The `UnicodeDuplicate` and `WhitespaceCollision` controls test strip-equal duplicates only. Their names say more than they cover.
- No tests or runs were executed; no installs or upgrades were made.

## Tool record

- Installs/updates: none.
- Commands: read-only `sha256sum`, `git show`, `diff`, `cmp`, `python3` JSON parse and count of fixtures, `jq` presence check, and directory listings. No measure.py or fixture run.

## Report

Report: .ufo/waves/round-15/build/advice/GuardReview.md
