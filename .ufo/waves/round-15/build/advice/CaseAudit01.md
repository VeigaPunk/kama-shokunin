# CaseAudit01 (KamaR15.CaseAudit01-3) — cases 2/3 and duplicate-guard non-interference

Scope: read-only audit of `tests/ollama-evidence/cases.json` indexes 2 and 3 (zero-based), the classifier branches they hit in `tools/kama-ollama-evidence.py`, and whether the new duplicate-corpus guard in `.ufo/waves/round-14/measure.py` can change those two original results. No code was executed (no classifier, runner, harness, selftest, test, build, lint, or formatter). Statements come from file reads, `jq` queries over the name field, `diff`, `sha256sum` and read-only `git status`/`rev-parse`. Runtime outcomes predicted from the code are marked `[INFERENCE]`.

## Observed corpus context

- `tests/ollama-evidence/cases.json`: a 51-element JSON array (`array` envelope), 768 lines, sha256 `4a4de0b8…158ae4`. Its git blob `677ba8a3…` equals `HEAD:kama-shokunin/tests/ollama-evidence/cases.json` at HEAD `6e348e28…`. `git status --porcelain` is clean for `cases.json` and `tools/kama-ollama-evidence.py` (sha256 `38d1f5d2…fb02`). Only `.ufo/waves/round-14/measure.py` is ` M`. The original corpus and the classifier are therefore unmodified.
- Name census, taken from `jq` over `.name` only: 51 string names, 0 empty after strip, and 0 changed by strip. There are 51 distinct names raw, 51 distinct after strip, and 51 distinct after ASCII lowercasing. Every name matches `^[a-z0-9_]+$`, so Python `str.strip()` leaves each one unchanged. After stripping, index 2's name matches exactly one corpus name (itself), and index 3's name does the same.
- **Index 2**, `cases.json:36-51`:
  - Name: `loaded_empty_string_remote_markers_are_absent` (`:37`).
  - Entries: the tags entry (`:40`) and the ps entry (`:45`) are identical. Each is `{"name": "llama3:8b", "model": "llama3:8b", "digest": "sha256:1111…", "remote_model": "", "remote_host": ""}`.
  - Expectations: `expect: "llama3:8b"` (`:48`), `expected_exit: 0` (`:49`), `expected_finding: "loaded_same_digest"` (`:50`).
- **Index 3**, `cases.json:52-67`:
  - Name: `loaded_exact_gguf_name_no_stripping` (`:53`).
  - Entries: the tags entry (`:56`) and the ps entry (`:61`) are identical. Each is `{"name": "model.gguf", "model": "model.gguf", "digest": "sha256:1111…"}`, with no marker fields.
  - Expectations: `expect: "model.gguf"` (`:64`), `expected_exit: 0` (`:65`), `expected_finding: "loaded_same_digest"` (`:66`).

## Runner path shared by both cases (`measure.py`, current 493 lines, sha256 `46c5866d…5257`)

1. `load_cases` (`:109-128`) returns the array as-is. `corpus_problems` (`:350-364`) returns `[]` (see the guard section). `run()` calls it at `:374`, `if corpus:` at `:377` is false, and the run continues to `elif tool_present:` (`:381`) → `measure_case` (`:385`).
2. In `measure_case` (`:211-347`), `case_problems` (`:139-150`) finds no problems: `expect` is a string, `expected_exit` is an int `0` and not a bool, and `expected_finding` is a string.
3. The case directory is `root / "02"` or `root / "03"` (`:220`). It is named by index; the case name never becomes a path component.
4. `write_capture` (`:189-196`) stages each `tags`/`ps` dict as `json.dumps(value, ensure_ascii=False) + "\n"`.
5. The child argv (`:230-235`) is `sys.executable -I -B <tool> --tags <dir>/tags.json --ps <dir>/ps.json --expect <expect>`. Neither the argv nor the child environment (`:199-208`) contains the case name.
6. Grading (`:296-325`) passes only when all of these hold:
   - exit equals `expected_exit`;
   - `finding_id` equals `expected_finding`;
   - `schema` is `kama-ollama-evidence/v1`;
   - `verdict_exit` equals the process exit;
   - `readiness` is `unknown`;
   - `scope` is `offline-captures-not-runtime`.

## Case 2 — exact branch trace (`tools/kama-ollama-evidence.py`)

1. `_run` (`:483-514`): argv parses, `--selftest` is unset (`:491`), and all three required arguments are present (`:499`). `read_json_file` (`:137-169`) reads two regular UTF-8 files under 4 MiB. They contain valid JSON with no duplicate keys (`_pairs`, `:124-130`) and no NaN or Infinity (`_constant`, `:133-134`).
2. `validate_capture` (`:172-187`): each document is an object with a `models` list, and each entry is an object. At `:184-186`, every present field among `name`/`model`/`digest`/`remote_model`/`remote_host` must be a `str`. Both markers are present and equal `""`, which is a `str`, so validation passes.
3. `_matching` (`:190-192`) uses exact `==`. It finds one tags match and one ps match.
4. `classify` (`:218-264`), in precedence order:
   - `:226`/`:228`: not more than one match → no duplicate-selection `invalid_input`.
   - `:231`: a tags match exists.
   - `:234`/`:236`: `_identity_conflict` (`:195-202`) is false because `name == model == "llama3:8b"`.
   - `:238`/`:240`: both digests are non-empty.
   - `:243`: `_remote_marker(tag)` (`:205-210`) checks `isinstance(value, str) and value != ''`. Both `""` markers fail the `!= ''` test, so it returns `None`.
   - `:246-252`: the ps entry is identical, so its marker check also returns `None`.
   - `:254`: a ps match exists.
   - `:259`: the digests are equal, so `:261` returns `loaded_same_digest` with reasons `tags_ps_digest_equal` and `metadata_correspondence_not_readiness`, plus `CONSTANT_REASONS` (`:87-90`).
5. `classify_payload` (`:267-276`) emits `schema: kama-ollama-evidence/v1`, `finding_id: loaded_same_digest`, `verdict_exit: FINDING_EXIT['loaded_same_digest'] == 0` (`:92`), `readiness: unknown`, and `scope: offline-captures-not-runtime`. `_run` returns `0` (`:514`), and the process exits through `sys.exit(main())` (`:531`) with code 0 `[INFERENCE]`.
6. The runner records `passed: true` (`:325`) `[INFERENCE]`.

What case 2 tests: marker fields that are present but empty count as no marker, as the module docstring states (`:39-43`). A `null` marker would be `invalid_input`/2 at `:185-186`. A non-empty marker would be `remote_inventory`/1 at `:243-252`.

## Case 3 — exact branch trace

1. Reading and validation follow the case 2 path. The marker fields are absent, so the `if field in entry` guard at `:185` skips them.
2. `_matching` (`:190-192`): `"model.gguf" == "model.gguf"`, giving one tags match and one ps match. The classifier code never normalizes names. A grep of the tool for `strip|gguf|lower(|casefold|normaliz|endswith|removesuffix|split(` matches only the docstring disclaimer at `:13-14` ("no GGUF basename, `:latest`, case or digest-prefix normalization").
3. `:234`/`:236`: `name == model`, so there is no conflict. `:238`/`:240`: the digests are present. `:243`/`:247`: `entry.get(field)` is `None`, which is not a `str`, so there is no marker. `:254`: a ps match exists. `:259`: the digests are equal, so `:261` returns `loaded_same_digest` with exit 0 (`:92`).
4. The runner grades this case the same way as case 2 → `passed: true` `[INFERENCE]`.

What case 3 tests: an `--expect` value with a literal `.gguf` suffix is matched exactly as given, against entries with the same exact name.

## New duplicate-corpus guard — exact code and placement

`diff -u .ufo/waves/round-15/frozen/measure-before.py .ufo/waves/round-14/measure.py` shows exactly one hunk:

```python
     unique = len(set(declared))
     problems = []
+    if len(declared) != unique:
+        problems.append("duplicate case names")
     if unique < MINIMUM_UNIQUE_CASES:
```

The frozen snapshot's sha256 is `fda61e00…a1ab`, matching `.ufo/waves/round-15/frozen/manifest.json` (`source_commit 6e348e28…`). The repaired lines are `measure.py:358-359`. The guard runs at `:374`. Before it, `run()` only reads the cases file (`:370`), stats the tool (`:372`) and hashes it (`:373`). No subprocess, temp directory or capture file is created before the `if corpus:` decision at `:377`.

## Why the guard cannot alter cases 2/3

1. **What the guard reads.** `corpus_problems` reads only `case.get("name")` (`:353`), stripped (`:355`). It never reads `tags`, `ps`, `expect`, `expected_exit` or `expected_finding`, and it never calls the classifier.
2. **What the guard can do.** It is a whole-corpus pass/fail gate. If it fires, every record becomes an `unmeasured_record` (`:159-176`: `observed_*` null, `passed: false`) and the run fails before any child starts. It cannot turn `loaded_same_digest`/0 into any other finding or exit, whether passing or failing. If it does not fire, execution follows the pre-repair code path unchanged: the diff touches nothing outside `:358-359`.
3. **Result on the original corpus.** `declared` has 51 entries: no non-string names and no names that are blank after stripping. `unique == 51`, so `len(declared) != unique` is false. Since `51 >= 16`, there is no minimum-size problem either. `problems == []`, and `run()` follows `:381`→`:385`.
4. **Case names cannot affect classification.** Inside `measure_case`, the name is used only as record text (`:216`, `:328`). The directory is index-based (`:220`), and neither the argv (`:230-235`) nor the environment (`:199-208`) contains the name. Even if the guard behaved differently, it has no way to change what the child sees for indexes 2/3.
5. **Two different kinds of stripping.** The guard's `str.strip()` trims whitespace from fixture case names, and has no effect on all 51 `^[a-z0-9_]+$` names. The "no_stripping" in case 3's name refers to model-name matching between `--expect` and the capture entries. The guard never touches either, so it cannot add model-name normalization.
6. **Selftest path untouched.** The classifier's own selftest duplicate check (tool `:359-365`, `duplicate_case_names`) is separate code in a file that is clean against HEAD. The repair did not change it.

## Contrary evidence and boundaries

- **Case 3 is not a negative control on its own.** Normalizing both sides (for example, removing `.gguf` from both `expect` and the entry names) would also produce `loaded_same_digest`/0. This fixture rules out only normalization of entry names alone `[INFERENCE]`. The corpus does contain a separate negative control, `unknown_gguf_suffix_not_stripped` (`cases.json:277`, entries `llama3:8b.gguf` at `:280`/`:285`, `expect: "llama3:8b"` at `:288`). That case is outside my assigned indexes, and I did not audit its expected values.
- **"are_absent" in case 2 describes meaning, not structure.** Both marker fields are present and are type-checked at `:184-186`. `""` passes only because it is a string. If the fixture used `null`, the result would become `invalid_input`/2.
- **Inaccurate staging comment (does not affect cases 2/3).** `measure.py:193` says "Byte-identical staging rule shared with the classifier's selftest". However, the runner uses `json.dumps(value, ensure_ascii=False)`, while the tool's `_fixture_text` (`:310-313`) uses `ensure_ascii=True, allow_nan=False`. For cases 2/3 every string is ASCII and there are no non-finite numbers, so the staged bytes are the same either way `[INFERENCE]`.
- **The runner and selftest guards check names differently.**
  - The runner guard compares stripped names and requires at least 16 distinct names.
  - The tool selftest compares names without stripping (`:359-364`). Its minimum is the entry count (`len(document) < MIN_CASES`, `:356`), not the distinct-name count.
  - The original corpus (51 entries, 51 distinct names, no names with surrounding whitespace) does not exercise either difference.
- **Blank or missing names are not counted.** Such names are left out of `declared` (`:353-355`) and get fallback `case-NN` labels (`:131-136`). Unnamed padding entries are therefore neither counted toward the 16 nor reported as duplicates. Cases 2/3 do not exercise this.
- **No execution.** The exit and finding outcomes above are static predictions. The fixture contents, branch order and the diff were observed directly.

## Limitations

- I audited only indexes 2 and 3. Reads beyond them were limited to the name-only `jq` census and a `gguf` grep, which surfaced one out-of-scope case name. I did not evaluate the sibling-authored guard fixtures under `tests/ollama-corpus-guard/` (12 files present at report time).
- `measure.py` changed while I was auditing it: my first read showed 491 lines, and every later read showed 493 lines. All cited `measure.py` lines refer to the 493-line version, sha256 `46c5866d…5257`, which I re-hashed just before writing this report.
- I ran no verification commands, as assigned. The 51-for-51 measurement and the guard's rejection of duplicate corpora that still have at least 16 distinct names are structural predictions for L1 to verify once.
- I installed or updated no tools: no pacman, uv, npm or cargo actions.

Report: .ufo/waves/round-15/build/advice/CaseAudit01.md
