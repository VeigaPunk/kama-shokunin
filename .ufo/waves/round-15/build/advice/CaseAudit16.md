# CaseAudit16 — cases 32/33 literals vs the corpus duplicate guard

Read-only audit. No classifier, harness, or selftest was executed. One stdlib
`json.load` of `tests/ollama-evidence/cases.json` was used to count names; that is data
inspection, not a project-code run. No `lsp` device/server is mounted in this session, so
every definition/reference below comes from reading the defining source lines directly,
not from grep-as-semantic-proof. No tool installed or updated.

## Observed literals (zero-based indexes into the array)

| idx | name | source line | tags | ps | expect | expected_exit | expected_finding |
|---|---|---|---|---|---|---|---|
| 32 | `invalid_tags_models_missing` | `tests/ollama-evidence/cases.json:503` | `{}` | `{"models": []}` | `llama3:8b` | 2 | `invalid_input` |
| 33 | `invalid_ps_models_missing` | `tests/ollama-evidence/cases.json:513` | one `llama3:8b` entry, digest `sha256:1111…` | `{}` | `llama3:8b` | 2 | `invalid_input` |

Both are envelope-gate fixtures: the only defect is a capture object that omits the
`models` key. Case 32's ps is otherwise valid (`models` present, empty array); case 33's
tags entry is otherwise valid (`name`/`model`/`digest` all strings, no remote marker).

## Exact classifier branches

Harness staging (` .ufo/waves/round-14/measure.py:189-197`, `211-245`): `{}` is a dict, not
`None`, so `write_capture` serializes `{}\n`; `{"models": []}` becomes
`{"models": []}\n`. The child is invoked with `--tags tags.json --ps ps.json --expect
llama3:8b`.

Case 32 — `tools/kama-ollama-evidence.py`:
1. `read_json_file` (137-170): both files parse; no duplicate keys, no NaN.
2. `classify` line 220: `validate_capture(tags_document, 'tags')` → line 176
   `'models' not in document` → line 177 `_fail('tags_models_missing')` → `InputError`.
3. `_run` 511-513 catches it: `finding, reasons = 'invalid_input', ['tags_models_missing']`.
4. `classify_payload` (267-277): `verdict_exit = FINDING_EXIT['invalid_input'] = 2`
   (line 97), schema `kama-ollama-evidence/v1`, readiness `unknown`, scope
   `offline-captures-not-runtime`, plus the two constant reasons.
5. `_run` 514 returns `FINDING_EXIT[finding]` = 2; `main` passes it to `sys.exit`.

Case 33 — same file:
1. `read_json_file`: both parse.
2. `classify` 220: tags validates (entry is a dict; `name`, `model`, `digest` are strings;
   `remote_*` absent). Line 221: `validate_capture(ps_document, 'ps')` → `'models' not in
   {}` → `_fail('ps_models_missing')` → `InputError`.
3. `_run` 511-513 → `invalid_input` with reason `ps_models_missing`; payload `verdict_exit`
   2; process exit 2.

Precedence that makes these literals correct: both `validate_capture` calls (220-221) run
before `_matching` (223-224) and before every semantic step — duplicate selection (226-229),
no-tags (231), identity (233-236), digest (237-240), marker (242-249), ps presence (251),
digest comparison (256-258). Consequences:
- Case 33 cannot reach `available_not_loaded` (exit 1), which is what a selection-first
  order would produce (tags match exists, ps absent).
- Case 32 cannot reach `unknown` (exit 2) from "no tags match" — that would keep the exit
  but change the `finding_id`, so the harness would fail it on the finding assertion.

## Why the new duplicate-corpus guard cannot alter these results

Guard structure (`.ufo/waves/round-14/measure.py:350-362`): `corpus_problems` is
corpus-level only — it strips names, counts `unique`, and today emits a problem only when
`unique < MINIMUM_UNIQUE_CASES` (16) at line 360. `run` (365-423) calls it once at 372;
`if corpus:` at 377 emits one `unmeasured_record` per case (`passed: false`,
`observed_exit: null`, `detail` starting `corpus:`) and never enters the child path;
`elif tool_present:` at 381 is the only branch that calls `measure_case`.

Isolation chain for cases 32/33:
1. The committed corpus is 51 cases with 51 distinct names and 0 duplicates after `strip`
   (verified by the JSON parse above). Every case carries a non-empty string name.
2. A repaired predicate that adds duplicate detection (`len(canonical) !=
   len(set(canonical))`) and a blank/missing-name problem, while keeping `unique < 16`,
   therefore produces **no** problem for this corpus: 51 unique, no duplicates, no unnamed
   cases. `corpus` stays empty.
3. Execution then takes the same `elif tool_present:` path as before; each case is measured
   in document order, and case 32/33 records derive only from their own staged captures,
   `expect`, and the child's exit/stdout. The guard result is not consulted per case.
4. Case 32/33 names are already canonical: `invalid_tags_models_missing` and
   `invalid_ps_models_missing` have no surrounding whitespace, so `strip` is identity and
   they cannot collide with each other or with any other case.
5. Even in the rejection branch, the guard can only deny the whole corpus; it never rewrites
   `expected_exit`/`expected_finding` or any observed tuple. It cannot convert these
   `invalid_input`/2 literals into anything else — only suppress their measurement.
6. Guard-control corpora live in separate files (`tests/ollama-corpus-guard/*.json`,
   directory not present yet) and are built by cloning `cases[0]` (`loaded_same_digest`,
   `cases.json:2-17`), not cases 32/33; the committed `cases.json` is never mutated.

Therefore: for the real corpus the guard passes, and the literal expected pairs
(`invalid_input`, 2) for cases 32 and 33 are measured exactly as before. The guard's only
effect is on synthetic corpora that carry duplicate or unnamed case names.

## Contrary evidence and limits

- Exit 2 is shared by `unknown` and `invalid_input` (`FINDING_EXIT` 91-99). Exit code alone
  cannot prove these two cases; the discriminating assertion is `finding_id`. The harness
  checks both (`measure.py:299` exit mismatch, `304` finding mismatch), so the pair is
  conjunctive and neither half is redundant.
- The only way these literals break without touching the fixtures is a reordering of
  `classify` 220-221 relative to selection: case 33 would flip to `available_not_loaded`/1
  and case 32 to `unknown`/2 (exit matches, finding does not). The current order is the
  evidence that the literals are right; the guard does not touch `classify`.
- The duplicate predicate described above is advisory from `MeasurementPlan.md`, not yet in
  the file: line 360 still only enforces `unique < 16`. This audit's isolation argument is
  conditional on the guard remaining name-based, per the shared fixture schema
  `{name, names[], envelope, expected_rejected}`. A content-level "duplicate corpus" rule
  (e.g. rejecting repeated payloads) is not in that schema and would be wrong scope; no
  such rule is evidenced.
- I did not run `measure.py`, the classifier, `--selftest`, or any guard fixture. Counts
  (51/51 unique, 0 stripped duplicates) are observed from `json.load` of the committed file;
  child exit codes are read from source, not observed.

Confidence: high for the literals, the branch lines, and the guard isolation (direct source
reads); conditional on the repaired guard being corpus-level and name-based as specified.

Report: .ufo/waves/round-15/build/advice/CaseAudit16.md
