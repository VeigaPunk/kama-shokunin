# CaseAudit18 (KamaR15.CaseAudit18-3): scout, static read only

Scope: cases at zero-based indexes 36 and 37 of `tests/ollama-evidence/cases.json`, the classifier path each one takes, and whether the round-15 duplicate-name guard can change their results. I executed no code. All paths below are relative to `/home/vgpnk/Projects/shokunin/kama-shokunin`.

## Snapshot pins (observed)

| Artifact | SHA-256 | Note |
|---|---|---|
| `tests/ollama-evidence/cases.json` | `4a4de0b85009c42804e43c8ae8833bd6f0673edc71ae5ec8baa1e3201e158ae4` | Same as `cases_sha256` in every round-14 receipt run. 51 records. |
| `tools/kama-ollama-evidence.py` | `38d1f5d216181bdb7693582027da83eace707f111f42dd32785d386ffe78fb02` | Same as receipt `tool_sha256` and `round-14/advice/Classifier.md`. Not touched in round 15. |
| `.ufo/waves/round-15/frozen/measure-before.py` | `fda61e001ca8c2533c99a1759bb4b82f3260a72fafccf72f863f3f4e3684b60d` | Same as `frozen/manifest.json` and the `HEAD` (`6e348e2`) blob of `.ufo/waves/round-14/measure.py`. |
| `.ufo/waves/round-14/measure.py` (current) | `46c5866d73a4f875353ff59c6929615149a1f4f4acf69b0b07deeb99d5445257` | mtime 05:09:13 local. `diff -u` against the frozen snapshot shows exactly 2 added lines, 358-359: `if len(declared) != unique: problems.append("duplicate case names")`. |
| `.ufo/waves/round-14/acceptance.json` | `fdf90a5d0886b1f501a67a168a20a4b5a22cfa56fca58aad45eb33757edcc612` | Same as the `HEAD` blob, so the old receipt is unmodified. |

## Case 36: `invalid_tags_digest_not_string` (cases.json lines 548-561)

Literal fixture:
- tags: `{"models":[{"name":"llama3:8b","model":"llama3:8b","digest":12345}]}`
- ps: `{"models":[]}`
- expect: `llama3:8b`
- **expected_exit `2`**, **expected_finding `invalid_input`**

Branch path:
1. Runner (`measure.py`):
   - `measure_case` (211): `case_problems` (139-150) finds no problem. `expect` is a string, `expected_exit` is int `2` and not a bool, `expected_finding` is a string.
   - `write_capture` (189-196) serializes both captures with `json.dumps`, so `12345` stays a JSON integer.
   - The child argv (230-235) is `--tags <path> --ps <path> --expect llama3:8b`. The case name does not appear in it.
2. Classifier `_run` (483):
   - argv parses, and the missing-argument check (499) does not fire.
   - `read_json_file` (137-169) returns dicts for both files: regular file, UTF-8, no duplicate keys, no NaN or Infinity.
3. `classify` (218) calls `validate_capture(tags)` (172) first. Entry 0 is a dict. The field loop (184-186) checks `name`, `model`, `digest`, … in that order. `digest` is present and is an `int`, not a `str`, so `_fail('tags_entry_0_digest_invalid_type')` runs at line 186. The ps capture is never validated (line 221 is not reached).
4. The `InputError` is caught at `_run` 511-512. It is not caught at 506-508, which only handles read errors. The result is finding `invalid_input` with reason `tags_entry_0_digest_invalid_type`, `verdict_exit = FINDING_EXIT['invalid_input'] = 2` (line 97), `return 2` (514), then `sys.exit` (531).
5. The runner's checks then pass: exit, `finding_id`, schema, `verdict_exit` equal to the process exit, and the readiness and scope constants (299-323).

Discrimination: suppose the type gate at 184-186 were removed. `_digest_present` (213-215) would then treat the integer as an absent digest and return `unknown` with exit 2 (238-239). The exit stays the same and only the ID changes. So this case tells Tier-1 type validation apart from Tier-2 digest presence only through the `finding_id` comparison (measure.py 303-307), not through the exit.

## Case 37: `unknown_tags_missing_digest` (cases.json lines 562-575)

Literal fixture:
- tags: `{"models":[{"name":"llama3:8b","model":"llama3:8b"}]}` (no `digest` key)
- ps: `{"models":[]}`
- expect: `llama3:8b`
- **expected_exit `2`**, **expected_finding `unknown`**

Branch path:
1. Staging and argv are the same as case 36.
2. `validate_capture` accepts tags, because line 185 type-checks a field only when it is present (`if field in entry`), and accepts ps as an empty list.
3. `classify`: `tags_matches` is `[entry]` (name equality, 191-192) and `ps_matches` is `[]`.
   - 226: false (one match).
   - 228: false (zero matches).
   - 231: false.
   - 234: `_identity_conflict` is false because name equals model.
   - 236: short-circuits on the empty `ps_matches`.
   - **238**: `_digest_present` gets `None`, which is false, so it returns `unknown` with `['selected_tags_entry_digest_missing_or_empty']` (239).
4. `FINDING_EXIT['unknown'] = 2` (line 96) is returned at 514.

Discrimination:
- If line 238 were removed, or moved after 254, the empty `ps_matches` would give `available_not_loaded` with exit 1 (254-257). Both exit and ID would differ.
- The rejected "missing digest is invalid" proposal (`round-14/advice/Classifier.md` 124-126) would give `invalid_input` with exit 2. The exit is the same and only the ID differs.

## Why the duplicate guard cannot change these two results

Observed:
1. **The guard reads only names.** `corpus_problems` (350-364) reads only `case.get("name")`, stripped (353-355). It never reads `tags`, `ps`, `expect` or `expected_*`. Its only effect is appending a string to `problems` (359), and its only caller is `run()` (374, then 377):
   - non-empty `corpus`: every record becomes an `unmeasured_record` and no child process starts (379-380);
   - empty `corpus`: the unchanged `measure_case` loop runs (381-385).
2. **The committed corpus does not trigger it.** A static jq profile found:
   - 51 records with 51 non-empty string names, 51 of them unique;
   - 0 names with leading or trailing whitespace;
   - all 51 names match `^[a-z0-9_]+$`.

   So `strip()` changes no name, and `len(declared) == 51 == unique`. Line 358 is false. The minimum check (360) is also false (51 ≥ 16). `corpus` is `[]`.
3. **Both names are unique.** Each name occurs exactly once (jq count 1 each), and no other whitespace-free name can strip to either of them.
4. **The name never reaches the child.** The argv (230-235) carries only the capture paths and `expect`, and the case directory is named by index (`f"{index:02d}"`, 220). The classifier has no input derived from the name. Its own pre-existing selftest check (kama-ollama-evidence.py 359-365, raw names) also passes on 51 distinct names.
5. **The guard is all-or-nothing.** It cannot single out case 36 or 37. It can only void every record, and that requires a duplicate, which this corpus does not contain.
6. **Nothing else changed.** The diff touches only 358-359. The classifier and cases are byte-identical to the round-14 receipts.

Historical corroboration comes from the round-14 `acceptance.json`, which was committed in `06cc6db`, after the runner, cases and tool commit `e545ed9`. Both cases passed with observed exit 2 and matching IDs in four runs:
- `final_corpus`: lines 2435-2466, with `unique_case_names` 51 at line 1853;
- `precedence_red`: lines 1572-1603;
- `precedence_only_causal_red`: lines 3795-3826;
- `selftest`: lines 3037-3054.

All four are pre-repair runs. That the repaired runner also passes them is `[INFERENCE]` from the unchanged code path; it was not observed.

## Contrary evidence

- **For cases 36 and 37: none found.** A lane-wide grep for both names hits only `cases.json` and the round-14 receipts. No round-15 advice disputes them.
- **Caveats outside these two cases:**
  - **Residual fail-open.** Names that are not strings, empty, or whitespace-only are still left out of `declared` (354), so the duplicate check never sees them. This does not matter here, since all 51 names are non-empty strings. `MeasurementPlan.md` flags the same gap.
  - **Strip mismatch.** The runner's guard compares stripped names, but the classifier selftest compares raw names (359-365). For a corpus containing both `" a"` and `"a"`, the runner rejects it and the selftest proceeds. This corpus cannot reach that case.
  - **Case 36 is sensitive to the ID only.** Both of its exits are 2, so a scorer that checked only exits would not tell the variants apart.
  - **The runner edit was in flight when I read it.** These findings are tied to SHA `46c5866d…`; any further edit invalidates them.

## Limitations

- I executed no code. The `lsp` device is not mounted in this session (there is no `xd://lsp`), so I traced call sites with literal grep over two module-local files. Each has a single caller:
  - `corpus_problems` ← `run`, line 374;
  - `measure_case` ← `run`, line 385;
  - `classify` ← `_run`, line 510;
  - `validate_capture` ← `classify`, lines 220-221.

  This is not semantic proof.
- The reason tokens (`tags_entry_0_digest_invalid_type` and `selected_tags_entry_digest_missing_or_empty`) come from reading the code. The receipts record only harness-level reasons, so these tokens were never observed.
- That the receipts came from the frozen runner is inferred from commit order: the runner blob has not changed since `e545ed9`, and the receipt was committed in `06cc6db`. The receipts do not record a runner SHA.
- The jq profile used jq's regex semantics. Because every name matches `^[a-z0-9_]+$`, no name contains whitespace of any kind, so the conclusion does not depend on how jq defines `\s`.
- Tooling: nothing installed or updated.

Report: .ufo/waves/round-15/build/advice/CaseAudit18.md
