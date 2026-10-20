# CaseAudit17 — cases 34/35 literals and duplicate-guard inertness

Seat: `KamaR15.CaseAudit17-3` (leaf scout). Scope: zero-based indexes 34 and 35 of
`tests/ollama-evidence/cases.json`, the classifier path that grades them, and the repaired
duplicate-corpus guard in `.ufo/waves/round-14/measure.py`. Static reads only; the classifier,
harness, and fixtures were not executed. Fact commands used: `jq` name enumeration, `sha256sum`,
`diff`, `grep`, `sed`, `wc`. No tools installed or updated.

## Anchors

| Artifact | SHA-256 | State |
|---|---|---|
| `tests/ollama-evidence/cases.json` | `4a4de0b85009c42804e43c8ae8833bd6f0673edc71ae5ec8baa1e3201e158ae4` | 51 cases; matches the `cases_sha256` in `.ufo/waves/round-14/acceptance.json` |
| `tools/kama-ollama-evidence.py` | `38d1f5d216181bdb7693582027da83eace707f111f42dd32785d386ffe78fb02` | 531 lines; matches the round-14 receipt tool hash |
| `.ufo/waves/round-14/measure.py` | `46c5866d73a4f875353ff59c6929615149a1f4f4acf69b0b07deeb99d5445257` | 493 lines; repaired guard present |
| `.ufo/waves/round-15/frozen/measure-before.py` | not recomputed | pre-edit snapshot; diff below |

Static corpus check: 51 case objects, 51 raw names, 51 distinct raw names, 0 names changed by
`strip`, 0 names outside `[a-z0-9_]*`, 0 exact duplicates. The two assigned names are therefore
distinct under both raw and stripped canonicalization.

## Case index 34 — `invalid_tags_models_not_array`

Literal block `tests/ollama-evidence/cases.json:524-535`:

- `name` (`:525`) = `invalid_tags_models_not_array`
- `tags` (`:526-528`) = `{"models": {"name": "llama3:8b", "model": "llama3:8b", "digest": "sha256:1111…"}}` — `models` is a JSON object, not an array
- `ps` (`:529-531`) = `{"models": []}`
- `expect` (`:532`) = `llama3:8b`
- `expected_exit` (`:533`) = `2`
- `expected_finding` (`:534`) = `invalid_input`

Classifier branch, statically traced:

1. Harness staging serializes the `tags` object as UTF-8 JSON (`measure.py:189-196`); the child
   receives `--tags`, `--ps`, `--expect` only (`measure.py:230-235`).
2. `classify` calls `validate_capture(tags_document, 'tags')` first, then ps
   (`tools/kama-ollama-evidence.py:220-221`). Tags validation sees a dict document with a
   present `models` key, then `if not isinstance(models, list)` fails at `:179-180` with
   `_fail('tags_models_not_array')`. The ps document is never validated on this path.
3. `InputError` propagates out of `classify`; `_run` catches it at `:511-512` and substitutes
   `finding = 'invalid_input'`, `reasons = ['tags_models_not_array']`.
4. `classify_payload` emits `schema = kama-ollama-evidence/v1`, `finding_id = invalid_input`,
   `verdict_exit = 2`; `_run` returns `FINDING_EXIT['invalid_input'] = 2` (`:91-98`, `:513-514`).
5. Harness comparison: observed exit `2 == expected_exit 2`; observed finding
   `invalid_input == expected_finding`; schema/verdict_exit/readiness/scope constants match
   (`measure.py:296-330`). Expected pass.

Selftest validity: `_valid_case` (`tools/kama-ollama-evidence.py:329-344`) accepts the case because
`expected_exit 2` is in `FINDING_EXIT.values()` and `FINDING_EXIT['invalid_input'] == 2`.

## Case index 35 — `invalid_tags_entry_not_object`

Literal block `tests/ollama-evidence/cases.json:536-547`:

- `name` (`:537`) = `invalid_tags_entry_not_object`
- `tags` (`:538-540`) = `{"models": ["llama3:8b"]}` — the sole entry is a string, not an object
- `ps` (`:541-543`) = `{"models": []}`
- `expect` (`:544`) = `llama3:8b`
- `expected_exit` (`:545`) = `2`
- `expected_finding` (`:546`) = `invalid_input`

Classifier branch, statically traced:

1. `validate_capture(tags_document, 'tags')`: `models` is a list, so the loop at `:181-183`
   reaches entry index 0; `if not isinstance(entry, dict)` fails with
   `_fail('tags_entry_0_not_object')`. Again ps is never validated.
2. Same `InputError` catch at `_run:511-512`; `finding_id = invalid_input`,
   `reasons = ['tags_entry_0_not_object']`; return `FINDING_EXIT['invalid_input'] = 2`.
3. Harness comparison is identical to case 34; expected pass with exit 2 and `invalid_input`.

Both cases are Tier-1 structural failures that occur before any name matching, duplicate-selection,
remote-marker, or digest logic. Neither `expect` value participates in the failure.

## Why the repaired duplicate-corpus guard cannot alter these results

Repaired guard, `.ufo/waves/round-14/measure.py:350-364`:

- `:352-356` builds `declared` from `case.get("name").strip()` only for dict cases with a non-empty
  string name.
- `:357` `unique = len(set(declared))`.
- `:358-359` new predicate: `if len(declared) != unique: problems.append("duplicate case names")`.
- `:360-363` preserved minimum predicate: `if unique < MINIMUM_UNIQUE_CASES` (16).

The only delta between `frozen/measure-before.py` and the repaired runner is those two lines; `diff`
shows no change to `run()`, `measure_case()`, staging, child argv, or comparison. Therefore the
per-case grading path for these two fixtures is unchanged.

For the committed corpus:

1. `declared` has 51 entries; `set(declared)` has 51; `len(declared) == unique` → the duplicate
   predicate is false. `unique = 51 >= 16` → the minimum predicate is false. `corpus` is empty.
2. `run()` (`:367-381`) evaluates `corpus_problems` before the branch. With `corpus == []` it takes
   `elif tool_present:` (`:381`) and calls `measure_case` for every index, including 34 and 35.
3. The guard reads only the `name` field. It never mutates the case objects, so `tags`, `ps`,
   `expect`, `expected_exit`, and `expected_finding` are untouched. Record names still come from
   `case_name()` (`:131-136`), which returns the raw name.
4. The case name is never passed to the child. Child argv is `--tags`, `--ps`, `--expect`
   (`:230-235`), and the temp directory is named by index (`:218-223`). Stripped-name
   canonicalization has no path into classification.
5. If the guard ever fired, `run()` would take `if corpus:` (`:377-380`) and build
   `unmeasured_record` for every case from `record_triplet(case)` (`:153-178`), preserving the
   literal `expected_exit`/`expected_finding` while setting `observed_* = None`, `passed = False`,
   and `error = "corpus: …"`. Even the rejection path cannot rewrite a literal expectation; it can
   only mark the corpus unmeasured. For this duplicate-free corpus that path is not taken.

The classifier's own selftest has a separate duplicate-name gate at
`tools/kama-ollama-evidence.py:359-365`, using raw non-empty names (`len(names) != len(set(names))`).
Both assigned names are unique there as well, so neither the raw-name selftest gate nor the
strip-canonicalized harness gate changes their outcomes.

## Contrary evidence and limits

- The pre-repair guard did **not** reject duplicates when at least 16 distinct names existed
  (`frozen/measure-before.py:355-362`), despite the module docstring (`measure.py:13-14`) and
  `LIMITS[3]` (`:77`) claiming it did. The current two-line insert is the repair; this report is
  pinned to SHA `46c5866d…` (493 lines). A later edit to the guard could invalidate the inertness
  claim.
- The two guards use different canonicalization: harness strips, classifier selftest does not. A
  future corpus whose names differ only by surrounding whitespace would pass the selftest gate and
  be rejected by the harness. The assigned names contain no whitespace, so this divergence does not
  apply.
- `corpus_problems` treats non-string/blank names as undeclared, so they are neither counted nor
  duplicate-checked. `cases.json` has no such names; the policy is unchanged by the repair.
- "Cannot alter results" means the literal `expected_exit`/`expected_finding` and the per-case
  measurement path. A false-positive guard firing would change measurement **status** for all 51
  cases (all unmeasured, exit 1) while leaving the literals intact. It cannot occur for the current
  corpus.
- All exit/finding outcomes above are static code traces, not executions; no child process was run.
- Corpus dependence: if `cases.json` is edited (names or expectations), the analysis must be
  repeated against the new bytes. The current corpus hash matches the round-14 measured receipt.

Report: .ufo/waves/round-15/build/advice/CaseAudit17.md
