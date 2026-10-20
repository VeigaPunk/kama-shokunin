# Round-15 C1 advisory: duplicate-corpus guard gate decisions

Lane: advisory only. No product, harness, fixture, or receipt files were edited. No checks, tests, or builds were run. No tools were installed or updated.

## Observed source facts (read-only)

Source: `kama-shokunin/.ufo/waves/round-14/measure.py` (blob #B6F1 at read time).

- `corpus_problems(cases)` (lines 350-362) collects `name.strip()` for each dict fixture whose `name` is a non-blank string. It counts `len(set(declared))` and rejects only when that unique count is below `MINIMUM_UNIQUE_CASES = 16`.
- Gap: duplicate names are never rejected. A corpus with 16 or more distinct stripped names and any repeated name (exact or whitespace-only variant such as `"x"` and `" x "`) passes the guard. `run()` then measures every entry, so the duplicate corpus measures as valid.
- Ordering is already correct for the "no child before rejection" requirement. `run()` (lines 365-423) calls `corpus_problems` at line 372 and, when `corpus` is non-empty, emits `unmeasured_record` for every fixture (line 377-378) and never reaches the `tool_present` branch that creates a tempdir or calls `measure_case` (which is the only path that calls `subprocess.run`). A fix inside `corpus_problems` therefore blocks all child processes.
- Secondary inconsistency: `case_name()` (lines 131-136) returns the unstripped name for records, while the guard counts stripped names. Records for `" x "` show `" x "`. Cosmetic; not required for the fix.
- Secondary gap: a fixture with a missing or blank `name` is excluded from `declared` but still measured when the other 16 names pass. Recommended to reject with the same guard.

## Advised minimal guard change (not applied)

Replace `corpus_problems` in `kama-shokunin/.ufo/waves/round-14/measure.py` (owner: the executor assigned to that file). Use `collections.Counter` (import needed; add it at the top import block):

```python
def corpus_problems(cases):
    declared = []
    problems = []
    for index, case in enumerate(cases):
        name = case.get("name") if isinstance(case, dict) else None
        if isinstance(name, str) and name.strip():
            declared.append(name.strip())
        else:
            problems.append(f"fixture {index} has no non-blank name")
    counts = Counter(declared)
    unique = len(counts)
    duplicates = sorted(name for name, count in counts.items() if count > 1)
    if duplicates:
        problems.append(f"duplicate case names after strip: {duplicates}")
    if unique < MINIMUM_UNIQUE_CASES:
        problems.append(
            f"{unique} unique case names; at least {MINIMUM_UNIQUE_CASES} required"
        )
    return problems, unique
```

Gate decision:
- Required: the duplicate check (`duplicates` branch). This is the bug fix. Without it, the guard cannot distinguish a duplicate corpus with at least 16 distinct names.
- Recommended, same function: the blank/missing-name check. Without it, a nameless fixture can ride along a valid 16-name corpus.
- Not advised: changing the 16 threshold, changing `run()` control flow, or changing `case_name()`. None are needed for the bug and each would widen the diff.
- Keep the `unique_case_names` field as the distinct stripped count. Add no new schema fields. Any change to the output schema would invalidate the immutable round-14 receipt's comparison basis.

## Advised fixture set (tests/ollama-corpus-guard/*.json)

Directory does not exist at read time; the fixture owner creates it. Schema: array of `{name, names, envelope, expected_rejected}`. Every fixture is identical except `names` and `envelope`, and the harness clones the first passing case from `tests/ollama-evidence/cases.json` (`loaded_same_digest`, line 3) for each `names` item.

| file | envelope | names | distinct stripped | expected_rejected |
|---|---|---|---|---|
| valid-16-distinct.json | array | 16 distinct, e.g. `guard-valid-01`..`guard-valid-16` | 16 | false |
| valid-18-distinct-object.json | object | 18 distinct | 18 | false |
| invalid-exact-duplicate-17.json | array | 16 distinct plus one exact repeat (17 entries) | 16 | true |
| invalid-whitespace-duplicate-18.json | array | 16 distinct plus `" guard-valid-03 "` alongside `"guard-valid-03"` (18 entries) | 16 | true |
| invalid-object-duplicate-18.json | object | 16 distinct plus two repeats (18 entries) | 16 | true |

Acceptance for the fixture set (for the reviewer, not run here): the old `corpus_problems` accepts all three invalid controls (16 distinct stripped names) and therefore measures them; the advised version rejects them with zero child processes and still measures both valid controls.

## Source boundary candidate sample (paths under kama-shokunin)

- `.ufo/waves/round-14/measure.py`: the only file whose logic changes (`corpus_problems` plus one import). Keep at this historical path (contract: final runner stays here; old receipt immutable).
- `tests/ollama-evidence/cases.json`: fixture source for cloning; read-only. 768 lines; first fixture `loaded_same_digest` at line 3.
- `tools/kama-ollama-evidence.py`: child classifier whose sha is recorded in every measure output (`tool_sha256`). Do not edit; the sha is the boundary.
- `tests/ollama-corpus-guard/*.json`: new fixture directory (does not exist yet). Owned by the fixture owner.
- `.ufo/waves/round-15/build/advice/`: this report's directory. Holds `swarm-registry.json` (not mine; not touched).
- `.ufo/waves/round-15/frozen/`: exists but is empty at read time. Contract requires `frozen/measure-before.py` taken before the source edit.
- `.ufo/waves/round-14/` census and validate artifacts (`sources-final-census.json`, `sources-final-validate.json`, `validation.json`, `integration-review.json`): these record hashes of `measure.py`. They will be stale after the edit. Not read in detail; flagged for the census owner.

## Limitations

- Did not read `measure.py` lines 3-41, 45-52, 73-79 (LIMITS), 153-158, 177-210, 240-299 (child result parsing), or 366-367 edge cases beyond what is quoted. The advised change does not touch them, but the reviewer should confirm no other reference to `corpus_problems`' return shape exists.
- Did not scan `cases.json` (768 lines) for existing duplicate names. Whether the current round-14 corpus is itself duplicated is unknown from this report. Per the no-checks rule, this was not measured.
- The fixture schema beyond the contract's description (`name`, `names`, `envelope`, `expected_rejected`) was not observed on disk.
- Advice only: the minimal patch above is not applied and has not been executed or type-checked.
- No installs or updates were performed; no tooling record is needed for this report.
