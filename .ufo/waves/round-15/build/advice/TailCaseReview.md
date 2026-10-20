# TailCaseReview — round-15 read-only review of original cases 40–50

Scope: `tests/ollama-evidence/cases.json` indexes 40–50 (original round-14 fixtures): expected findings, exits, and distinct names. Read-only static trace against `tools/kama-ollama-evidence.py`, plus the in-flight round-14 `measure.py` guard repair and the pending `tests/ollama-corpus-guard/` harness. No tests, builds, measure runs, or runner invocations were executed. Only read-only inspection was done (file reads, `sha256sum`, `git status/show/diff` for tracking, and Python JSON parsing of fixtures and receipts).

Tooling: none installed or updated.

## 1. Cases 40–50: names and expected findings (verdict: consistent)

Raw and stripped names are distinct for all 51 cases; no duplicate names exist in cases.json (`len(names)=51`, `len(set)=51`, stripped distinct 51).

| idx | name | expected | exit | deciding rule in `tools/kama-ollama-evidence.py` | round-14 receipt |
|---|---|---|---|---|---|
| 40 | invalid_duplicate_selected_tags | invalid_input | 2 | `tags_matches > 1` → invalid (L226–227) | final pass |
| 41 | invalid_duplicate_selected_ps | invalid_input | 2 | `ps_matches > 1` → invalid (L228–229) | final pass |
| 42 | invalid_duplicate_selected_ps_with_remote_marker | invalid_input | 2 | duplicate ps check precedes remote-marker check (L228–229 before L246–252); ps[0] carries `remote_host`, ps[1] does not | final pass |
| 43 | invalid_remote_marker_number_type | invalid_input | 2 | `validate_capture` non-string `remote_model` (L184–186) | final pass |
| 44 | invalid_remote_marker_boolean_type | invalid_input | 2 | non-string `remote_host` (`false`) (L184–186) | final pass |
| 45 | invalid_remote_marker_null_type | invalid_input | 2 | `null` is present and non-string (L184–186) | final pass |
| 46 | remote_missing_digest | unknown | 2 | digest-presence check (L238–239) precedes remote marker (L243–245) | draft observed `remote_inventory`/1 (red); final `unknown`/2 (pass) |
| 47 | tags_none_ps_duplicates | invalid_input | 2 | ps duplicate (L228–229) precedes no-tags `unknown` (L231–232) | draft observed `unknown`/2 (red); final `invalid_input`/2 (pass) |
| 48 | invalid_unparsable_tags_body | invalid_input | 2 | `read_json_file` JSON decode failure (L164–169) | final pass |
| 49 | invalid_duplicate_raw_json_key | invalid_input | 2 | `_pairs` object_pairs_hook raises `duplicate_json_key` (L124–130, L165) → `tags_input_duplicate_json_key` | final pass |
| 50 | invalid_ps_top_level_array | invalid_input | 2 | `ps_capture_not_object` (L174–175) | final pass |

Every expected finding has an exit consistent with `FINDING_EXIT` (L91–98). Both `expected_finding` and `expected_exit` agree for all 11 rows.

Receipt cross-check (`.ufo/waves/round-14/acceptance.json`):
- Final measure record (`/records/2`): 51/51 pass. Its `tool_sha256` (38d1f5d2…) equals the current `tools/kama-ollama-evidence.py`; `cases_sha256` (4a4de0b8…) equals the current `cases.json`.
- Draft/causal-red records (`/records/1`, `/causal_red`): 49/51, and the only failures are indices 46 and 47, as described above.
- `/records/0` is the tool-absent baseline (`unsupported`), which is expected.

Note: names 40–50 test per-capture entry duplicates and classifier precedence. They are not case-name duplicates and do not exercise the corpus-level guard. Do not conflate the two kinds of "duplicate" in the new harness.

## 2. Findings on the in-flight duplicate-corpus guard (pending; not final)

State at read time (05:09): `.ufo/waves/round-14/measure.py` is modified (`git diff 6e348e2`: +2 lines, `if len(declared) != unique: problems.append("duplicate case names")` inserted before the minimum check at L358). The frozen original `.ufo/waves/round-15/frozen/measure-before.py` (sha fda61e…) is byte-identical to committed `6e348e2:.ufo/waves/round-14/measure.py`, so the frozen copy is a valid pre-fix baseline. `tests/ollama-corpus-guard/` has 12 fixture files still being written (mtimes 05:09:10–05:09:43).

### F1 — Medium (pending): blank, missing, or non-string names bypass duplicate detection and unique counting
`corpus_problems` (round-14 `measure.py` L350–364) collects only names where `isinstance(name, str) and name.strip()`. Two fixtures named `""` (or whitespace-only, or with no `name`) are neither flagged as duplicates nor counted toward the minimum. `case_problems` (L139–150) does not check `name`. So a corpus with 16 valid unique names plus two blank-named fixtures passes the corpus guard, and each blank-named fixture runs a child (labelled `case-NN`). This conflicts with the shared fixture schema, which requires a unique descriptive `name` per fixture, and with the docstring's "a duplicated corpus fails the whole measurement before any child is spawned." The pending harness contains no blank or missing-name control. Recommendation: reject any fixture whose name is not a non-blank string, before any child; add a blank-duplicate control with at least 16 distinct valid names.

### F2 — Low (pending): "strip as existing runner" is inaccurate for the runner
The shared-fixture contract says "Guard canonicalizes names with strip as existing runner." The stripping exists only in round-14 `measure.py` (`corpus_problems` L350–364; `case_name` L131–136). `tools/kama-ollama-evidence.py` `run_selftest` (L359–365) compares raw names with `len(names) != len(set(names))`, with no strip and no unique-count check. Consequences:
- A harness that targets the runner's `--selftest` path will not reject `PrependDuplicate-padded-strip-collision` or `TriplicateName_array_n08_triplicated_strip_equivalent`. The harness must target `measure.py`, not the runner selftest. The contract should name the target explicitly.
- The runner selftest's `MIN_CASES` check counts entries, not unique names. It is weaker than the corpus guard, although it rejects exact duplicates before any child.
- The shared-schema text should be corrected so it does not claim the runner strips.

### F3 — Low (pre-existing; comment inaccurate): "byte-identical staging" is not byte-identical
`measure.py` `write_capture` (L189–196) serializes with `ensure_ascii=False`. The comment says "Byte-identical staging rule shared with the classifier's selftest." The runner's `_fixture_text` (runner L310–313) uses `ensure_ascii=True`. For non-ASCII fixtures (for example, the pending `UnicodeDuplicate` cases), the staged bytes differ while the parsed JSON is equal. Classifier verdicts are unaffected. The comment is false. Recommendation: correct the comment, or align the serializers if the byte claim is kept.

### F4 — Info: repair scope limits
- The repair covers only the `measure.py` path. The runner's own `--selftest` (`tools/kama-ollama-evidence.py`, L347–445) is a separate, weaker guard (F2).
- Stripped equality is the only normalization. Unicode-visually-identical names (NFC vs NFD) are distinct, and case variants are distinct by design (the classifier is case-sensitive). Neither is a defect under the stated exact-string policy, but the guard makes no normalization claim and should not.
- The new guard is pre-child: `run()` builds `unmeasured_record` for every case when `corpus` is non-empty and never calls `measure_case`, so the invalid-case child count is zero as required. Verified by static read only.

## 3. Pending harness: structural check at read time (pending, not final)

`tests/ollama-corpus-guard/*.json` (12 files, 50 fixtures at read time). Parsed read-only:
- Every file is a JSON array. Every fixture has exactly the keys `{name, names, envelope, expected_rejected}`.
- Every `expected_rejected: true` fixture has at least 16 stripped-distinct names (minimum observed 16, so the old `unique < 16` guard cannot catch it). The duplicate is present in each.
- Every `expected_rejected: false` control has all names distinct, with at least 16 names (16 or 17 or 32).
- Envelopes are `array` or `object` only.

These checks are structural only. They do not verify the clone rule (every fixture identical to the original first-passing case except `names`/`envelope`) because the harness does not exist yet. Re-check once the harness and the final fixture set land.

## 4. Residual risk and verification gaps
- All findings are static. Nothing was executed, so the claims about runtime behaviour of the classifier, the repaired guard, and the red/green matrix are unverified here. L1 should run the verification once after edits.
- `measure.py` and the harness were in motion (mtimes 05:09). F1–F3 may already be addressed by the time they are read. Recheck against the final file hash.
- The cases 40–50 conclusions depend on the current runner hash (38d1f5…) matching the round-14 receipt, which I confirmed by hash but did not re-run.

Report: .ufo/waves/round-15/build/advice/TailCaseReview.md
