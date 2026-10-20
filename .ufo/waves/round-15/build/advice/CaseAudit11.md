# CaseAudit11 — cases 22/23 literals vs the new corpus duplicate guard

Seat: KamaR15.CaseAudit11-3 (leaf scout). Read-only: no repo code executed, no tests run.
Labels: **[observed]** = direct file or receipt read; **[inference]** = static code-path reasoning.

## Scope and files [observed]

| Role | Absolute path | sha256 at read time |
|---|---|---|
| Fixtures (indexes 22 = lines 356–371, 23 = lines 372–387) | `/home/vgpnk/Projects/shokunin/kama-shokunin/tests/ollama-evidence/cases.json` | `4a4de0b85009c42804e43c8ae8833bd6f0673edc71ae5ec8baa1e3201e158ae4` |
| Classifier (runner `DEFAULT_TOOL`, `measure.py:55–57`) | `/home/vgpnk/Projects/shokunin/kama-shokunin/tools/kama-ollama-evidence.py` | `38d1f5d216181bdb7693582027da83eace707f111f42dd32785d386ffe78fb02` |
| Runner, post-repair (read tag 6643) | `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-14/measure.py` | `46c5866d73a4f875353ff59c6929615149a1f4f4acf69b0b07deeb99d5445257` |
| Pre-repair snapshot (matches `frozen/manifest.json`) | `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-15/frozen/measure-before.py` | `fda61e001ca8c2533c99a1759bb4b82f3260a72fafccf72f863f3f4e3684b60d` |
| Round-14 receipt (immutable, read only) | `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-14/acceptance.json` | — |

`git log` shows one commit touching the runner, classifier and cases: `e545ed9` (round-14), which is
also the receipt's `measured_commit`.

## Assigned fixtures (exact literals) [observed]

**Index 22 — `identity_conflict_ps_name_model_alias_ambiguity`**

```
tags: {"models":[{"name":"llama3:8b","model":"llama3:8b",        "digest":"sha256:<64×'1'>"}]}
ps:   {"models":[{"name":"llama3:8b","model":"llama3:8b-ctx8192","digest":"sha256:<64×'1'>"}]}
expect "llama3:8b" · expected_exit 1 · expected_finding "identity_conflict"
```

**Index 23 — `identity_conflict_digest_prefix_not_stripped`**

```
tags: {"models":[{"name":"llama3:8b","model":"llama3:8b","digest":"sha256:<64×'1'>"}]}
ps:   {"models":[{"name":"llama3:8b","model":"llama3:8b","digest":"<64×'1'>"}]}
expect "llama3:8b" · expected_exit 1 · expected_finding "identity_conflict"
```

Digest facts from jq: case 22 tags and ps digests are byte-equal (71 chars each). Case 23 has a
71-char tags digest and a 64-char ps digest, and the two are equal once `sha256:` is removed. Both
cases have byte-identical `tags` captures and differ only in `ps`. The raw text has no duplicate
JSON keys, so `measure.py:load_cases` (plain `json.loads`, `:109–128`) stages them faithfully.

## Classifier branch trace (`tools/kama-ollama-evidence.py`, tag D8BD)

The first steps are the same for both cases [observed code]:

1. `_run` `:499` — `--tags`, `--ps` and `--expect llama3:8b` are all non-empty.
2. `read_json_file` `:137–169` — both files are regular UTF-8 JSON with no duplicate keys or NaN, so there is no `InputError`.
3. `validate_capture` `:172–187` — both inputs are objects with a `models` list of objects, and `name`/`model`/`digest` are strings. No remote markers are present.
4. `_matching` `:190–192` selects on exact `name == expected or model == expected`. tags gives 1 match. ps gives 1 match, selected by `name`.
5. The duplicate-selection checks `:226–229` are not taken. The no-tags-match check `:231–232` is not taken. `_identity_conflict(tag)` `:234` is false because the tags name equals the model.

**Case 22 → branch `:236–237`.** The selected ps entry has a non-empty `name` (`"llama3:8b"`) and a
non-empty, different `model` (`"llama3:8b-ctx8192"`), so `_identity_conflict` (`:195–202`) returns true.
The classifier returns `'identity_conflict', ['selected_ps_entry_name_model_conflict']`.
`classify_payload` `:267–276` emits `verdict_exit = FINDING_EXIT['identity_conflict'] = 1` (`:91–98`), and
`_run` `:514` exits 1. Lines `:238–264` are unreachable. The "alias ambiguity" is that the OR in
`_matching` selects the ps entry by `name` even though its `model` names a different alias.

**Case 23 → branch `:259–260`.** The ps entry has name == model, so `:236` is false. Both digests are
non-empty, so `:238` and `:240` are not taken. No remote markers fire (`:243–252`), and `ps_matches` is
non-empty (`:254`). The raw string comparison `tag['digest'] != ps_entry['digest']`
(`"sha256:1…1"` vs `"1…1"`) is true, so the classifier returns `'identity_conflict', ['tags_ps_digest_mismatch']` and exits 1.
The module docstring `:12–14` states that there is no digest-prefix normalization. Docstring
`:22–23` lists both identity_conflict clauses: case 22 hits the name/model clause on the ps side, and
case 23 hits the tags-vs-ps digest clause.

**Literal consistency.** For identity_conflict, `FINDING_EXIT` gives 1. `_valid_case` `:334–343` requires
`FINDING_EXIT[expected_finding] == expected_exit`. `measure.py` grades exit `:299`, `finding_id` `:304`,
schema `:308`, verdict_exit `:312`, readiness `:316` and scope `:320`.

**Counterfactuals that pin the branches [inference].**
- Case 22: deleting `:236–237` lets the equal digests reach `loaded_same_digest` with exit 0, which fails the exit grade.
- Case 22: matching ps on `model` only gives `ps_matches=[]`, which leads to `available_not_loaded` (exit **1**). Only the `finding_id` grade catches that.
- Case 23: adding `sha256:` stripping makes the digests equal, which gives `loaded_same_digest` with exit 0 and fails the exit grade.

## Prior observation in the round-14 receipt [observed]

| `acceptance.json` run | Tool | Cases 22 and 23 |
|---|---|---|
| `records[0]` capability_absent | absent `frozen/before/...` | `unsupported`, exit null (tool absent) |
| `records[1]` precedence_red | `frozen/precedence-before.py` sha `6e1c4ba5…` | both pass. The only failures were `remote_missing_digest` and `tags_none_ps_duplicates` |
| `records[2]` final_corpus | tool sha `38d1f5d2…`, cases sha `4a4de0b8…` | both pass: observed_exit 1, `identity_conflict`, schema/verdict_exit 1/readiness/scope all correct. Run totals: `unique_case_names: 51`, 51/51 passed |
| `records[3]` selftest | classifier `--selftest` | both pass: exit 1, `identity_conflict` |

The final_corpus tool and cases hashes are **byte-equal to the current files**.

## Why the new duplicate guard cannot alter cases 22/23

**Repair delta [observed].** `diff -u frozen/measure-before.py round-14/measure.py` shows exactly two
inserted lines and nothing else:

```python
if len(declared) != unique:            # measure.py:358
    problems.append("duplicate case names")   # :359
```

`measure_case`, `case_name`, `write_capture`, the child argv, the grading, `run` branching, `LIMITS` and the docstring
are all unchanged.

1. **The guard is corpus-level, runs before any child, and is all-or-nothing.** `corpus_problems` has a single caller, `run` `:374`. Its result is used only at
   `:377`. A non-empty result turns every record into `unmeasured_record` (`:379–380`). An empty result
   leaves the per-case path (`:381–385`) unchanged. The guard has no path that singles out case 22 or 23.
2. **The committed corpus produces no problems.** All 51 entries are objects with string names, and 51
   are exactly unique. Every name matches `^[a-z0-9_]+$`, so `strip()` changes nothing. That gives
   `len(declared)=51 == unique=51`, so the duplicate check does not fire. 51 ≥ 16, so the minimum check
   does not fire either. Each of the names at 22 and 23 occurs exactly once. Case-folded uniqueness is
   also 51, so even a case-insensitive guard would not collide (the spec stays case-sensitive).
3. **The guard reads only `name`.** Cases 22 and 23 share `expect`, a byte-identical `tags` capture,
   `expected_exit` 1 and `expected_finding` (`identity_conflict` covers indexes 19–23). None of these fields enter
   `declared`, so sharing them cannot reduce `unique`.
4. **Names never reach the child.** The argv at `:230–235` passes only `--tags/--ps/--expect`. The case
   directory is named `f"{index:02d}"` (`:220`). The classifier opens `cases.json` only under `--selftest`.
5. **Result [inference, not re-executed].** The classifier and fixture bytes are unchanged since the passing
   final_corpus receipt, and the guard yields `[]` for this corpus. So the post-repair records for cases 22 and 23
   should repeat exit 1 / `identity_conflict` / passed.

## Contrary evidence and risks

- **Nothing contradicts the expected IDs/exits for cases 22/23.** Three tool-present observations pass (precedence_red, final_corpus, selftest).
- **A sibling report is incomplete.** `.ufo/waves/round-15/build/advice/CaseAudit08.md:124–128` says
  acceptance.json records all 51 cases as `unsupported` with passed 0. That is true only of `records[0]` (capability_absent).
  `records[2]` (final_corpus) shows 51/51 passed with the current tool and cases hashes.
- **Exit 1 alone does not identify the finding.** `identity_conflict`, `available_not_loaded` and
  `remote_inventory` all exit 1. The `finding_id` grade (`measure.py:304`, selftest `:439–440`) carries the weight.
- **The specific branch is not graded.** For passing cases, neither the runner nor the selftest keeps the
  child's `reasons`. The runner keeps `stdout_tail` only on failure (`:343–346`), and the selftest keeps only
  mismatch reasons. So `:236–237` for case 22 and `:259–260` for case 23 come from the static trace; the
  receipts confirm only finding and exit. The counterfactuals above show that adjacent regressions would
  still change the finding or the exit.
- **The guard must stay keyed on names.** Cases 22 and 23 have identical `tags` and the same expect,
  exit and finding. Deduplicating on content or finding would wrongly collapse distinct cases.
- **Runner and selftest canonicalize differently.** The runner strips names. The classifier selftest
  `:359–365` compares raw names. The committed names are slugs, so both agree today.
- **The guard fails the whole run by design.** If a duplicate name were injected, cases 22 and 23 would not be measured at all
  (observed_exit/finding `None`, exit 1). That is the intended fail-closed behavior, not a classification change.
- **The guard fixtures were not observed running.** `tests/ollama-corpus-guard/check.py` was absent at read time. The 12 fixture JSONs
  do not reference the names of cases 22/23 or `llama3:8b-ctx8192`.

## Limitations

- No repo code was executed (runner, classifier, selftest, harness). Read-only commands used: `sha256sum`, `diff`,
  `git log`. One initial `python3 -c` JSON length count (list, 51) was also run; it read data only and imported no repo code.
- Corpus-wide facts are jq aggregates over `name` only (counts, uniqueness, slug test). Other fixture bodies were not read.
- No `lsp` device is mounted (`xd://lsp` → "No such tool"). Callers were found from full reads of the
  single-file call chains plus a literal grep fallback. That grep found one call site each:
  `corpus_problems` `:374`, `measure_case` `:385`, `classify` `:510`. This is not semantic LSP proof.
- Line numbers refer to measure.py tag 6643 (post-repair) and classifier tag D8BD.
- No tools installed or upgraded.

Report: .ufo/waves/round-15/build/advice/CaseAudit11.md
