# CaseAudit06 — original cases 12/13 vs the landed corpus duplicate guard

Seat `KamaR15.CaseAudit06-3`, scout, read-only. Reviewed 2026-10-20 (~08:10Z). No code was executed: no classifier, runner, selftest, guard harness, test, build, lint or formatter. Fact gathering used only file reads, JSON queries, `sha256sum`, `diff`, and `git show <commit>:<path> | sha256sum`. No tools were installed or updated.

Axes: (1) the literal expected ID/exit matches the classifier branch; (2) the guard does not interfere (it reads names only, runs before any child, and acts on the whole corpus); (3) evidence provenance (byte identity of what was observed versus what exists now).

## Files and fingerprints (sha256 at read time)

| path (under `kama-shokunin/`) | sha256 | note |
|---|---|---|
| `tests/ollama-evidence/cases.json` | `4a4de0b85009c42804e43c8ae8833bd6f0673edc71ae5ec8baa1e3201e158ae4` | 51 entries; indexes 12–13 read (lines 197–229) |
| `tools/kama-ollama-evidence.py` | `38d1f5d216181bdb7693582027da83eace707f111f42dd32785d386ffe78fb02` | classifier (child) |
| `.ufo/waves/round-14/measure.py` | `46c5866d73a4f875353ff59c6929615149a1f4f4acf69b0b07deeb99d5445257` | 493 lines, mtime 05:09:13 -0300; guard landed |
| `.ufo/waves/round-15/frozen/measure-before.py` | `fda61e001ca8c2533c99a1759bb4b82f3260a72fafccf72f863f3f4e3684b60d` | matches `frozen/manifest.json` |

## Case literals (observed)

| idx | name | cases.json lines | `expect` | `expected_exit` | `expected_finding` |
|---|---|---|---|---|---|
| 12 | `available_shared_digest_alias_copy_inactive` | 197–213 | `gpt-x:latest` | 1 | `available_not_loaded` |
| 13 | `unknown_ps_alias_without_tags_match` | 214–229 | `llama3:8b` | 2 | `unknown` |

- Case 12 captures: tags = [`llama3.2:latest`, `gpt-x:latest`], both digest `sha256:111…`. ps = [`llama3.2:latest`, digest `sha256:111…`].
- Case 13 captures: tags = [`qwen3:4b`, digest `sha256:222…`]. ps = [name `llama3:8b`, model `llama3:8b-ctx8192`, digest `sha256:111…`].
- The pairs agree with the classifier's exit table, `FINDING_EXIT` (`tools/kama-ollama-evidence.py:91-98`): `available_not_loaded`→1 and `unknown`→2. The selftest's `_valid_case` enforces this mapping (`:339-342`). `measure.py` does not enforce it, but it grades exit and finding ID independently.

## Runner staging (`.ufo/waves/round-14/measure.py`, same for both cases)

- `case_problems` (`:139-150`) passes: `expect` is a str, `expected_exit` is an int, `expected_finding` is a str.
- `case_dir = root / f"{index:02d}"` (`:220`) is named by index only, as `12` and `13`. `tags` and `ps` are non-null dicts, so `write_capture` writes `json.dumps(value, ensure_ascii=False) + "\n"` (`:189-196`, `:226-229`).
- argv (`:230-235`): `python -I -B <tool> --tags <dir>/tags.json --ps <dir>/ps.json --expect <expect>`. The env (`:199-208`) holds PATH/HOME/TMPDIR/LANG/LC_ALL only. **The case `name` never reaches the child.** It is used only as the record label (`:216`, `:328`).
- Grading (`:296-325`) checks, each independently: process exit == `expected_exit`, `finding_id` == `expected_finding`, schema == `kama-ollama-evidence/v1`, `verdict_exit` == process exit, readiness `unknown`, scope `offline-captures-not-runtime`.

## Classifier path, case 12 → `available_not_loaded` / exit 1

1. `_run` (`:483-514`): argv parses, `--selftest` is not set, and `--tags/--ps/--expect` are all non-empty (`:499`).
2. `read_json_file` (`:137-169`) for both files: regular file, under 4 MiB, UTF-8, valid JSON. `_pairs` (`:124-130`) finds no repeated key within any object. The two tags entries share a digest *value*, which is not a key collision.
3. `classify` (`:218-264`):
   - `validate_capture` (`:172-187`): both documents are objects with a `models` list. Every entry is an object, `name`, `model` and `digest` are str, and there are no marker fields.
   - `_matching` (`:190-192`) uses exact `name == expect or model == expect`. Tags returns only the `gpt-x:latest` entry. `llama3.2:latest` is not selected despite the equal digest. ps returns `[]`.
   - `:226` and `:228` (duplicate selection, more than one match): counts are 1 and 0, not taken.
   - `:231` (no tags match): false.
   - `:234` (tags name/model conflict): false, because name == model. `:236` and `:240` are skipped because there is no ps match. `:238` (tags digest present): passes. `:243` (tags remote marker): none. `:246` is skipped.
   - **`:254` `if not ps_matches` → `('available_not_loaded', ['tags_digest_local_no_matching_ps_entry'])` (`:255-257`).** The digest comparison at `:259` is never reached.
4. `classify_payload` (`:267-276`) sets `verdict_exit = FINDING_EXIT['available_not_loaded'] = 1`, readiness `unknown`, and scope `offline-captures-not-runtime`. `_run` returns 1 (`:514`), and that is the process exit (`:531`).
5. Why this is correct: selection uses the exact name or alias only (docstring `:12-14`). The tags/ps digest join is "an inference, not a documented mapping" (`:51-52`). A loaded *other* alias with the same digest therefore does not make `gpt-x:latest` loaded. The precedence step "no selected ps entry (available)" (`:37`) comes before the digest comparison.

## Classifier path, case 13 → `unknown` / exit 2

1. Reading and validation pass as in case 12. `qwen3:4b`, `llama3:8b` and `llama3:8b-ctx8192` are all str.
2. `_matching("llama3:8b")`: tags returns `[]`. ps returns `[entry]`, matched on `name == "llama3:8b"`.
3. `:226` and `:228` see counts of 0 and 1, not taken.
4. **`:231` `if not tags_matches` → `('unknown', ['no_tags_entry_matches_expected_name'])` (`:232`).** `classify_payload` sets `verdict_exit` 2, and the process exits 2.
5. Unreached branch: at `:236`, `_identity_conflict(ps_matches[0])` would be True (name `llama3:8b` ≠ model `llama3:8b-ctx8192`, both non-empty) and would return `identity_conflict`/1. The fixed order puts no-tags first: docstring `:33-35` says "no tags match (unknown, even when a ps entry matches or conflicts)", and the parser epilog `:459-461` matches it.

## Why the landed duplicate guard cannot alter these two results

1. **Exact delta.** `diff -u .ufo/waves/round-15/frozen/measure-before.py .ufo/waves/round-14/measure.py` shows one hunk. It inserts `:358-359` (`if len(declared) != unique: problems.append("duplicate case names")`) inside `corpus_problems`. Nothing else changed: `measure_case`, staging, argv, grading, schema, `LIMITS` and the minimum check (`:360-363`) are all untouched.
2. **Input domain.** `corpus_problems` (`:350-364`) reads only `case["name"]`, canonicalized with `strip()` (`:353-355`). It never reads `tags`, `ps`, `expect`, `expected_exit` or `expected_finding`, and it never rewrites the case list.
3. **The committed corpus passes it.** A JSON query over `cases.json` gives total 51 and 51 unique raw names. No name fails `^[a-z0-9_]+$`, so `strip()` changes nothing and there are no blank or non-string names. Therefore `len(declared) == unique == 51`: `:358` is false, `:360` is false (51 ≥ 16), and `corpus == []`.
4. **The assigned names are singletons.** `available_shared_digest_alias_copy_inactive` occurs only at index 12. `unknown_ps_alias_without_tags_match` occurs only at index 13.
5. **Unchanged control flow.** `run` computes `corpus` at `:374`, before any staging or child process. With `corpus` empty, `elif tool_present:` (`:381`) calls `measure_case` for each index (`:385`), as before. The only `subprocess.run` is at `:240`, inside `measure_case`.
6. **There is no channel from name to verdict.** The name is absent from argv, env and the directory name (point 5 above, and the staging section). The guard can therefore only gate the whole run. If it fired, it would switch every record to `unmeasured_record` (`:377-380`, `:159-176`: `observed_*` null, `passed: false`, run exit 1). It can never re-grade case 12 or 13 to another finding ID or exit.
7. **The classifier is untouched.** The current tool sha `38d1f5d2…` equals the round-14 observed run's `tool_sha256` and equals `git show e545ed99:./tools/kama-ollama-evidence.py | sha256sum`.

## Prior observed evidence (`.ufo/waves/round-14/acceptance.json`)

The file records `recorded_at 2026-10-20T06:38:39Z` and `measured_commit e545ed99…`.

- `records.2` (`final_corpus`): `measure.py` with the default tool. `tool_sha256 38d1f5d2…` equals the current tool and `cases_sha256 4a4de0b8…` equals the current corpus. Overall: 51/51 passed, unique 51, exit 0.
  - Case 12: observed 1 / `available_not_loaded`, `verdict_exit` 1, passed, `reasons: []`.
  - Case 13: observed 2 / `unknown`, `verdict_exit` 2, passed, `reasons: []`.
- The runner bytes at the measured commit (`git show e545ed99:./.ufo/waves/round-14/measure.py | sha256sum`) are `fda61e00…`, identical to the frozen pre-repair snapshot. **The only code difference between that observed pass and today is the two-line guard.** It does not fire on this corpus (points 3–4 above).
- `records.3` (`selftest`): both cases passed with the same IDs and exits. The `observed_verdict_exit` is null there because the selftest `_record` (`:316-326`) has no verdict field. The selftest still checks `verdict_exit_mismatch` internally (`:431-432`).
- `records.1` (`precedence_red`) and `causal_red` (`precedence_only_causal_red`): both cases still passed, with 49/51 overall. They are not the controls that discriminate those mutations.
- `records.0` (`capability_absent`): both cases are `unsupported` with exit null, as expected when the tool is absent.

## Contrary evidence and caveats

- **I found no evidence that changes either result.**
- Case 12 reader trap: the equal digest between the loaded `llama3.2:latest` and the requested `gpt-x:latest` suggests `loaded_same_digest`. Name-only selection (`:190-192`) contradicts that. The `_active` twin is index 5, `loaded_shared_digest_alias_copy_active` (cases.json line 86); its ps holds `gpt-x:latest`. I did not read its literals (out of scope).
- Case 13 reader trap: the ps entry is itself a name/model alias conflict, which suggests `identity_conflict`/1. Precedence gives `unknown`/2. Round-14 advice records L1 resolving this deliberately:
  - `advice/Fixtures.md:28,34`
  - `advice/ReviewFixtures.md:228-229`
  - The case was renamed from `identity_conflict_ps_alias_without_tags_match` (`advice/ReplayKnowledge.md:77-78`).
- Exit codes alone are ambiguous. Exit 1 covers `available_not_loaded`, `remote_inventory` and `identity_conflict`; exit 2 covers `unknown` and `invalid_input`. The finding ID is what discriminates, and `measure.py` grades it independently (`:304-307`).
- "Duplicate" means three different things here:
  - corpus case-name duplicates: the runner guard;
  - duplicate selected entries: classifier `:226-229`, giving `invalid_input`;
  - duplicate JSON object keys: `_pairs`, giving `*_input_duplicate_json_key`.

  Case 12's shared digest triggers none of them. Case 13 has one ps selection and zero tags selections, which triggers none of them either.
- The code canonicalizes names in two ways:
  - the runner guard strips names (`:354-355`);
  - the selftest compares raw names (`:359-365`);
  - the record label is the raw name (`case_name`, `:131-136`).

  For these two names raw == stripped, so the two conventions do not diverge here.
- Guard limitation, not exercised here: non-string or blank names are excluded from `declared`, so they cannot trigger the duplicate problem. The committed corpus has none.
- Concurrency note: my first read of `measure.py` (491 lines, pre-repair) happened before GuardRepair landed at 05:09:13 -0300. Every runner line number above refers to the re-read landed file (493 lines, sha `46c5866d…`).

## Limitations

- These are static traces. The post-repair outcome for cases 12/13 is an [INFERENCE] from two facts: the repair is a zero-effect diff on this corpus, and the round-14 observation was made on identical classifier and corpus bytes. Neither case was re-executed in round 15.
- From `cases.json` I read only the index 12/13 payloads, plus corpus-wide name counts. The guard fixtures in `tests/ollama-corpus-guard/*.json` (12 files present) were not read; they are out of scope.
- The verification L1 should run once, after integration: `.ufo/waves/round-14/measure.py` against the committed corpus. Expect exit 0, 51/51 passed, `unique_case_names` 51, no `error`. Cases 12 and 13 should match the literals above.

Report: .ufo/waves/round-15/build/advice/CaseAudit06.md
