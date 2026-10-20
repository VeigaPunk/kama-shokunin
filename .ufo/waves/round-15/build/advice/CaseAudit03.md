# CaseAudit03 (KamaR15.CaseAudit03-3) — cases 6/7 and duplicate-guard non-interference

Scope: read-only audit of `tests/ollama-evidence/cases.json` indexes 6 and 7 plus the classifier branches they hit, and of whether the new duplicate-corpus guard in `.ufo/waves/round-14/measure.py` can change those two original results. No code was executed (no classifier, runner, harness, selftest, test, build, lint, or formatter). Every statement is from file reads; structural predictions are marked `[INFERENCE]`.

## Observed corpus context

- `tests/ollama-evidence/cases.json` is a 51-element array (51 `expected_finding` lines, 768 lines); all 51 names are non-empty and pairwise distinct, including the two audited names. This matches the round-14 verifier's independent count of 51 cases / 51 unique names (`corpus/lessons/round-14-verifier-spotcheck.md`).
- Index 6 (zero-based): `loaded_remote_marker_only_on_unselected_tags_entry`, declared at `cases.json:103`, `expect: "llama3:8b"`, `expected_exit: 0`, `expected_finding: "loaded_same_digest"` (`cases.json:103-118`).
- Index 7 (zero-based): `loaded_ignores_past_expires_at`, declared at `cases.json:120`, `expect: "llama3:8b"`, `expected_exit: 0`, `expected_finding: "loaded_same_digest"` (`cases.json:120-134`).

## Case 6 — exact branch trace

Fixture: tags carries an unselected `qwen3:4b` entry with `remote_model`/`remote_host` and digest `sha256:2222…`, plus a selected `llama3:8b` entry with digest `sha256:1111…`; ps carries one `llama3:8b` entry with the same `sha256:1111…` digest. Child argv is `python -I -B tools/kama-ollama-evidence.py --tags tags.json --ps ps.json --expect llama3:8b` (`measure.py:211-236`).

Branches in `tools/kama-ollama-evidence.py`:

1. `validate_capture` (`:172-187`): both documents are objects with `models` arrays; every entry is an object; `name`/`model`/`digest`/`remote_model`/`remote_host`, where present, are strings. Passes; returns both tags entries and the one ps entry.
2. `_matching` (`:190-192`) uses exact `name == expected or model == expected`. Only `llama3:8b` matches in tags (the qwen3 entry's name and model are `qwen3:4b`); one ps match. So `len(tags_matches) == 1` and `len(ps_matches) == 1`.
3. `classify` (`:218-265`) precedence:
   - `:226` / `:228` duplicate-selection checks: not `> 1` → no `invalid_input`.
   - `:231` `not tags_matches`: false (one match exists).
   - `:234` `_identity_conflict(tag)`: selected entry has `name == model == llama3:8b` → false.
   - `:236` ps identity conflict: false.
   - `:238` / `:240` `_digest_present`: both selected digests are non-empty strings → true.
   - `:243` `_remote_marker(tag)` inspects only the **selected** tags entry; it has neither marker field → `None`. The unselected qwen3 entry's nonempty `remote_model`/`remote_host` are never consulted for the marker finding, so `remote_inventory` is not returned.
   - `:247-252` selected ps entry has no marker → `None`.
   - `:254` `not ps_matches`: false.
   - `:259` selected digests are equal → `:261` returns `loaded_same_digest` with reasons `['tags_ps_digest_equal', 'metadata_correspondence_not_readiness']` plus the constant reasons; `FINDING_EXIT['loaded_same_digest'] == 0` (`:92`), so `classify_payload` sets `verdict_exit: 0` and the process exits 0.
4. Runner grading (`measure.py:296-325`): observed exit 0 equals `expected_exit` 0; `finding_id` equals `expected_finding`; schema `kama-ollama-evidence/v1`; `verdict_exit` equals the process exit; `readiness` `unknown`; `scope` `offline-captures-not-runtime` → record `passed: true` (`:325`).

## Case 7 — exact branch trace

Fixture: tags has one `llama3:8b` entry with digest `sha256:1111…` and `modified_at: 2030-01-01T00:00:00Z`; ps has one `llama3:8b` entry with the same digest and `expires_at: 2001-01-01T00:00:00Z` (past).

1. `validate_capture` (`:172-187`) type-checks only `IDENTITY_FIELDS + ('digest',) + MARKER_FIELDS` (`:184-186`); `modified_at`/`expires_at` are unknown keys and are tolerated. Passes.
2. One exact tags match and one exact ps match → duplicate checks (`:226`, `:228`) do not fire; identity checks (`:234`, `:236`) are false because `name == model`.
3. Digests present (`:238`, `:240`); no remote markers on either selected entry (`:243`, `:247`); ps match exists (`:254`).
4. Digests are equal → `:261` `loaded_same_digest`, exit 0; runner grading passes as in case 6.

No branch reads `modified_at` or `expires_at`: the only occurrences in the repository's audited files are the fixture literals at `cases.json:123,128`; the tool never parses timestamps. The past `expires_at` is therefore inert by non-evaluation, and every payload carries the constant reason `ps_expiry_not_evaluated` (`:89`) as a scope statement, not as evidence of an expiry comparison.

## New duplicate-corpus guard — exact code and effect

Current `.ufo/waves/round-14/measure.py` (493 lines, mtime 2026-10-20 05:09:13) contains, in `corpus_problems()` (`:350-364`):

```python
declared = []
for case in cases:
    name = case.get("name") if isinstance(case, dict) else None
    if isinstance(name, str) and name.strip():
        declared.append(name.strip())
unique = len(set(declared))
problems = []
if len(declared) != unique:
    problems.append("duplicate case names")
if unique < MINIMUM_UNIQUE_CASES:
    problems.append(...)
return problems, unique
```

A `diff -u .ufo/waves/round-15/frozen/measure-before.py .ufo/waves/round-14/measure.py` shows exactly this two-line addition and nothing else.

`run()` (`:367-425`) calls `corpus_problems` at `:374` before any child is staged. When `corpus` is non-empty (`:377-380`) every case becomes an `unmeasured_record` (`:159-177`: `observed_exit: None`, `passed: False`, `reasons: [detail]`, `verdict_exit` forced to 1); when it is empty the flow enters `elif tool_present:` (`:381`) and calls `measure_case` per case (`:385`), exactly as before the guard.

## Why the guard cannot alter cases 6/7

- The guard reads only each case's `name` metadata. It never reads `tags`, `ps`, `expect`, `expected_exit`, or `expected_finding`, and it never invokes the classifier or rewrites a classification.
- Both audited names are non-empty strings with no leading/trailing whitespace, so `name.strip()` yields two distinct strings. For the committed corpus, `len(declared) == unique == 51`, `51 >= 16`, so `problems == []`; the guard is a no-op and `run()` takes the unchanged `measure_case` path.
- The guard's only possible effects are corpus-level: adding `"duplicate case names"` to the `error`/`unmeasured_record` detail (and thereby failing the whole run before any child) or leaving the corpus untouched. It cannot convert `loaded_same_digest`/0 into a different finding/exit; a firing guard would only produce unmeasured failures with `observed_*` null.
- `unique_case_names` in the output (`:412`) is still computed by the same expression and stays 51 for this corpus.
- The tool-side selftest duplicate check (`tools/kama-ollama-evidence.py:359-365`, `duplicate_case_names`, `MIN_CASES = 16` at `:84`) is a separate path in a file the guard repair does not touch, so selftest behavior for these cases is unchanged as well.

## Contrary evidence and boundaries

- **Case 6 marker scope is finding-only.** `validate_capture` type-checks `remote_model`/`remote_host` on *every* entry, selected or not (`:184-186`). A non-string marker on the unselected qwen3 entry would make the whole capture `invalid_input`; only the `remote_inventory` finding is restricted to selected entries. The fixture name is accurate for the finding precedence, not for type validation.
- **Case 7 is a non-evaluation control, not an expiry rule.** A reader expecting a past `expires_at` to imply "not loaded" is contradicted by the literal expected result: the classifier deliberately makes no timestamp/expiry/current-state claim (module docstring `tools/kama-ollama-evidence.py:53-54`), and `ps_expiry_not_evaluated` is a constant appended to every payload.
- **Guard canonicalization is `strip()` only.** Names differing by internal whitespace, case, or Unicode form are distinct; cases with missing/blank names are excluded from `declared` and fall back to `case-NN` display labels (`case_name`, `:131-136`), so duplicate fallback labels are not rejected by this guard. Neither limitation is exercised by indexes 6/7, but the guard's guarantee is narrower than "any duplicated corpus".
- **No execution performed**, so the traces above are static `[INFERENCE]` about runtime output; the fixture literals and branch order are observed facts.

## Limitations

- Only `cases.json` indexes 6 and 7 were audited; the remaining 49 cases and the sibling-owned guard fixtures (`tests/ollama-corpus-guard/*.json`, authored by other seats) were not evaluated.
- Line numbers reflect the files as read at 2026-10-20 05:09-05:12; concurrent sibling edits to the guard harness do not affect the `measure.py` guard lines cited, but could move harness line numbers (none cited).
- No verification commands were run per assignment; the guard's rejection of duplicate corpora and the 51/51 measurement are structural predictions here, to be verified once by L1.
- No tools were installed or updated; no pacman/uv/npm actions were taken.

Report: .ufo/waves/round-15/build/advice/CaseAudit03.md
