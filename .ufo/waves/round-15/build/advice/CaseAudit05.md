# CaseAudit05 (KamaR15.CaseAudit05-3) — cases 10/11 and duplicate-guard non-interference

Seat: scout. Read-only except for this file. I read the code statically and executed none of it: no classifier, runner, selftest, tests, builds or linters. The only commands I ran report facts about files: `jq` field and uniqueness queries on `cases.json`, `sha256sum`, and `diff -u` between the frozen runner and the working runner. I installed and updated nothing.

The `lsp` device is not mounted in this session (`xd://lsp` returned "No such tool"). I traced callers with `grep`/`read` as a literal fallback. That is not semantic proof.

## Axes
1. **Literal fidelity:** the committed expected pair for each case.
2. **Classifier branch:** the exact `classify()` line that returns that pair.
3. **Guard non-interference:** the round-15 duplicate guard cannot change either pair for the committed corpus.

## Pinned inputs (observed)
| Artifact | Identity |
|---|---|
| `tests/ollama-evidence/cases.json` | sha256 `4a4de0b85009c42804e43c8ae8833bd6f0673edc71ae5ec8baa1e3201e158ae4`; top-level array of 51 records |
| `tools/kama-ollama-evidence.py` | sha256 `38d1f5d216181bdb7693582027da83eace707f111f42dd32785d386ffe78fb02`. This equals the round-14 `final_corpus` `tool_sha256` (`.ufo/waves/round-14/acceptance.json:1848`) |
| `.ufo/waves/round-14/measure.py` (working copy) | sha256 `46c5866d73a4f875353ff59c6929615149a1f4f4acf69b0b07deeb99d5445257`, 493 lines. `diff -u` against the frozen copy shows only the insertion at `:358-359` |
| `.ufo/waves/round-15/frozen/measure-before.py` | sha256 `fda61e001ca8c2533c99a1759bb4b82f3260a72fafccf72f863f3f4e3684b60d`. This equals `frozen/manifest.json` (source commit `6e348e28`) |

## Case 10 — `available_tag_without_ps_entry` (`cases.json:167-182`)
Literals: `expect` `"llama3:8b"`, `expected_exit` **1**, `expected_finding` **`available_not_loaded`**.
- `tags.models`: `[{name:"llama3:8b", model:"llama3:8b", digest:"sha256:1111…"}]`
- `ps.models`: `[{name:"qwen3:4b", model:"qwen3:4b", digest:"sha256:2222…"}]`

**Runner staging** (`measure.py`):
- `case_problems` passes (`:139-150`): `expect` is a str, `expected_exit` is an int and not a bool, `expected_finding` is a str.
- Both captures are non-null, so both are written with `json.dumps(..., ensure_ascii=False)+"\n"` (`:189-196`, `:226-229`).
- The child argv is `[sys.executable, -I, -B, tool, --tags <dir>/tags.json, --ps <dir>/ps.json, --expect "llama3:8b"]` (`:230-235`).
- The case directory is `root/"10"`, taken from the index (`:220`).

**Classifier path** (`tools/kama-ollama-evidence.py`):
1. `_run` `:499`: all three arguments are non-empty. `read_json_file` reads both files (`:504-505`). Each is a regular file, at most 4 MiB, valid UTF-8, has no duplicate keys (`_pairs` `:124-130`) and no NaN/Infinity (`_constant` `:133-134`).
2. `classify` `:220-221`, `validate_capture`: each capture is a dict, `models` is present and is a list, and every entry is a dict whose name/model/digest are strings. Neither entry has a marker field (`:172-187`). Both captures pass.
3. `:223-224`: `tags_matches` holds the one llama3 entry. `ps_matches` is `[]`, because `qwen3:4b` differs from `expect` in both name and model (`_matching` `:190-192`).
4. The intermediate checks all fall through:
   - `:226` and `:228` duplicate checks: false.
   - `:231` no-tags check: false.
   - `:234` `_identity_conflict(tag)`: name == model, so false.
   - `:236` ps conflict: skipped because there is no ps match.
   - `:238` tag digest is present: continue.
   - `:240`: skipped.
   - `:243-245` tag remote marker: none.
   - `:246`: skipped.
5. **`:254-257`: `not ps_matches` returns `('available_not_loaded', ['tags_digest_local_no_matching_ps_entry'])`.**
6. `:513-514`: `classify_payload` (`:267-276`) emits:
   - schema `kama-ollama-evidence/v1`
   - `verdict_exit` = `FINDING_EXIT[...]` = 1
   - readiness `unknown`
   - scope `offline-captures-not-runtime`

   The process exits with `FINDING_EXIT['available_not_loaded']` = **1** (`:93`). All five comparisons in `measure_case` (`:299-323`) are therefore satisfiable.

**What this case pins:** the unselected ps entry has a different digest, and that digest is never compared. The digest comparison at `:259` is reachable only when a ps entry is selected. A digest-join implementation, or one that treats "any ps entry" as loaded, would return `identity_conflict` or `loaded_same_digest` here.

## Case 11 — `available_empty_ps_models` (`cases.json:183-196`)
Literals: `expect` `"llama3:8b"`, `expected_exit` **1**, `expected_finding` **`available_not_loaded`**.
- `tags` is identical to case 10. `ps` is `{"models": []}`, written as `{"models": []}\n`.

The path matches case 10 with one difference. `validate_capture(ps)` returns `[]`: the entry loop at `:181` has nothing to check, and an empty list is a valid envelope, so neither `ps_models_missing` nor `ps_models_not_array` fires. `ps_matches` is `[]`, so `:231-246` fall through exactly as in case 10 and **`:254-257` returns exit 1, `available_not_loaded`**.

**What this case pins:** an explicitly empty ps array is valid input, not `invalid_input`. It means only "absent from the supplied ps capture".

## Why the new duplicate guard cannot alter these results
How the guard works (working `measure.py:350-364`):
- `declared` collects `name.strip()` for every dict case whose name is a non-blank str (`:351-355`).
- `unique = len(set(declared))` (`:356`).
- **New** `:358-359`: if `len(declared) != unique`, add "duplicate case names".
- Kept `:360-363`: if `unique < 16`, add the minimum-count problem.

1. **The committed corpus produces no problem.**
   - `jq` over `cases.json` gives 51 records and 51 string names. All match `^[a-z0-9_]+$`, so `strip()` changes nothing. There are 51 unique exact names.
   - `len(declared) = 51 = unique`, so `:358` is false. `51 ≥ 16`, so `:360` is false. The result is `corpus == []`.
   - Each audited name occurs exactly once: `available_tag_without_ps_entry` ×1 and `available_empty_ps_models` ×1.
2. **Control flow is the same as in the frozen runner.**
   - `run()` calls the guard at `:374`, before any temp directory or child process exists.
   - With `corpus == []`, `:377 if corpus:` is false. `:381 elif tool_present:` then calls `measure_case` for every index (`:384-385`).
   - Indexes 10 and 11 get the same staging, argv, env, timeout and comparisons as before.
   - `diff -u` from frozen to working shows only the two inserted lines. `load_cases`, `case_problems`, `write_capture`, `child_environment` and `measure_case` are unchanged.
3. **The case name is not an input to the classifier.**
   - The argv (`:230-235`) carries only the tool, two capture paths and `expect`. The case directory comes from the index (`:220`).
   - `classify(expected, tags_document, ps_document)` (`:218`) has no name parameter.
   - The guard reads only `name` (`:353`) into a local list. It never modifies `cases`, `tags`, `ps`, `expect` or `expected_*`.
4. **The guard can only stop the whole measurement, never change one result.**
   - If it fires, every case becomes an `unmeasured_record` (`:159-176`: `observed_exit` None, `observed_finding` None, `passed` False), and the run exits 1.
   - It cannot turn a measured `(1, available_not_loaded)` into any other result.
   - For this corpus it does not fire.
5. **The history is consistent with this.**
   - The round-14 `final_corpus` receipt (`acceptance.json:1846-1857`) used the same tool sha and the same cases sha, recorded `unique_case_names` 51, and passed 51/51.
   - It records both cases as observed `1`/`available_not_loaded`/`passed: true` (`:2019-2050`).
   - The current classifier and corpus bytes hash to the receipt's values.

## Contrary evidence checked
No evidence I found contradicts the conclusion.
- **The file changed while I was reading it.** My first read of `measure.py:350-362` showed only the minimum check, identical to the frozen copy. The GuardRepair edit landed during the audit (mtime 2026-10-20 05:09:13; 491 → 493 lines). The argument holds for both versions. Re-anchor the line numbers if the body changes again.
- **No near-collisions.** Lower-casing the names (`ascii_downcase`) still leaves 51 unique values, so even a case-folding guard would not fire. [INFERENCE] NFKC normalization leaves `[a-z0-9_]` unchanged, so a Unicode-normalizing guard would not fire either.
- **The guard has a blind spot that these cases do not touch.** Unnamed or blank names are left out of `declared` (`:354`). `cases.json` has none: all 51 names are non-blank strings.
- **Display name and guard identity differ, with no effect here.** `case_name()` (`:131-136`) reports the raw name, while the guard counts the stripped name. These names contain no whitespace, so the two are identical.
- **These cases do not show the round-14 precedence repair.** Both were also observed as `1`/`available_not_loaded`/passed in `precedence_red` (`acceptance.json:1156-1187`) and `precedence_only_causal_red` (`:3379-3410`). They stay stable across classifier builds and add no red→green credit.
- **`capability_absent` is not a classifier verdict.** Its records (`acceptance.json:216-250`) show observed_exit null and `unsupported`. That comes from the runner's tool-absent branch (`measure.py:386-393`).
- **Adjacent observation outside the round-15 target.** The classifier's own `--selftest` (`tools/kama-ollama-evidence.py:356-365`) already rejects duplicate names, but differently from the runner:
  - It compares exact names. It excludes only `''` and does not strip.
  - Its minimum counts records (`len(document) < 16`), not unique names.

  A variant such as `" n04 "` would be rejected by the runner's guard but not by the selftest. Round 15 does not change the selftest, and its round-14 records for these two cases passed (`acceptance.json:2803-2820`).

## Limitations
- I read the code and did not run it. The classifier branch walk and the runner flow were traced by hand, so the observed exits are `[INFERENCE]` from static code. They are backed by the round-14 receipt hashes, which match.
- No `lsp` server was available. `grep` found exactly one caller of `corpus_problems` (`measure.py:374`). That is a text search, not semantic proof.
- I audited only indexes 10 and 11, plus the corpus-wide name counts. Indexes 0-9 and 12-50 belong to sibling seats.
- I did not read the new guard fixtures or harness (`tests/ollama-corpus-guard/`); they are outside this question.
- I installed and updated no tools and took no pacman/uv/npm actions.

Report: .ufo/waves/round-15/build/advice/CaseAudit05.md
