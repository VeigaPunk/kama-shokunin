# CaseAudit10 — cases 20/21 literals and duplicate-guard invariance

Scope: static read only, no code execution. Sources read:
- `/home/vgpnk/Projects/shokunin/kama-shokunin/tests/ollama-evidence/cases.json` (51 entries; index 20 = lines 324-339, index 21 = lines 340-355)
- `/home/vgpnk/Projects/shokunin/kama-shokunin/tools/kama-ollama-evidence.py`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-14/measure.py` (post-repair state, 493 lines, mtime 2026-10-20 05:09:13)
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-15/frozen/measure-before.py` (pre-repair snapshot)

## Corpus facts that decide guard invariance

Parsed from cases.json: 51 fixtures, 51 distinct raw `name` values, 51 distinct `name.strip()` values; no blank names and no whitespace-padded names.

- index 20: `identity_conflict_name_model_alias_ambiguity` (cases.json:325), occurs once.
- index 21: `identity_conflict_digest_whitespace_not_stripped` (cases.json:341), occurs once.
- Both names are strip-invariant (`name == name.strip()`), so the guard's canonicalization `name.strip()` (measure.py:355) maps each name to itself.

## Case 20 — literal expectation and branch walk

Fixture (cases.json:324-339):
- tags.models[0] = `{name: "llama3:8b", model: "llama3:8b-ctx8192", digest: "sha256:1111…1111"}`
- ps.models[0] = `{name: "llama3:8b", model: "llama3:8b", digest: "sha256:1111…1111"}`
- `expect = "llama3:8b"`, `expected_exit = 1`, `expected_finding = "identity_conflict"`

Classifier path (`classify`, tools/kama-ollama-evidence.py:218-265):
1. `validate_capture` (172-188) accepts both envelopes: dict, `models` list, each entry dict, all identity/digest/marker fields strings.
2. `_matching` (190-192) returns exactly one tags match (entry `name == expect`) and exactly one ps match (`name == expect`); duplicate-selected branches at 226-229 do not fire.
3. `tag = tags[0]`; `_identity_conflict` (195-203) is true because name `llama3:8b` != model `llama3:8b-ctx8192`, both non-empty strings.
4. Line 234-235 returns `('identity_conflict', ['selected_tags_entry_name_model_conflict'])`.

Literal result: `finding_id = identity_conflict`, `verdict_exit = FINDING_EXIT['identity_conflict'] = 1` (FINDING_EXIT at 91-98), process exit 1. Payload also asserts `schema = kama-ollama-evidence/v1`, `expected_model = llama3:8b`, `readiness = unknown`, `scope = offline-captures-not-runtime`, `reasons = ['selected_tags_entry_name_model_conflict', 'capture_timing_unknown_exports_not_asserted_simultaneous', 'ps_expiry_not_evaluated']` (constants at 87-90, appended at 275).

Discriminating power: both digests are equal and the ps entry has name == model, so absent the tags name/model conflict branch the same capture pair would reach 261-264 and yield `loaded_same_digest` exit 0. The case pins conflict precedence over digest equality.

## Case 21 — literal expectation and branch walk

Fixture (cases.json:340-355):
- tags.models[0] = `{name: "llama3:8b", model: "llama3:8b", digest: " sha256:1111…1111"}` (leading space)
- ps.models[0] = `{name: "llama3:8b", model: "llama3:8b", digest: "sha256:1111…1111"}`
- `expect = "llama3:8b"`, `expected_exit = 1`, `expected_finding = "identity_conflict"`

Classifier path:
1. Both entries match `expect` once by `name`; duplicate-selected branches 226-229 do not fire.
2. `_identity_conflict` is false for both entries (name == model in each).
3. `_digest_present` (213-215) is true for the tags digest: it is a non-empty string; there is no strip, prefix, or format validation. So 238-241 do not return `unknown`.
4. `_remote_marker` (205-211) finds no `remote_model`/`remote_host` on either selected entry (243-252).
5. ps match exists, so 254-257 does not return `available_not_loaded`.
6. Line 259 compares exact strings: `" sha256:…" != "sha256:…"` is true; 259-260 returns `('identity_conflict', ['tags_ps_digest_mismatch'])`.

Literal result: `finding_id = identity_conflict`, `verdict_exit = 1`, process exit 1; `reasons = ['tags_ps_digest_mismatch', 'capture_timing_unknown_exports_not_asserted_simultaneous', 'ps_expiry_not_evaluated']`; same schema/readiness/scope assertions.

Discriminating power: if digest whitespace were stripped or normalized, line 259 would compare equal and 261-264 would yield `loaded_same_digest` exit 0. The case name pins the literal non-stripping behavior.

Both fixtures also satisfy `_valid_case` (329-345): non-empty string name/expect, `tags` and `ps` present, integer `expected_exit` in `FINDING_EXIT.values()`, string `expected_finding` key whose mapped exit equals `expected_exit`.

## Why the new corpus duplicate guard cannot alter these two results

Current guard (`corpus_problems`, measure.py:350-363):
- collects `name.strip()` for dict cases with non-empty stripped names (351-356);
- appends `"duplicate case names"` iff `len(declared) != unique` (358-359);
- preserves the existing minimum check `unique < MINIMUM_UNIQUE_CASES` (360-362).

For the committed corpus: `declared` length 51, `unique` 51, so `len(declared) != unique` is false and `unique < 16` is false; `problems == []`.

`run()` (367+) then takes `elif tool_present:` (381) and calls `measure_case` per index (385), exactly as the pre-repair snapshot did for duplicate-free corpora (measure-before.py:350-362 had only the minimum check). Consequences:

1. The guard reads only `case["name"]`; it never mutates `cases`, `expect`, capture bytes, or index order, and it never dedupes, skips, or renumbers fixtures.
2. The guard's only new behavior is corpus-wide fail-closed rejection: when `corpus` is non-empty, `run()` (377-379) emits one `unmeasured_record` per fixture (`passed: False`, `observed_*: None`, detail `corpus: duplicate case names`) and never enters the tempdir/child branch (381-385). There is no per-case guard path that could change an individual fixture's inputs or observed classification.
3. The child classifier is name-agnostic: measure.py passes only `--tags`, `--ps`, `--expect` (231-237); `classify()` (218-265) receives only the two capture documents and the expected model string. Fixture `name` is evidence text only (measure.py docstring 30-31; `case_name` 131-137).
4. The classifier's separate selftest duplicate gate (`run_selftest`, 347-365) compares raw non-empty names and passes because all 51 raw names are distinct; measure.py does not invoke `--selftest`, it invokes the classification CLI per case.

Therefore, with the corpus as committed, the guard's added predicate is false, no record is converted to unmeasured, and the case 20/21 child invocations, observed findings (`identity_conflict`), observed exits (1), and pass records are unchanged.

## Contrary evidence / limitations

1. Invariance depends on the corpus being duplicate-free. If cases 20/21 were placed in a corpus containing any repeated stripped declared name, the guard would not preserve their results: every fixture would be unmeasured and failed before any child. Verified duplicate-free: 51 raw-distinct and 51 stripped-distinct names.
2. Strip divergence between the two gates: the measure guard canonicalizes with `.strip()`, while the classifier selftest (`run_selftest`, 359-365) compares raw names. Names `"x"` and `" x "` would be rejected by the measure guard but accepted by the classifier selftest. Cases 20/21 have no padding, so this divergence does not touch them.
3. The guard is name-only. A corpus of identical capture fixtures under distinct names is not detected; "duplicate corpus" here means duplicate declared names, not duplicate content.
4. Case 21's expected result relies on `_digest_present` accepting a whitespace-prefixed digest as present. A whitespace-only digest is likewise "present"; two whitespace-only digests would compare equal and classify `loaded_same_digest` exit 0. That adjacent boundary is not covered by this fixture.
5. Case 20's expected result relies on branch precedence: the tags name/model conflict (234-235) is evaluated before digest comparison (259-264). The ps entry alone is non-conflicting, and the digests are equal, so removing or reordering that branch would flip the fixture to `loaded_same_digest` exit 0.
6. The guard landed in flight during this audit (measure.py grew 491 -> 493 lines; guard present at read time). Analysis is against that state; a later change from fail-closed rejection to per-case dedupe would not alter cases 20/21 because their names are unique, but it would change corpus-level semantics.
7. No execution, no verification commands, no edits outside this report, no tool installs.

Confidence: high for the static branch walk, literal IDs/exits, and the guard predicate; there is no runtime observation here.

Report: .ufo/waves/round-15/build/advice/CaseAudit10.md
