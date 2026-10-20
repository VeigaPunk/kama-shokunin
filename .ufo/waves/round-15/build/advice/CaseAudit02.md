# CaseAudit02 — cases.json indexes 4 and 5 vs the corpus duplicate guard

Seat: `KamaR15.CaseAudit02-3` (scout, leaf, read-only). No code executed, no child process, no network,
no build/test/lint/format, no tool installed or upgraded.

Files read:

- `/home/vgpnk/Projects/shokunin/kama-shokunin/tests/ollama-evidence/cases.json` (indexes 4 and 5; case 0 and the full case-name list for the collision check)
- `/home/vgpnk/Projects/shokunin/kama-shokunin/tools/kama-ollama-evidence.py` (531 lines) — the classifier path
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-14/measure.py` (current 493-line post-GuardRepair state)
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-15/build/spec.json` (GuardRepair and CaseAudit item text)

The `lsp` device is not mounted in this session (no server available), so literal `grep`/`read` was the
fallback. Every claim below is a direct source read, not semantic-server evidence.

## 1. Literal fixture data (observed)

The file is a top-level JSON array (51 objects). Reader query on the file returned
`[length, [.[].name]|length, [.[].name]|unique|length] = [51, 51, 51]`, so all 51 declared names are
distinct; neither audited name repeats anywhere in the corpus.

| idx | name | expect | expected_exit | expected_finding |
|---|---|---|---|---|
| 4 | `loaded_remote_marker_only_on_unselected_ps_entry` (name line 69; object 68-84) | `llama3:8b` | `0` | `loaded_same_digest` |
| 5 | `loaded_shared_digest_alias_copy_active` (name line 86; object 85-101) | `gpt-x:latest` | `0` | `loaded_same_digest` |

Index 4 captures:

- `tags.models` = one entry `{name/model: llama3:8b, digest: sha256:1111…1111}` (no marker)
- `ps.models` = `{qwen3:4b, digest: sha256:2222…2222, remote_host: https://remote.invalid}` (unselected)
  then `{llama3:8b, digest: sha256:1111…1111}` (selected)
- `expect: "llama3:8b"`, `expected_exit: 0`, `expected_finding: "loaded_same_digest"`

Index 5 captures:

- `tags.models` = `{llama3.2:latest, sha256:1111…1111}` and `{gpt-x:latest, sha256:1111…1111}`
- `ps.models` = `{gpt-x:latest, sha256:1111…1111}`
- `expect: "gpt-x:latest"`, `expected_exit: 0`, `expected_finding: "loaded_same_digest"`

Zero-based index 4/5 in the document map to the 5th/6th objects; `run()` enumerates `cases` in document
order and `measure_case` stages each case in `root / f"{index:02d}"` (measure.py:220), so these are the
`04`/`05` temp dirs.

## 2. Exact classifier branches (tools/kama-ollama-evidence.py)

Constants: `FINDING_EXIT` at 91-97, `'loaded_same_digest': 0` at 92. `classify` at 218-264.
`classify_payload` at 267-277 sets `verdict_exit = FINDING_EXIT[finding]`. `_run` emits the payload and
returns `FINDING_EXIT[finding]` at 513-514.

Order in `classify`, with the branch taken for both cases:

1. 220-221 `validate_capture` (172-187): envelope must be an object with a `models` list; each entry an
   object; `name`, `model`, `digest`, `remote_model`, `remote_host` are type-checked only when present.
   Both captures pass (all present values are strings).
2. 223-224 `_matching` (190-192): exact, case-sensitive equality on `name` **or** `model`; no strip, no
   normalization. Index 4: `tags_matches = [llama3:8b]`, `ps_matches = [llama3:8b]` (qwen3:4b is
   filtered out). Index 5: `tags_matches = [gpt-x:latest]`, `ps_matches = [gpt-x:latest]`
   (llama3.2:latest is filtered out).
3. 226-229 duplicate selected entries → `invalid_input` (2). Not hit (1 match each side).
4. 231-232 no tags match → `unknown` (2). Not hit.
5. 234-237 `_identity_conflict` (195-202) on selected tag, then selected ps: name and model both
   non-empty and unequal. Not hit (name == model in both entries of both cases).
6. 238-241 `_digest_present` (213-215) on selected tag, then selected ps. Both non-empty.
7. 243-245 remote marker on the **selected tags** entry (`_remote_marker` 205-211). None in either case.
8. 246-252 remote marker on **`ps_matches[0]` only**. Index 4's `remote_host` sits on the unselected
   qwen3:4b entry, which `_matching` already removed, so the classifier never inspects it. Index 5's
   selected ps entry has no marker.
9. 254-257 no ps match → `available_not_loaded` (1). Not hit.
10. 259-260 digest inequality → `identity_conflict` (1). Not hit: index 4 compares
    `sha256:1111…1111 == sha256:1111…1111`; index 5 compares the same value.
11. 261-264 → `loaded_same_digest`, reasons `['tags_ps_digest_equal', 'metadata_correspondence_not_readiness']`;
    `classify_payload` declares `verdict_exit: 0` and `_run` returns 0.

Index 5 also shows the classifier imposes no digest uniqueness across the tags inventory: two tags
entries share `sha256:1111…1111`, and only the selected tags/ps pair is compared at 259. A global
digest-uniqueness rule would flip this fixture; the code has none.

Harness side (`measure.py` `measure_case`, 211-348) checks: observed exit vs `case["expected_exit"]`
(299-302), parsed `finding_id` vs `case["expected_finding"]` (304-307), `schema` vs
`kama-ollama-evidence/v1` (308), `verdict_exit` vs process exit (312), `readiness` vs `unknown` (316),
`scope` vs `offline-captures-not-runtime` (320). Steps 1-11 plus `classify_payload`/`_run` produce exactly
the literals `0` / `loaded_same_digest`, so both fixtures pass on an unmodified classifier.

## 3. Why the new corpus duplicate guard cannot alter these results

Current guard body (`measure.py:350-364`, post-repair):

- `declared` = stripped `case["name"]` for dict cases whose name is a non-blank string (354-355)
- `unique = len(set(declared))` (356)
- problems: `len(declared) != unique` → `"duplicate case names"` (358-359); `unique < 16` → floor
  message (360-363); returns `(problems, unique)`

Ordering: `run()` calls it at 374; `if corpus:` at 377 builds one `unmeasured_record(..., finding=None)`
per case (379-380) and never calls `measure_case`; only `elif tool_present:` at 381 reaches the child
spawn at 385. The guard is corpus-global and evaluated before any child process.

For the committed corpus: 51 dict cases, 51 non-blank string names, 51 unique after strip, so
`len(declared) == unique == 51` and `unique >= 16` → `corpus == []` → control flows to 381 and indexes
4/5 are measured exactly as before the repair. `unique_case_names` stays 51, `total` stays 51, and no
`error` key is set (421-424).

The guard reads only `case["name"]`; it never reads `expect`, `expected_exit`, `expected_finding`,
`tags`, `ps`, child stdout, or the exit code. Per-case pass/fail is computed solely in `measure_case`
from those literals plus child output. A name-cardinality predicate that is false for this corpus is
therefore observationally inert for indexes 4/5.

The two names are strip-invariant (no leading/trailing whitespace) and differ from each other and from
all 49 other names at their first token; the guard applies no casefold or Unicode normalization, so no
canonicalization can collide them.

## 4. Contrary evidence / risks that would falsify this claim

1. **Wrong key.** Case 0 (`loaded_same_digest`) and case 4 share `expect: "llama3:8b"`,
   `expected_exit: 0`, `expected_finding: "loaded_same_digest"`; case 5 shares the same exit/finding. A
   guard keyed on `expect`, on `(expect, expected_exit, expected_finding)`, or on capture bodies would
   reject the committed corpus and convert every record — including 4/5 — into an unmeasured corpus
   record with `observed_finding: null` and exit 1. The landed guard keys only on stripped `name`, so
   this is currently avoided; it is the single edit that would falsify §3.
2. **Normalization asymmetry.** `case_name` (131-136) returns the raw, unstripped name when
   `name.strip()` is truthy, while the guard compares stripped names. Harmless for 4/5 (no whitespace),
   but a whitespace-padded name would be recorded verbatim yet counted canonically.
3. **Blank / non-string names.** Line 354 excludes them from `declared`, so duplicates among blank names
   are caught only indirectly by the 16-name floor; an all-blank corpus is rejected by the floor, not by
   the duplicate rule. No effect on 4/5.
4. **Mid-audit edit.** `measure.py` changed during this audit (491 → 493 lines). The earlier
   `corpus_problems` body (previous lines 350-362) had only the minimum-unique check, while the module
   docstring (13-14) and `LIMITS` (line 77) already promised duplicate rejection — that mismatch is R1's
   defect. The guard audited above is the current 493-line file; if GuardRepair revises the body again,
   re-anchor on the final lines.
5. **Corpus-global, not per-case.** A duplicate at any index fails the whole run before any child, so
   cases 4/5 would then appear as unmeasured records rather than per-case failures. That is the intended
   fail-closed semantics and does not change their literals.

## 5. Limits

- Static read only. Nothing executed: no classifier, selftest, `measure.py`, corpus-guard `check.py`, or
  child process; no network.
- `lsp` not mounted; literal search is the fallback, so no definition/reference/implementation-server
  evidence exists for these claims.
- Line numbers are from this audit's reads; `measure.py` is an in-flight sibling edit.
- Confidence: high for fixture literals, classifier branch order, `FINDING_EXIT` values, guard body and
  ordering; medium-high for "guard is inert", contingent on the guard staying name-keyed only (risk 1).
