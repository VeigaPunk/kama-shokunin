# CaseAudit12: cases.json indexes 24 and 25 vs the duplicate-corpus guard

Seat: `KamaR15.CaseAudit12-3` (scout, read-only). Static reads only. I did not run the
classifier, the runner, the selftest, or any test. The only shell commands were `sha256sum`,
`diff`, and `git diff --stat`, used to compare files and record where they came from.

Axes: (1) literal expectation fidelity, (2) exact classifier branch, (3) whether the guard
can interfere, (4) whether the round-14 receipt still matches the current files.

Files read (all relative to the kama-shokunin root):
- `tests/ollama-evidence/cases.json`: indexes 24 and 25 (lines 388–419), plus corpus-wide
  name counts computed with jq.
- `tools/kama-ollama-evidence.py`: the whole classify path.
- `.ufo/waves/round-14/measure.py`: read twice, because the repair landed during this
  audit. The first read (`#B6F1`, 491 lines) had the minimum-only guard. The later read
  (`#6643`, 493 lines) has the duplicate guard.
- `.ufo/waves/round-15/frozen/{measure-before.py,manifest.json}`.
- `.ufo/waves/round-14/acceptance.json`: only the records for these two cases.
- `.ufo/waves/round-14/frozen/precedence-before.py`: diff against the classifier only.

## Case 24: `remote_inventory_tags_loaded_pair` (cases.json:388–403)

Fixture:
- tags: `{models:[{name:"llama3:8b", model:"llama3:8b", digest:"sha256:1111…1111",
  remote_model:"llama3-cloud", remote_host:"https://remote.invalid"}]}`
- ps: `{models:[{name:"llama3:8b", model:"llama3:8b", digest:"sha256:1111…1111"}]}`
- `expect:"llama3:8b"`, `expected_exit:1`, `expected_finding:"remote_inventory"`

Classifier path (`tools/kama-ollama-evidence.py`):
1. **CLI checks pass.** `_run` (483–514) parses the arguments. `--selftest` is not set, and
   `--tags`, `--ps` and `--expect` are all nonempty (499).
2. **Both files load.** `read_json_file` (137–169) finds a regular file well under the
   4 MiB limit, valid UTF-8, no duplicate keys (`_pairs`) and no NaN/Infinity (`_constant`).
3. **Structure is valid.** `validate_capture` (172–187) sees objects with a `models` array.
   Every name, model, digest and remote-marker field present is a `str`.
4. **Exactly one match on each side.** `_matching` (190–192) returns one tags entry and one
   ps entry. The duplicate branches (226–229) and the no-tags-match branch (231–232) do not
   fire.
5. **No identity conflict.** On both sides `name == model`, so 234–237 do not fire.
6. **Both digests are present and nonempty**, so 238–241 do not fire.
7. **The tags remote-marker branch decides the result (243–245).** `MARKER_FIELDS` is
   `('remote_model','remote_host')` (line 100). The tags entry has a nonempty
   `remote_model` (`"llama3-cloud"`), so `_remote_marker` (205–210) returns
   `'remote_model'`. The result is `remote_inventory`, with reason
   `selected_tags_entry_remote_model_present`.
8. **Exit and payload.** `FINDING_EXIT['remote_inventory'] = 1` (line 94). `classify_payload`
   (267–276) sets `verdict_exit:1`, `readiness:"unknown"` and
   `scope:"offline-captures-not-runtime"`. The process exits 1 (514 → 531).

Why this case matters: the two digests are equal. If the tags-marker check were missing, or
ran after the digest comparison, the same fixture would reach 261 and return
`loaded_same_digest` with exit 0. The exit code and the finding ID would both change, so
this case catches the error either way.

## Case 25: `remote_inventory_tags_digest_mismatch` (cases.json:404–419)

Fixture:
- tags: `{models:[{name:"llama3:8b", model:"llama3:8b", digest:"sha256:1111…1111",
  remote_host:"https://remote.invalid"}]}`
- ps: `{models:[{name:"llama3:8b", model:"llama3:8b", digest:"sha256:2222…2222"}]}`
- `expect:"llama3:8b"`, `expected_exit:1`, `expected_finding:"remote_inventory"`

Classifier path: steps 1–6 are the same as case 24.
- At 243–245 `remote_model` is absent, so `.get` returns `None` and the loop moves on.
  `remote_host` is nonempty, so `_remote_marker` returns `'remote_host'`.
- The result is `remote_inventory`, with reason `selected_tags_entry_remote_host_present`.
  The exit is 1.
- The digest-mismatch branch (259–260, `identity_conflict`) is never reached.

Why this case matters: the digests differ. If the marker check ran after the digest
comparison, the result would be `identity_conflict`, which also exits 1. The exit code would
not change, so only `expected_finding` catches that reordering. `measure.py:304–307` would
report `finding_id 'identity_conflict' != expected 'remote_inventory'`.

## Runner grading for both cases (`measure.py`, line numbers unchanged by the repair)

1. `case_problems` (139–150) passes: `expect` is a str, `expected_exit` is an int (not a
   bool), and `expected_finding` is a str.
2. `measure_case` (220–235) stages the inputs:
   - The case directory is named by index (`"24"`, `"25"`), never by case name.
   - `write_capture` (189–196) writes `json.dumps(..., ensure_ascii=False)`.
   - The child command line passes only the tags path, the ps path, and `--expect` taken
     from `case["expect"]`.
3. The checks at 299–323 pass when the child returns exit 1, `remote_inventory`, the right
   schema, `verdict_exit` 1, `unknown` readiness, and the right scope.

The case `name` is used only as the record label (`case_name`, 131–136).

## Why the new duplicate guard cannot change these two results

- **What changed.** `diff -u frozen/measure-before.py round-14/measure.py` shows exactly one
  edit: lines 358–359,
  `if len(declared) != unique: problems.append("duplicate case names")`.
  Everything else is byte-identical to the frozen snapshot. That includes `measure_case`,
  `write_capture`, `case_name`, and the order of the branches in `run`.
  - The frozen snapshot's sha256 is `fda61e00…`, which matches `frozen/manifest.json` for
    source commit `6e348e2`.
- **The guard's only input is names.** It reads stripped nonempty string `name`s
  (`corpus_problems`, 350–364). It never reads or rewrites tags, ps, expect, or the expected
  values. It also cannot reorder the cases.
- **It accepts this corpus.** jq over `cases.json` gives:
  - 51 cases, 51 nonempty string names, 51 unique raw names, 51 unique stripped names;
  - no names with leading or trailing whitespace;
  - `remote_inventory_tags_loaded_pair` appears once, and so does
    `remote_inventory_tags_digest_mismatch`.

  So the declared count equals the unique count (51 = 51) and 51 ≥ 16. The corpus has no
  problems, the corpus-reject branch (377–380) is skipped, and `elif tool_present` (381–385)
  runs `measure_case` for indexes 24 and 25 exactly as before.
- **When it rejects, it rejects everything.** A rejection replaces every record with
  `unmeasured_record(..., "corpus: …", None)`. It never produces a different
  per-case result or expectation.
- **The classifier cannot see the case name.** Its normal path reads only the `--tags`,
  `--ps` and `--expect` arguments. It reads `cases.json` only under `--selftest` (491–497).
  With the guard passing, the child's inputs for 24 and 25 are the same bytes as before the
  repair.
- **Round-14 receipt** (`.ufo/waves/round-14/acceptance.json`, measured commit `e545ed9`):

  | run | tool | cases 24 and 25 |
  |---|---|---|
  | `final_corpus` | sha `38d1f5d2…` (same as the current classifier) | exit 1, `remote_inventory`, schema/verdict/readiness/scope all match, `passed:true`, `reasons:[]` |
  | `selftest` | current classifier | 1 / `remote_inventory`, passed |
  | `capability_absent` | absent | `unsupported`, `observed_exit:null`; tool-absent branch, which does not depend on names |

  - Every runner record carries `cases_sha256 4a4de0b8…`, which equals the current
    `cases.json`.
  - `git diff --stat e545ed9 6e348e2` over the runner, the classifier and `cases.json` is
    empty.
  - So the repaired runner uses the same per-case code, the same classifier and the same
    inputs as that passing receipt. *[INFERENCE: not re-run by me; L1 owns that.]*

## Contrary evidence and limits

1. **These two cases do not catch the round-14 precedence bug.** In the receipt's
   `precedence_red` run (`frozen/precedence-before.py`, sha `6e1c4ba5…`), both cases passed
   with 1 / `remote_inventory`. The diff explains why. The red tool checked no-tags-match
   before duplicates, and the remote marker before digest presence. Both cases have exactly
   one tags match and nonempty digests, so neither reordering affects them. They only pin
   "remote marker beats a loaded or mismatched pair".
2. **Case 25's exit code is not enough on its own.** `identity_conflict` also exits 1, so
   only the finding ID catches a marker/digest reordering.
3. **Reason tokens are not graded** by `measure.py` or by the selftest. Case 24 carries both
   markers, and `remote_model` wins only because of the field order in `MARKER_FIELDS`. If
   that order changed, the reason token would change and nothing would flag it. The
   finding ID and exit code would stay the same.
4. **Two canonicalization mismatches exist but do not apply here:**
   - The guard strips names, while the selftest guard (359–365) and `case_name` use raw
     names. These two names have no padding.
   - `measure.py` stages captures with `ensure_ascii=False`, the selftest with
     `ensure_ascii=True`. All strings in these cases are ASCII, so the bytes are identical.
5. **Future edits.** If anything ever introduces a duplicate name into `cases.json` (for
   example by merging guard fixtures into it), the whole corpus would be rejected and 24/25
   would go unmeasured. No guard fixture under `tests/ollama-corpus-guard/` mentions these
   names or `cases.json`.
6. **`measure.py` changed during the audit** (`#B6F1` to `#6643`). The conclusion holds for
   both versions.
7. **No `lsp` device was available.** Reading `xd://lsp` returned "No such tool". The branch
   walk is direct source reading. Grep was used only to locate literals and is not offered
   as semantic proof.

I found no evidence against the literal expected IDs or exits.

## Confidence

- **High:** the expected values, the branch each case takes, and that the guard does not
  interfere. This rests on the jq uniqueness counts, the two-line diff, and the matching
  hashes.
- **Runtime outcome under the repaired runner:** inferred from the unchanged code and
  inputs, not observed by me.

Tools installed: none.

Report: .ufo/waves/round-15/build/advice/CaseAudit12.md
